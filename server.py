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
from gtts import gTTS
import ssl
import paho.mqtt.client as mqtt
from pydub import AudioSegment
from paho.mqtt.client import CallbackAPIVersion
from paho.mqtt.client import MQTTv311  # Asume-se MQTT versão 3.1.1

from llm import send_prompt



commands = ['background', 'eden']

loaded_model = models.load_model("modelo")

#SERVER_IP = "192.168.1.12" # Your id: if windows ipconfig, linux: ifconfig
SERVER_PORT = 12445 # Server port
#ESP32_TCP_SERVER_IP = "192.168.1.15"  # Substitua pelo IP do servidor TCP da ESP32
ESP32_TCP_SERVER_PORT_FOR = 12345  # Substitua pela porta do servidor TCP da ESP32
RECEIVE_DURATION_SECONDS = 1
RECEIVE_DURATION_SECONDS_R = 3
RECEIVE_BUFFER_SIZE = 1024
SEND_BUFFER_SIZE = 2048

wav_file_path = "./reformated2.wav"

MQTT_BROKER = "a34ypir054ngjb-ats.iot.us-east-2.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC = "topic/esp32/pub"
CA_CERTIFICATE = "certs/AmazonRootCA1.pem"
CLIENT_CERTIFICATE = "certs/client.crt"
CLIENT_PRIVATE_KEY = "certs/client.key"

def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} {str(msg.payload)}")

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    if rc == 0:
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}\n")

def mqtt_publish(message, topic):
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)  # Assumindo a utilização do protocolo MQTT v3.1.1

    # Defina sua função on_connect aqui
    client.on_connect = on_connect

    # Configura a conexão TLS
    client.tls_set(ca_certs=CA_CERTIFICATE,
                   certfile=CLIENT_CERTIFICATE,
                   keyfile=CLIENT_PRIVATE_KEY,
                   tls_version=ssl.PROTOCOL_TLSv1_2)

    # Conecta ao broker MQTT
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Inicia um loop em background para gerenciar a conexão
    client.loop_start()

    # Publica a mensagem e captura o resultado em info
    info = client.publish(topic, message)

    # Aguarda a conclusão do envio da mensagem
    info.wait_for_publish()

    # Log do resultado da publicação
    print(f"Message published: MID={info.mid}, Granted QoS={info.rc}")

    # Para a execução do loop e desconecta do broker
    client.loop_stop()
    client.disconnect()


def initialize_mqtt_client():
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)

    # Configure TLS connection
    client.tls_set(ca_certs=CA_CERTIFICATE,
                   certfile=CLIENT_CERTIFICATE,
                   keyfile=CLIENT_PRIVATE_KEY,
                   tls_version=mqtt.ssl.PROTOCOL_TLS)

    # Assign event callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Parse MQTT_BROKER to remove "mqtts://" and extract the host
    mqtt_broker_host = MQTT_BROKER.replace("mqtts://", "").split(":")[0]

    # Connect to MQTT broker
    client.connect(mqtt_broker_host, MQTT_PORT, 60)

    return client


class DiscoverESP32:
    def __init__(self):
        self.esp32_address = None
        self.esp32_port = None  # A porta que a ESP32 usará para se conectar

    def listen_for_esp32(self, listen_port=12340):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('', listen_port))
            server_socket.listen()
            print(f"Listening for ESP32 connection on port {listen_port}...")
            
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print(f"ESP32 connected from {client_address}")
                data = client_socket.recv(1024).decode('utf-8')
                if data == "Hello from ESP32!":
                    self.esp32_address = client_address[0]
                    self.esp32_port = client_address[1]  # Opcional, depende de como você quer usar
                    print(f"ESP32 IP Address: {self.esp32_address}")
                    response_message = "Address get successfully"
                    client_socket.sendall(response_message.encode('utf-8'))
                else:
                    print("Unknown device connected")


def get_local_ip():
    try:
        # Cria um socket DGRAM
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Não é necessário enviar dados, então apenas conecte ao endereço externo
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"Erro ao obter o endereço IP local: {e}")
        ip = "127.0.0.1"  # Fallback para localhost
    return ip

# Use a função para definir SERVER_IP
SERVER_IP = get_local_ip()
print(f"O IP do servidor foi definido para {SERVER_IP}")

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
    if command == 'eden':
        activation_word = b'eden'
        connect_to_esp32_tcp_server(activation_word)
    print("Predicted:", command)

def delete_file(file):
    try:
        os.remove(file)
    except OSError as e:
        print(f"Erro ao excluir o arquivo {file}: {e}")

