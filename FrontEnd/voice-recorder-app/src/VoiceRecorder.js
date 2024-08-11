import React, { useState, useRef } from 'react';
import { ReactMic } from 'react-mic';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faPause, faStop, faMicrophone, faDownload, faSpinner, faKeyboard, faMicrophoneSlash } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import './VoiceRecorder.css'; // Assuming the CSS is in this file

const VoiceRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [processedAudioURL, setProcessedAudioURL] = useState('');
  const [processedText, setProcessedText] = useState(''); // To store the processed text
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [inputMode, setInputMode] = useState('voice'); // "voice" or "text"
  const [textInput, setTextInput] = useState('');
  const audioRef = useRef(null);

  const toggleRecording = () => {
    if (recording) {
      stopRecording();
    } else {
      setProcessedAudioURL(''); // Clear processed audio when starting a new recording
      setProcessedText(''); // Clear processed text when starting a new recording
      startRecording();
    }
  };

  const startRecording = () => {
    setRecording(true);
  };

  const stopRecording = () => {
    setRecording(false);
  };

  const handleTextInputChange = (event) => {
    setTextInput(event.target.value);
  };

  const uploadAudio = async (blob) => {
    setIsLoading(true);
    setProcessedAudioURL(''); // Clear processed audio when submitting new input
    setProcessedText(''); // Clear processed text when submitting new input
    try {
      const formData = new FormData();
      formData.append('file', blob, 'audio.wav');
      const initial_response = await axios.post('http://localhost:8000/chat', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (initial_response) {
        console.log(initial_response)
        console.log("----")
        console.log(initial_response.data)
        const result = initial_response.data;
        
        const response = await axios.get('http://localhost:8000/download', {responseType: 'blob' });
        setIsLoading(false);
        setProcessedText(result);
        const contentType = response.headers['content-type'] || 'audio/mpeg';
        const audioBlob = new Blob([response.data], { type: contentType });
        const url = window.URL.createObjectURL(audioBlob);
        setProcessedAudioURL(url);// Set the processed text for display
        playAudio(url);
       
      }
    } catch (error) {
      console.error('Error processing audio:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const uploadInput = async () => {
    console.log("Sending input")
    setIsLoading(true);
    setProcessedAudioURL(''); // Clear processed audio when submitting new input
    setProcessedText(''); // Clear processed text when submitting new input
    try {
      let response;
      let initial_response
      if (inputMode === 'voice' && audioBlob) {
        console.log("Blob received")
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.wav');
        initial_response = await axios.post('http://localhost:8000/chat', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
         
        });

      } else if (inputMode === 'text' && textInput.trim() !== '') {
        const formData = new FormData();
        formData.append('text', textInput);
        initial_response = await axios.post('http://localhost:8000/chat',formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
         
        });

        
      }
      if (initial_response ) {
        console.log(initial_response)
        console.log("----")
        console.log(initial_response.data)
        const result = initial_response.data;
        
        response = await axios.get('http://localhost:8000/download', {responseType: 'blob' });
        setIsLoading(false);
        setProcessedText(result);
        const contentType = response.headers['content-type'] || 'audio/mpeg';
        const audioBlob = new Blob([response.data], { type: contentType });
        const url = window.URL.createObjectURL(audioBlob);
        setProcessedAudioURL(url);// Set the processed text for display
        playAudio(url);
       
        // Decode the base64 audio and create a Blob
        
      }
    } catch (error) {
      console.error('Error processing input:', error);
      setProcessedText("There was an error processing your request")
    } finally {
      setIsLoading(false);
    }
  };

  

  const playAudio = (url) => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    const audio = new Audio(url);
    audioRef.current = audio;

    audio.play();
    setIsPlaying(true);

    audio.onended = () => {
      setIsPlaying(false);
      window.URL.revokeObjectURL(url);
    };
  };

  const pauseAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const downloadAudio = () => {
    if (processedAudioURL) {
      const link = document.createElement('a');
      link.href = processedAudioURL;
      link.setAttribute('download', 'processed-audio.mp3');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const onStop = (recordedBlob) => {
    console.log('Recorded Blob:', recordedBlob);
  if (recordedBlob && recordedBlob.blob) {
    setAudioBlob(recordedBlob.blob);
    uploadAudio(recordedBlob.blob);
  } else {
    console.error('No audio data captured');
  }
  };

  

  return (
    <div className="recorder-container">
      <div className="input-mode-toggle">
        <button onClick={() => setInputMode('voice')} disabled={inputMode === 'voice'} className="toggle-button">
          <FontAwesomeIcon icon={faMicrophone} size="2x" /> Voice Input
        </button>
        <button onClick={() => setInputMode('text')} disabled={inputMode === 'text'} className="toggle-button">
          <FontAwesomeIcon icon={faKeyboard} size="2x" /> Text Input
        </button>
      </div>
      {inputMode === 'voice' && (
        <div className={`sound-wave ${isLoading ? 'pale' : ''}`}>
          <ReactMic
            record={recording}
            className="sound-wave"
            onStop={onStop}  // Capture the audio data and automatically upload after stopping
            mimeType="audio/wav"
            channelCount={1}
            strokeColor="#000000"
            backgroundColor="#FF4081"
          />
          <div className="controls">
            <button onClick={toggleRecording} className="control-button mic-button" disabled={isLoading}>
              <FontAwesomeIcon icon={recording ? faMicrophoneSlash : faMicrophone} size="4x" />
            </button>
            <p className="recording-text" disabled={isLoading ||  isPlaying} >
              {recording ? 'Click here to stop recording' : 'Click here to start recording'}
            </p>
          </div>
          
        </div>
      )}
      {inputMode === 'text' && (
        <>
          <textarea
            value={textInput}
            onChange={handleTextInputChange}
            placeholder="Type your text here..."
            disabled={isLoading}
            className="text-input"
          />
          <button onClick={uploadInput} disabled={isLoading || textInput.trim() === ''} className="submit-button">
            {isLoading ? <FontAwesomeIcon icon={faSpinner} spin /> : 'Submit'}
          </button>
        </>
      )}
      {isLoading && (
        <div className="loading-icon-container">
          <FontAwesomeIcon icon={faSpinner} spin size="3x" />
          <p>Processing...</p>
        </div>
      )}
      {!isLoading && !recording && processedText && (
         <div className="output-container">
         <p>Key Insights:</p>
         <div className="output-textbox auto-expand">
           {processedText}
         </div>
       </div>
      )}
      {!isLoading && !recording && processedAudioURL && (
        <div className="controls">
          <button onClick={() => playAudio(processedAudioURL)} disabled={isPlaying} className="control-button">
            <FontAwesomeIcon icon={faPlay} size="2x" />
          </button>
          <button onClick={pauseAudio} disabled={!isPlaying} className="control-button">
            <FontAwesomeIcon icon={faPause} size="2x" />
          </button>
          <button onClick={stopAudio} disabled={!isPlaying} className="control-button">
            <FontAwesomeIcon icon={faStop} size="2x" />
          </button>
          <button onClick={downloadAudio} disabled={!processedAudioURL} className="control-button">
            <FontAwesomeIcon icon={faDownload} size="2x" />
          </button>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;
