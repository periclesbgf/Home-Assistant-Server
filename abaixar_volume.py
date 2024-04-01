import wave
import numpy as np

wav_file_path = "G:/server/Home-Assistant-Server/reformated.wav"

def adjust_volume(input_path, output_path, volume_scale):
    # Abrir arquivo WAV original
    with wave.open(input_path, 'rb') as wav:
        params = wav.getparams()
        frames = wav.readframes(params.nframes)
    
    # Converter frames para array numpy
    audio = np.frombuffer(frames, dtype=np.int16)
    
    # Ajustar o volume
    adjusted_audio = (audio * volume_scale).astype(np.int16)
    
    # Salvar o arquivo com volume ajustado
    with wave.open(output_path, 'wb') as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(adjusted_audio.tobytes())

# Caminho do arquivo WAV original
input_path = wav_file_path
# Caminho para salvar o arquivo WAV com volume ajustado
output_path = "G:/server/Home-Assistant-Server/reformated2.wav"
# Fator de escala para ajustar o volume, e.g., 0.5 para reduzir o volume pela metade
volume_scale = 0.5

adjust_volume(input_path, output_path, volume_scale)
