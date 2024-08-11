import React, { useState, useRef } from 'react';
import { ReactMic } from 'react-mic';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlay, faPause, faStop, faMicrophone, faDownload, faTrash, faSpinner } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';

const VoiceRecorder = () => {
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [processedAudioURL, setProcessedAudioURL] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [inputMode, setInputMode] = useState('voice'); // "voice" or "text"
  const [textInput, setTextInput] = useState('');
  const audioRef = useRef(null);

  const toggleRecording = () => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const startRecording = () => {
    setRecording(true);
  };

  const stopRecording = () => {
    setRecording(false);
  };

  const abandonRecording = () => {
    setRecording(false);
    setAudioBlob(null);
    setProcessedAudioURL('');
    setIsLoading(false);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  };

  const handleTextInputChange = (event) => {
    setTextInput(event.target.value);
  };

  const uploadInput = async () => {
    setIsLoading(true);
    try {
      if (inputMode === 'voice' && audioBlob) {
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.wav');
        const response = await axios.post('http://localhost:8000/process-audio/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          responseType: 'blob',
        });

        const contentType = response.headers['content-type'] || 'audio/mpeg';
        const url = window.URL.createObjectURL(new Blob([response.data], { type: contentType }));
        setProcessedAudioURL(url);
        playAudio(url);

      } else if (inputMode === 'text' && textInput.trim() !== '') {
        const response = await axios.post('http://localhost:8000/process-text/', { text: textInput });
        const contentType = response.headers['content-type'] || 'audio/mpeg';
        const url = window.URL.createObjectURL(new Blob([response.data], { type: contentType }));
        setProcessedAudioURL(url);
        playAudio(url);
      }
    } catch (error) {
      console.error('Error processing input:', error);
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

  const onStop = (recordedBlob) => {
    setAudioBlob(recordedBlob.blob);
  };

  return (
    <div className="recorder-container">
      <div className="input-mode-toggle">
        <button onClick={() => setInputMode('voice')} disabled={inputMode === 'voice'}>
          Voice Input
        </button>
        <button onClick={() => setInputMode('text')} disabled={inputMode === 'text'}>
          Text Input
        </button>
      </div>
      {inputMode === 'voice' && (
        <div className={`sound-wave ${isLoading ? 'pale' : ''}`}>
          <ReactMic
            record={recording}
            className="sound-wave"
            onStop={onStop}  // Capture the audio data when recording stops
            mimeType="audio/wav"
            channelCount={1}
            strokeColor="#000000"
            backgroundColor="#FF4081"
          />
          <div className="controls">
            <button onClick={toggleRecording} className="control-button mic-button" disabled={isLoading}>
              <FontAwesomeIcon icon={recording ? faMicrophoneSlash : faMicrophone} size="4x" />
            </button>
          </div>
        </div>
      )}
      {inputMode === 'text' && (
        <textarea
          value={textInput}
          onChange={handleTextInputChange}
          placeholder="Type your text here..."
          disabled={isLoading}
        />
      )}
      <button onClick={uploadInput} disabled={isLoading || (inputMode === 'voice' && !audioBlob)}>
        {isLoading ? <FontAwesomeIcon icon={faSpinner} spin /> : 'Submit'}
      </button>
      {isLoading && (
        <div className="loading-icon-container">
          <FontAwesomeIcon icon={faSpinner} spin size="3x" />
          <p>Processing...</p>
        </div>
      )}
      {processedAudioURL && (
        <div className="controls">
          <button onClick={() => playAudio(processedAudioURL)} disabled={isPlaying} className="control-button">
            <FontAwesomeIcon icon={faPlay} size="2x" />
          </button>
          <button onClick={() => pauseAudio()} disabled={!isPlaying} className="control-button">
            <FontAwesomeIcon icon={faPause} size="2x" />
          </button>
          <button onClick={() => stopAudio()} disabled={!isPlaying} className="control-button">
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
