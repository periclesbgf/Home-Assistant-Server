import speech_recognition as sr
from gtts import gTTS
import os
import playsound
import pyjokes
import wikipedia
import pyaudio
import webbrowser
import pygame

#get mic audio
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('entrei')
        r.pause_threshold = 1
        # wait for a second to let the recognizer adjust the
        # energy threshold based on the surrounding noise level
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        said = ""
        try:
            said = r.recognize_google(audio, language='pt-br')
            print(said)
        except sr.UnknownValueError:
            speak("Desculpe, eu não entendi.")
        except sr.RequestError:
            speak("Desculpe, o serviço não está disponível.")
        print('sai')
    return said.lower()

#speak converted audio to text
pygame.mixer.init()

# função para falar o texto convertido em áudio
def speak(text):
    tts = gTTS(text=text, lang='pt')
    filename = "voice.mp3"
    
    try:
        os.remove(filename)
    except OSError:
        pass
    
    tts.save(filename)
    
    # usar o mixer do pygame para reproduzir o som
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    # aguardar o som terminar de ser reproduzido
    while pygame.mixer.music.get_busy():
        continue

#function to respond to commands
def respond(text):
    print("Text from get audio: " + text)

#let's try it
while True:
    print("I am listening...")
    text = get_audio()
    respond(text)
