from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import openai
from dotenv import load_dotenv
from google.cloud import texttospeech
import json
from datetime import datetime

load_dotenv()

# Load your API key from an environment variable or secret management service
openai.api_key = os.environ["OPENAI_API_KEY"]

class HomeView(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, "index.html")

class MeditationScriptView(APIView):
    def post(self, request, *args, **kwargs):
        # assign current data to a variable
        date = datetime.today()
        body = request.body.decode("utf-8")
        data = json.loads(body)
        input_text = data["input"]

        script = self.generateScript(input_text)
        audio = self.generateVoice(date, script)

        result = {
            "script": script,
            "audio": audio
        }

        return Response(data=result, status=status.HTTP_200_OK)

    def generateScript(self, input_text):
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": input_text}]
        )
        script = chat_completion.choices[0]["message"]["content"]

        return script

    def generateVoice(self, date, script):
        with open("./mindfuldev/assets/script_{}.ssml".format(date), "w") as f:
            f.write(script)

        script = texttospeech.SynthesisInput(ssml=script)
        client = texttospeech.TextToSpeechClient(
            client_options={"api_key": os.environ["GOOGLE_API_KEY"]}
        )

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=script, voice=voice, audio_config=audio_config
        )
        return response.audio_content
    
        # The response's audio_content is binary.
        # with open("output{}.mp3".format(date), "wb") as out:
        #     out.write(response.audio_content)
        #     print('Audio content written to file "output.mp3"')