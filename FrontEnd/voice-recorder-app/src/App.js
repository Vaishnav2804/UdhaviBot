// src/App.js
import React from 'react';
import VoiceRecorder from './VoiceRecorder';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Government Scheme Search App</h1>
        <VoiceRecorder />
      </header>
    </div>
  );
}

export default App;