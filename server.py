import socket
import wave
import time
import numpy as np
from tensorflow.keras import models
from recording_helper import *
from tf_helper import *
import random
import string
import os
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import speech_recognition as sr
import threading

commands = ['background', 'eden']

loaded_model = models.load_model("./saved")

SERVER_IP = "192.168.1.3"
SERVER_PORT = 12445
ESP32_TCP_SERVER_IP = "192.168.1.6"  # Substitua pelo IP do servidor TCP da ESP32
ESP32_TCP_SERVER_PORT = 12345  # Substitua pela porta do servidor TCP da ESP32
RECEIVE_DURATION_SECONDS = 1
RECEIVE_DURATION_SECONDS_R = 3
RECEIVE_BUFFER_SIZE = 1024

def receive_audio_data():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))

    print(f"Aguardando conexões em {SERVER_IP}:{SERVER_PORT}...")

    with ThreadPoolExecutor(max_workers=5) as executor:  # Ajuste o número de workers conforme necessário
        while True:
            string_aleatoria = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            wav_file = string_aleatoria + ".wav"
            received_data = bytearray()
            start_time = time.time()

            try:
                while time.time() - start_time < RECEIVE_DURATION_SECONDS:
                    data, _ = server_socket.recvfrom(RECEIVE_BUFFER_SIZE)
                    received_data.extend(data)
            except Exception as e:
                print(f"Erro durante a recepção dos dados: {e}")

            if received_data:
                # Utilizando ThreadPoolExecutor para realizar o salvamento, predição e exclusão
                executor.submit(save_predict_delete, received_data, wav_file)

    server_socket.close()

def save_predict_delete(data, filename):
    save_audio_data_to_wav(data, filename)
    predict_mic(filename)
    delete_file(filename)

def save_audio_data_to_wav(data, filename):
    try:
        with wave.open(filename, 'wb') as audio_file:
            audio_file.setnchannels(1)  # Mono
            audio_file.setsampwidth(2)   # 16 bits
            audio_file.setframerate(16000)  # Exemplo de taxa de amostragem
            audio_file.writeframes(data)
    except Exception as e:
        print(f"Erro ao salvar os dados de áudio como WAV: {e}")

def predict_mic(file):
    audio = record_audio_from_file(file)
    spec = preprocess_audiobuffer(audio)
    prediction = loaded_model(spec)
    label_pred = np.argmax(prediction, axis=1)
    command = commands[label_pred[0]]
    if command == 'eden':  # Adicione esta função para verificar se o comando predito é "eden"
        connect_to_esp32_tcp_server()
    print("Predicted:", command)

def delete_file(file):
    try:
        os.remove(file)
    except OSError as e:
        print(f"Erro ao excluir o arquivo {file}: {e}")

def connect_to_esp32_tcp_server():
    esp32_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        esp32_tcp_socket.connect((ESP32_TCP_SERVER_IP, ESP32_TCP_SERVER_PORT))
        esp32_tcp_socket.send(b'eden')  # Enviar um byte representando "eden"
        esp32_tcp_socket.close()
    except Exception as e:
        print(f"Erro ao conectar e enviar dados para o servidor TCP da ESP32: {e}")

def save_predict_delete1(data, filename):
    save_audio_data_to_wav(data, filename)
    transcricao = transcrever_audio(filename)
    print(transcricao)
    delete_file(filename)

def transcrever_audio(arquivo_wav):
    recognizer = sr.Recognizer()

    with sr.AudioFile(arquivo_wav) as source:
        audio = recognizer.record(source)

    try:
        texto_transcrito = recognizer.recognize_google(audio, language='pt-br')
        return texto_transcrito
    except sr.UnknownValueError:
        return "Não foi possível transcrever o áudio"
    except sr.RequestError as e:
        return f"Erro na requisição para a API do Google: {e}"

def receive_audio_data_tcp():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT + 1))
    server_socket.listen(5)

    print(f"Aguardando conexões em {SERVER_IP}:{SERVER_PORT + 1}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Conexão recebida de {addr}")

        string_aleatoria = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        wav_file = string_aleatoria + ".wav"
        received_data = bytearray()
        start_time = time.time()

        try:
            while time.time() - start_time < RECEIVE_DURATION_SECONDS_R:
                data = client_socket.recv(RECEIVE_BUFFER_SIZE)
                if not data:
                    break
                received_data.extend(data)
        except Exception as e:
            print(f"Erro durante a recepção dos dados: {e}")

        if received_data:
            save_predict_delete1(received_data, wav_file)

        client_socket.close()

    server_socket.close()
if __name__ == "__main__":

    tcp_thread = threading.Thread(target=receive_audio_data_tcp)
    tcp_thread.start()

    receive_audio_data()

    tcp_thread.join()