def connect_to_esp32_tcp_server(activation_word):
    esp32_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        esp32_tcp_socket.connect((ESP32_TCP_SERVER_IP, ESP32_TCP_SERVER_PORT_FOR))
        print('Enviando: ', activation_word)
        esp32_tcp_socket.send(activation_word)  # Enviar um byte representando "eden"
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
        response_handler(texto_transcrito)
        return texto_transcrito
    except sr.UnknownValueError:
        return "Não foi possível transcrever o áudio"
    except sr.RequestError as e:
        return f"Erro na requisição para a API do Google: {e}"

def response_handler(text):
    text_lower = text.lower()

    if text_lower in ['ligar a luminária', 'ligar luminária','ligue a luminária','ligue luminária', 'acender luminária', 'acender luz', 'acender a luiz', 'acender luiz', 'ligar luz', 'acender luz']:
        command = 'on'
        mqtt_publish(command, MQTT_TOPIC)
    elif text_lower in ['desligar a luminária', 'desligar luminária','apagar luminária', 'apagar a luminária', 'desligue a luminária', 'desligue luminária', 'desligar luiz', 'desligar luiz']:
        command = 'off'
        mqtt_publish(command, MQTT_TOPIC)
    elif text_lower in ["tocar musica", "tocar música", "tocar um som", "tocar som"]:
        send_wav_file_over_tcp(wav_file_path, ESP32_TCP_SERVER_IP, ESP32_TCP_SERVER_PORT_FOR)
    elif text_lower in ["ligar luz", "ligar a luz", "ligar luz.", "ligue luz."]:
        command = 'on_light'
        mqtt_publish(command, MQTT_TOPIC)
    elif text_lower in ["desligar luz", "desligar a luz", "desligar luz.", "desligue luz."]:
        command = 'off_light'
        mqtt_publish(command, MQTT_TOPIC)
    else:
        filepath = send_prompt(text)
        send_wav_file_over_tcp(filepath, ESP32_TCP_SERVER_IP, ESP32_TCP_SERVER_PORT_FOR)


def text_to_speech_wav(text, lang='pt-br'):
    # Cria um objeto gTTS
    tts = gTTS(text=text, lang=lang, slow=False)
    
    # Gera um arquivo temporário mp3
    temp_mp3 = "temp.mp3"
    tts.save(temp_mp3)
    
    # Converte o arquivo mp3 para wav
    audio = AudioSegment.from_mp3(temp_mp3)
    audio_file_wav = "speech.wav"
    audio.export(audio_file_wav, format="wav")
    
    # Remove o arquivo temporário mp3
    os.remove(temp_mp3)
    
    print(f"Arquivo '{audio_file_wav}' salvo com sucesso.")

# Exemplo de uso



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



def send_wav_file_over_tcp(wav_file_path, server_ip, server_port):
    """
    Envia um arquivo WAV para o servidor especificado através de TCP.

    :param wav_file_path: O caminho para o arquivo WAV a ser enviado.
    :param server_ip: O endereço IP do servidor TCP (ESP32).
    :param server_port: A porta TCP no servidor para a qual nos conectaremos.
    """
    # Criar um socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Conectar ao servidor
        sock.connect((server_ip, server_port))
        print(f"Conectado a {server_ip}:{server_port}")

        # Abrir o arquivo WAV e enviar seus bytes
        with open(wav_file_path, 'rb') as wav_file:
            data = wav_file.read(SEND_BUFFER_SIZE)  # Ler 1024 bytes por vez
            while data:
                sock.send(data)
                data = wav_file.read(SEND_BUFFER_SIZE)
        print("Arquivo WAV enviado com sucesso.")
    except Exception as e:
        print(f"Erro ao enviar arquivo WAV: {e}")
    finally:
        # Fechar o socket
        sock.close()

if __name__ == "__main__":
    SERVER_IP = get_local_ip()
    print(f"O IP do servidor foi definido para {SERVER_IP}")

    # Inicializa o descobridor da ESP32 e começa a ouvir a tentativa de conexão
    esp32_discoverer = DiscoverESP32()
    esp32_discoverer.listen_for_esp32()

    # Agora você tem o IP da ESP32 disponível como esp32_discoverer.esp32_address
    global ESP32_TCP_SERVER_IP, ESP32_TCP_SERVER_PORT
    ESP32_TCP_SERVER_IP = esp32_discoverer.esp32_address
    ESP32_TCP_SERVER_PORT = esp32_discoverer.esp32_port
    client = initialize_mqtt_client()
    client.loop_start()

    tcp_thread = threading.Thread(target=receive_audio_data_tcp)
    tcp_thread.start()

    receive_audio_data()

    tcp_thread.join()
    mqtt_publish("Hello MQTT!")