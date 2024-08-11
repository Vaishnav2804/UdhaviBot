import React from 'react';
import './LoadingScreen.css';

const LoadingScreen = () => {
  return (
    <div className="loading-screen">
      <div className="loading-spinner"></div>
      <h2 className="loading-text">Processing your audio...</h2>
    </div>
  );
};

export default LoadingScreen;
