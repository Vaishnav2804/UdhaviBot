import google.generativeai as genai
import json
from pydub import AudioSegment
from pydub.playback import play
from google.cloud import texttospeech


def speech_to_text() -> dict:
    genai.configure()

    audio_file = genai.upload_file(path='output.wav')
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    speech_to_text_prompt = """Convert the speech of the following audio file into english text. Give the output in a json format:
    language:"Original audio language", text :"Proper english translation of the question such that an englishman can understand, language_code: Google Text to Speech language code of the original language that the question was asked in" 
    """
    response = model.generate_content([speech_to_text_prompt, audio_file])
    response = response.text
    response_list = response.splitlines()
    response_list.pop(0)
    response_list.pop(-1)
    response = "\n".join(response_list)
    try:
        response_dict = json.loads(response)
    except Exception as e:
        print("Error while converting to dictionary" + e.__str__())
        raise e
    return response_dict


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

    song = AudioSegment.from_mp3("output.mp3")
    play(song)
