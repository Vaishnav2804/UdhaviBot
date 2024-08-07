import json


import pyaudio
import wave
import time
from pynput import keyboard

# Configuration dictionary for pyaudio settings
pyconf = {"frames_per_buffer":1024, "rate":48000, "channels":1}


def on_press():
    return False  # Stop listener on any key press


def record_audio():
    pyaudio_format = pyaudio.paInt16  # Changed to paInt16 for better compatibility

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio_format, channels=pyconf["channels"], rate=pyconf["rate"], input=True,
                    frames_per_buffer=pyconf["frames_per_buffer"])

    print("Ask your question. Press any key to stop.")

    frames = []
    timeout = time.time() + 20  # 20 seconds timeout

    while listener.running:
        data = stream.read(pyconf["frames_per_buffer"])
        frames.append(data)
        if time.time() > timeout:
            break

    print("Stopped")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open("output.wav", 'wb')
    wf.setnchannels(pyconf["channels"])
    wf.setsampwidth(p.get_sample_size(pyaudio_format))
    wf.setframerate(pyconf["rate"])
    wf.writeframes(b''.join(frames))
    wf.close()
    print("Recording Saved")



def ask_question_to_llm(context):
    context_dict = json.loads(context)
    genai.configure(api_key=key)
    model = genai.GenerativeModel(model_name="gemini-pro")
    questionprompt = f'Respond to the user with an informative answer in {context_dict["language"]}'
    response = model.generate_content([questionprompt, context_dict["text"]])
    return response.text


if __name__ == "__main__":
    record_audio()
    context = speech_to_text()
    print("THE QUESTION WAS\n")
    print(context)
    print("\n\nTHE ANSWER IS \n")
    print(ask_question_to_llm(context))
