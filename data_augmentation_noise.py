import os
import librosa
import numpy as np
import soundfile as sf

def add_noise(audio, noise_level=0.0001):
    noise = noise_level * np.random.randn(len(audio))
    return audio + noise

def augment_data_with_noise(input_folder, noise_level=0.005):
    # Percorra todos os arquivos na pasta de entrada
    for filename in os.listdir(input_folder):
        if filename.endswith(".wav"):
            input_path = os.path.join(input_folder, filename)

            # Carregue o arquivo de áudio usando librosa
            audio, sr = librosa.load(input_path, sr=None)

            # Aplique a adição de ruído
            augmented_audio = add_noise(audio, noise_level)

            # Construa o caminho de saída com um sufixo para o nome do arquivo aumentado
            output_filename = f"augmented_{filename}"
            output_path = os.path.join("G:/server/Home-Assistant-Server/data_augmentation_background", output_filename)

            # Salve o áudio aumentado no mesmo diretório que o original
            sf.write(output_path, augmented_audio, sr)

if __name__ == "__main__":
    input_folder = "G:/server/Home-Assistant-Server/background"

    # Ajuste o nível de ruído conforme necessário
    noise_level = 0.005

    augment_data_with_noise(input_folder, noise_level)
