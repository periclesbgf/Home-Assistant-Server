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

commands = ['_background_noise_', 'background', 'eden', 'marvin', 'off', 'on']

loaded_model = models.load_model("./saved")

SERVER_IP = "192.168.1.3"
SERVER_PORT = 12445
RECEIVE_DURATION_SECONDS = 1

def receive_audio_data():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(1)

    print(f"Aguardando conexão em {SERVER_IP}:{SERVER_PORT}...")
    client_socket, client_address = server_socket.accept()
    print(f"Conexão estabelecida com {client_address}")

    while True:
        string_aleatoria = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        wav_file = string_aleatoria + ".wav"
        received_data = bytearray()
        start_time = time.time()

        try:
            while time.time() - start_time < RECEIVE_DURATION_SECONDS:
                data = client_socket.recv(1024)
                if not data:
                    break
                received_data.extend(data)
        except Exception as e:
            print(f"Erro durante a recepção dos dados: {e}")

        if received_data:
            save_audio_data_to_wav(received_data, wav_file)
            predict_mic(wav_file)
            delete_file(wav_file)

    client_socket.close()
    server_socket.close()

    return received_data

def save_audio_data_to_wav(data, filename):
    try:
        with wave.open(filename, 'wb') as audio_file:
            audio_file.setnchannels(1)  # Mono
            audio_file.setsampwidth(2)   # 16 bits
            audio_file.setframerate(16000)  # Exemplo de taxa de amostragem
            audio_file.writeframes(data)
    except Exception as e:
        print(f"Erro ao salvar os dados de áudio como WAV: {e}")

def print_received_data(data):
    # Aqui, você pode processar ou imprimir os dados recebidos conforme necessário
    print("Dados recebidos:")
    print(data)

def main():
    receive_audio_data()
    #print_received_data(received_data)

def predict_mic(file):
    audio = record_audio_from_file(file)
    spec = preprocess_audiobuffer(audio)
    prediction = loaded_model(spec)
    label_pred = np.argmax(prediction, axis=1)
    command = commands[label_pred[0]]
    print("Predicted:", command)

def delete_file(file):
    try:
        os.remove(file)
    except OSError as e:
        print(f"Erro ao excluir o arquivo {file}: {e}")

if __name__ == "__main__":
    main()
