import google.generativeai as genai
import json


def speech_to_text() -> dict:
    genai.configure()

    audio_file = genai.upload_file(path='output.wav')
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    speech_to_text_prompt = """Convert the speech of the following audio file into english text. 
    Strictly Give the output in a json format:
    language:"Original audio language",text :"Proper english translated text such that an englishman can understand."
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
        print("Error while converting to dictionary"+e.__str__())
        raise e
    return response_dict
