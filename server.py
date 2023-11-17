import socket
import wave
import time


SERVER_IP = "192.168.1.3"
SERVER_PORT = 12445
RECEIVE_DURATION_SECONDS = 3

def receive_audio_data():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(1)

    print(f"Aguardando conexão em {SERVER_IP}:{SERVER_PORT}...")
    client_socket, client_address = server_socket.accept()
    print(f"Conexão estabelecida com {client_address}")

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
    finally:
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
        print(f"Dados de áudio recebidos e salvos como '{filename}'.")
    except Exception as e:
        print(f"Erro ao salvar os dados de áudio como WAV: {e}")

def print_received_data(data):
    # Aqui, você pode processar ou imprimir os dados recebidos conforme necessário
    print("Dados recebidos:")
    print(data)

def main():
    received_data = receive_audio_data()
    print_received_data(received_data)
    # Salvar dados como um arquivo WAV
    save_audio_data_to_wav(received_data, "audio_received11.wav")


if __name__ == "__main__":
    main()
