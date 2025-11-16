SpeedCheck - Internet Speed Test Application

A modern full-stack speed test application with real-time testing and history tracking.

 Features

- Real-time speed testing (download/upload)
- Automatic IP and server detection
- Responsive dark UI design

 Tech Stack

Frontend: React, CSS3, Lucide Icons  
Backend: FastAPI, speedtest-cli, SQLite, Uvicorn

 Quick Start

 Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend runs on http://localhost:8000

 Frontend Setup
```bash
cd frontend
npm install
npm start
```
Frontend opens at http://localhost:3000

 Project Structure

```
speedcheck/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.js
│       └── App.css
└── README.md
```

 API Endpoints

- `POST /test` - Run speed test
- `GET /history` - Get test history
- `DELETE /history` - Clear history
- `GET /servers` - List available servers

 Requirements

 Backend
- Python 3.8 or higher
- pip

 Frontend
- Node.js 14 or higher
- npm

 Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/speedcheck.git
cd speedcheck
```

2. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies
```bash
cd frontend
npm install
```

 Running the Application

1. Start the backend server
```bash
cd backend
python main.py
```

2. In a new terminal, start the frontend
```bash
cd frontend
npm start
```

3. Open your browser and navigate to http://localhost:3000

 Troubleshooting

Backend not starting:
```bash
pip install -r requirements.txt
```

Frontend errors:
```bash
npm install
```

CORS issues: Ensure backend is running on port 8000

 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

 License

This project is licensed under the MIT License.

 Author

Your Name - Mihir2207 (https://github.com/Mihir2207)

 Acknowledgments

- speedtest-cli - Speed testing library
- FastAPI - Modern Python web framework
- React - JavaScript library for building user interfaces
- Lucide Icons - Icon library
