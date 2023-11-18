import os
from pydub import AudioSegment

def aumentar_volume(input_folder, output_folder, gain_dB):
    # Certifique-se de que o diretório de saída existe
    os.makedirs(output_folder, exist_ok=True)

    # Percorra todos os arquivos na pasta de entrada
    for filename in os.listdir(input_folder):
        if filename.endswith(".wav"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"louder_{filename}")

            # Carregue o arquivo de áudio usando pydub
            audio = AudioSegment.from_wav(input_path)

            # Aumente o volume usando a função de ganho
            audio = audio + gain_dB

            # Salve o áudio aumentado no diretório de saída
            audio.export(output_path, format="wav")

if __name__ == "__main__":
    # Substitua 'caminho/para/seu/diretorio_de_entrada' pelo caminho do seu diretório de entrada
    input_folder_path = 'G:/server/Home-Assistant-Server/eden'
    
    # Substitua 'caminho/para/seu/diretorio_de_saida' pelo caminho do diretório de saída
    output_folder_path = 'G:/server/Home-Assistant-Server/aumentados'

    # Ajuste o ganho conforme necessário (10 dB é um aumento significativo)
    gain_dB = 10

    aumentar_volume(input_folder_path, output_folder_path, gain_dB)
