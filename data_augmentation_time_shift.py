import os
import librosa
import soundfile as sf
import random
import string

def time_shift(audio, sr, shift_amount=2):
    # Shift no tempo para a direita
    shifted_audio = librosa.effects.preemphasis(audio, coef=shift_amount)
    
    return shifted_audio

def save_wav(file_path, audio, sr):
    sf.write(file_path, audio, sr)

def apply_time_shift_to_directory(input_folder, output_folder, shift_amount=2):
    # Certifique-se de que o diretório de saída existe
    os.makedirs(output_folder, exist_ok=True)

    # Percorre todos os arquivos na pasta de entrada
    for filename in os.listdir(input_folder):
        if filename.endswith(".wav"):
            string_aleatoria = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            wav_file = string_aleatoria + ".wav"
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, wav_file)

            # Carrega o arquivo de áudio usando librosa
            audio, sr = librosa.load(input_file_path, sr=None, duration=1.0)

            # Aplica o time shift para a direita
            shifted_audio = time_shift(audio, sr, shift_amount)

            # Salva o áudio modificado em um novo arquivo WAV
            save_wav(output_file_path, shifted_audio, sr)

if __name__ == "__main__":
    # Substitua 'G:/server/Home-Assistant-Server/test' pelo caminho do seu diretório de entrada
    input_folder_path = 'G:/server/Home-Assistant-Server/eden'

    # Substitua 'caminho/para/seu/diretorio_de_saida' pelo caminho do diretório de saída
    output_folder_path = 'G:/server/Home-Assistant-Server/data_augmentation'

    # Quantidade de deslocamento no tempo em segundos
    shift_amount_seconds = 2

    apply_time_shift_to_directory(input_folder_path, output_folder_path, shift_amount_seconds)
