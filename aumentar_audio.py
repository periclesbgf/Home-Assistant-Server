from pydub import AudioSegment

def aumentar_volume(input_file, output_file, aumento_em_db):
    # Carregar o arquivo de áudio
    audio = AudioSegment.from_wav(input_file)

    # Aumentar o volume em dB
    audio = audio + aumento_em_db

    # Salvar o novo arquivo de áudio
    audio.export(output_file, format="wav")

# Exemplo de uso
input_file = "audio_received11.wav"
output_file = "seuarquivo_aumentado2.wav"
aumento_em_db = 20  # Ajuste o valor conforme necessário

aumentar_volume(input_file, output_file, aumento_em_db)