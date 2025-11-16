"""
Internet Speed Test Backend API
Built with FastAPI and speedtest-cli
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import speedtest
import time
from datetime import datetime
import sqlite3
from contextlib import contextmanager

app = FastAPI(title="Speed Test API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
@contextmanager
def get_db():
    conn = sqlite3.connect('speedtest.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS test_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                download_speed REAL NOT NULL,
                upload_speed REAL NOT NULL,
                ping REAL NOT NULL,
                jitter REAL,
                server_name TEXT,
                server_country TEXT,
                server_host TEXT,
                isp TEXT
            )
        ''')
        conn.commit()

init_db()

# Pydantic models
class SpeedTestResult(BaseModel):
    timestamp: str
    download_speed: float
    upload_speed: float
    ping: float
    jitter: Optional[float] = None
    server_name: Optional[str] = None
    server_country: Optional[str] = None
    server_host: Optional[str] = None
    isp: Optional[str] = None

class TestHistoryResponse(BaseModel):
    tests: List[SpeedTestResult]
    total: int

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Speed Test API",
        "version": "1.0.0",
        "endpoints": {
            "/test": "Run speed test",
            "/history": "Get test history",
            "/servers": "Get available servers"
        }
    }

@app.post("/test", response_model=SpeedTestResult)
async def run_speed_test():
    """
    Run a complete speed test and return results
    """
    try:
        print("Starting speed test...")
        st = speedtest.Speedtest()
        
        print("Getting best server...")
        # Get best server
        st.get_best_server()
        
        # Get server info
        server = st.results.server
        server_name = f"{server.get('name', 'Unknown')}, {server.get('country', 'Unknown')}"
        server_country = server.get('country', 'Unknown')
        server_host = server.get('host', 'Unknown')
        
        print(f"Server selected: {server_name}")
        
        print("Testing download speed...")
        # Run download test
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        print(f"Download: {download_speed} Mbps")
        
        print("Testing upload speed...")
        # Run upload test  
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        print(f"Upload: {upload_speed} Mbps")
        
        # Get ping
        ping = st.results.ping
        print(f"Ping: {ping} ms")
        
        # Calculate jitter (simplified)
        try:
            jitter = abs(ping - server.get('latency', ping))
        except:
            jitter = 0.0
        
        # Get ISP
        try:
            isp = st.results.client.get('isp', 'Unknown')
        except:
            isp = 'Unknown'
        
        # Create result
        result = SpeedTestResult(
            timestamp=datetime.now().isoformat(),
            download_speed=round(download_speed, 2),
            upload_speed=round(upload_speed, 2),
            ping=round(ping, 2),
            jitter=round(jitter, 2),
            server_name=server_name,
            server_country=server_country,
            server_host=server_host,
            isp=isp
        )
        
        print("Saving to database...")
        # Save to database
        with get_db() as conn:
            conn.execute('''
                INSERT INTO test_history 
                (timestamp, download_speed, upload_speed, ping, jitter, 
                 server_name, server_country, server_host, isp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.timestamp,
                result.download_speed,
                result.upload_speed,
                result.ping,
                result.jitter,
                result.server_name,
                result.server_country,
                result.server_host,
                result.isp
            ))
            conn.commit()
        
        print("Speed test completed successfully!")
        return result
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Speed test failed: {str(e)}")

@app.get("/history", response_model=TestHistoryResponse)
async def get_test_history(limit: int = 10, offset: int = 0):
    """
    Get speed test history
    """
    try:
        with get_db() as conn:
            # Get total count
            total = conn.execute('SELECT COUNT(*) FROM test_history').fetchone()[0]
            
            # Get tests
            cursor = conn.execute('''
                SELECT * FROM test_history 
                ORDER BY id DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            tests = []
            for row in cursor:
                tests.append(SpeedTestResult(
                    timestamp=row['timestamp'],
                    download_speed=row['download_speed'],
                    upload_speed=row['upload_speed'],
                    ping=row['ping'],
                    jitter=row['jitter'],
                    server_name=row['server_name'],
                    server_country=row['server_country'],
                    server_host=row['server_host'],
                    isp=row['isp']
                ))
            
            return TestHistoryResponse(tests=tests, total=total)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@app.delete("/history")
async def clear_history():
    """
    Clear all test history
    """
    try:
        with get_db() as conn:
            conn.execute('DELETE FROM test_history')
            conn.commit()
        return {"message": "History cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")

@app.get("/servers")
async def get_servers():
    """
    Get list of available speedtest servers
    """
    try:
        st = speedtest.Speedtest()
        servers = st.get_servers()
        
        server_list = []
        for server_group in servers.values():
            for server in server_group:
                server_list.append({
                    "id": server['id'],
                    "name": server['name'],
                    "country": server['country'],
                    "host": server['host'],
                    "distance": round(server['d'], 2)
                })
        
        # Sort by distance
        server_list.sort(key=lambda x: x['distance'])
        
        return {"servers": server_list[:20]}  # Return top 20 closest servers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch servers: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)