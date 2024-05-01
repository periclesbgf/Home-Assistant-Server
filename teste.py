import speech_recognition as sr
import wave
import string
import os

arquivo_wav = "/Users/peric/projects/Home-Assistant-Server/musica.wav"

def transcrever_audio(arquivo_wav):
    recognizer = sr.Recognizer()

    with sr.AudioFile(arquivo_wav) as source:
        audio = recognizer.record(source)

    try:
        texto_transcrito = recognizer.recognize_google(audio, language='pt-br')
        print(texto_transcrito)
        return texto_transcrito
    except sr.UnknownValueError:
        return "Não foi possível transcrever o áudio"
    except sr.RequestError as e:
        return f"Erro na requisição para a API do Google: {e}"
    
transcrever_audio(arquivo_wav)