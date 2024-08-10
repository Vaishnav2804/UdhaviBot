import google.generativeai as genai
import json
from pydub import AudioSegment
from pydub.playback import play
from google.cloud import texttospeech


def speech_to_text() -> str:
    genai.configure()

    audio_file = genai.upload_file(path='output.wav')
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    speech_to_text_prompt = """Use the audio for the following and provide a JSON response with the following keys:
            * language: The language of the input text.
            * text: A proper English translation understandable by a native English speaker.
            * language_code: The equivalent Google Cloud Platform language code for text-to-speech. 
    """
    response = model.generate_content([speech_to_text_prompt, audio_file])
    response = response.text
    return response


def tts(message, language):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=message)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')

    # song = AudioSegment.from_mp3("output.mp3")
    # play(song)
