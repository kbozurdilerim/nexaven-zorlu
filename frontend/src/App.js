import React from 'react';
import './App.css';

function App() {
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:3001/api';

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 ZorluForce</h1>
        <p>Professional Automotive ECU Management System</p>
        <div className="status">
          <p>Backend URL: <code>{backendUrl}</code></p>
          <p>Frontend is ready to serve your ECU management needs</p>
        </div>
        <div className="features">
          <h2>Features:</h2>
          <ul>
            <li>✅ ECU File Management</li>
            <li>🤖 AI-Powered Analysis</li>
            <li>⚡ Advanced Tuning</li>
            <li>📊 Performance Monitoring</li>
            <li>👥 Multi-User Support</li>
            <li>💰 Billing System</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;