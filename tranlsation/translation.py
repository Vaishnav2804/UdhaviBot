import pyaudio
import wave
from pynput import keyboard
import time
from config import pyaudio_configs as pyconf
from config import gemini_api_key as key
import google.generativeai as genai
import json


def on_press(keys):
    return False  # returning false stops the listener


def record_audio():
    format = pyaudio.paInt24

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    p = pyaudio.PyAudio()

    stream = p.open(format=format, channels=pyconf["channels"], rate=pyconf["rate"], input=True,
                    frames_per_buffer=pyconf["frames_per_buffer"])

    print("Ask your question. Press any key to stop.")

    frames = []
    timeout = time.time() + 20

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
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(pyconf["rate"])
    wf.writeframes(b''.join(frames))
    wf.close()
    print("Recording Saved")


def speech_to_text():
    genai.configure(api_key=key)
    audio_file = genai.upload_file(path='output.wav')
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    sttprompt = """Convert the speech of the following audio file into english text. Give the output in a json format:
    language:"Original audio language" and text :"Proper english translate text such that an englishman can understand" 
    """
    response = model.generate_content([sttprompt, audio_file])
    response = response.text
    response_list = response.splitlines()
    response_list.pop(0)
    response_list.pop(-1)
    response = "\n".join(response_list)
    return response


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
