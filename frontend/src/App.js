import React, { useState, useEffect } from 'react';
import { Download, Upload, Globe, Server, Clock } from 'lucide-react';
import './App.css';

function App() {
  const [testing, setTesting] = useState(false);
  const [currentSpeed, setCurrentSpeed] = useState(0);
  const [downloadSpeed, setDownloadSpeed] = useState(0);
  const [uploadSpeed, setUploadSpeed] = useState(0);
  const [userIP, setUserIP] = useState('...');
  const [server, setServer] = useState('...');
  const [statusMessage, setStatusMessage] = useState('');
  const [testHistory, setTestHistory] = useState([]);

  useEffect(() => {
    // Get user IP
    fetch('https://api.ipify.org?format=json')
      .then(res => res.json())
      .then(data => setUserIP(data.ip))
      .catch(() => setUserIP('Unable to fetch'));
    
    // Load test history
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const result = await window.storage.get('speedtest-history');
      if (result) {
        setTestHistory(JSON.parse(result.value));
      }
    } catch (error) {
      console.log('No history found');
    }
  };

  const saveToHistory = (testData) => {
    const newEntry = {
      date: new Date().toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      }),
      download: testData.download_speed,
      upload: testData.upload_speed,
      server: testData.server_name
    };

    const newHistory = [newEntry, ...testHistory].slice(0, 10); // Keep last 10 tests
    setTestHistory(newHistory);
    window.storage.set('speedtest-history', JSON.stringify(newHistory));
  };

  const runSpeedTest = async () => {
    setTesting(true);
    setCurrentSpeed(0);
    setDownloadSpeed(0);
    setUploadSpeed(0);
    setStatusMessage('Initializing...');

    try {
      // Initial animation while connecting
      for (let i = 0; i <= 50; i += 5) {
        setCurrentSpeed(i);
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      setStatusMessage('Running speed test... (This may take 30-60 seconds)');
      console.log('Calling backend...');
      
      // Call Python backend with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout

      const response = await fetch('http://localhost:8000/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.text();
        console.error('Backend error:', errorData);
        throw new Error(`Speed test failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('Backend response:', data);
      
      setServer(data.server_name || 'Unknown');
      setStatusMessage('Processing results...');

      // Animate download speed
      const downloadSteps = 50;
      const downloadIncrement = data.download_speed / downloadSteps;
      
      for (let i = 0; i <= downloadSteps; i++) {
        const speed = Math.min(i * downloadIncrement, data.download_speed);
        setCurrentSpeed(speed);
        await new Promise(resolve => setTimeout(resolve, 40));
      }
      
      setDownloadSpeed(data.download_speed);

      // Animate upload speed
      const uploadSteps = 50;
      const uploadIncrement = data.upload_speed / uploadSteps;
      
      for (let i = 0; i <= uploadSteps; i++) {
        const speed = Math.min(i * uploadIncrement, data.upload_speed);
        setCurrentSpeed(speed);
        await new Promise(resolve => setTimeout(resolve, 40));
      }
      
      setUploadSpeed(data.upload_speed);
      setCurrentSpeed(data.download_speed);
      setStatusMessage('Test complete!');
      
      setTimeout(() => setStatusMessage(''), 2000);

    } catch (error) {
      console.error('Speed test error:', error);
      
      if (error.name === 'AbortError') {
        alert('Speed test timed out. The test is taking longer than expected. Please try again.');
      } else if (error.message.includes('Failed to fetch')) {
        alert('Cannot connect to backend. Make sure the Python server is running on http://localhost:8000');
      } else {
        alert(`Failed to run speed test: ${error.message}\n\nCheck the browser console and backend terminal for details.`);
      }
      
      setCurrentSpeed(0);
      setStatusMessage('');
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <div className="logo">
          <div className="logo-icon">⚡</div>
          <h1>SpeedCheck</h1>
        </div>
      </div>

      <div className="container">
        {/* Main Speed Display */}
        <div className="speed-display">
          <div className="speed-value">{currentSpeed.toFixed(2)}</div>
          <div className="speed-label">Mbps</div>
          
          {statusMessage && <div className="status-message">{statusMessage}</div>}
          
          <button 
            className={`start-button ${testing ? 'testing' : ''}`}
            onClick={runSpeedTest}
            disabled={testing}
          >
            {testing ? 'Testing...' : 'Start'}
          </button>
        </div>

        {/* Download and Upload Cards */}
        <div className="results-grid">
          <div className="result-card">
            <div className="result-header">
              <Download className="result-icon" />
              <span>Download</span>
            </div>
            <div className="result-value">
              {downloadSpeed > 0 ? downloadSpeed.toFixed(2) : '--'}
            </div>
            <div className="result-unit">Mbps</div>
          </div>

          <div className="result-card">
            <div className="result-header">
              <Upload className="result-icon" />
              <span>Upload</span>
            </div>
            <div className="result-value">
              {uploadSpeed > 0 ? uploadSpeed.toFixed(2) : '--'}
            </div>
            <div className="result-unit">Mbps</div>
          </div>
        </div>

        {/* Info Bar */}
        <div className="info-bar">
          <div className="info-item">
            <Globe className="info-icon" />
            <span>Your IP: {userIP}</span>
          </div>
          <div className="info-item">
            <Server className="info-icon" />
            <span>Server: {server}</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        <a href="#about">About</a>
        <a href="#privacy">Privacy Policy</a>
        <a href="#contact">Contact</a>
      </div>
    </div>
  );
}

export default App;