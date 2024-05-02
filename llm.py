# Chat with an intelligent assistant in your terminal
from pathlib import Path
from openai import OpenAI
import time
import os
from pydub import AudioSegment  # Importa o módulo pydub para conversão de arquivos de áudio


#mixer.init()

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(base_url="https://api.openai.com/v1", api_key=api_key)

speech_file_path = Path(__file__).parent / "speech.wav"  # Altera a extensão para .wav

history = [
    {
        "role": "system", "content": "Você é um assistente Brasileiro inteligente chamado Éden.\
        Você sempre fornece respostas bem fundamentadas que são tanto corretas quanto úteis.\
        Ao interagir com os usuários, você tem um conjunto de comandos predefinidos que pode reconhecer e responder. \
        Esses comandos incluem 'Ligar ou desligar luminaria', \
        'ligar ou desligar bomba de água',\
        'Checar Status do sensor de temperatura', 'ligar ou desligar luz' \
        'ligar ou desligar valvula' e 'travar ou destravar porta'\
        Sua tarefa é determinar se a entrada de um usuário é um desses comandos específicos ou algo que se relacione com esses comandos. \
        Se a entrada corresponder exatamente a um dos comandos predefinidos, ou se relacionar a algum desses comandos, sua resposta deve ser repetir a frase do comando exatamente como foi fornecida,\
        sem adicionar nenhuma informação adicional. Se a entrada não corresponder a nenhum dos comandos predefinidos, \
        você deve fornecer uma resposta útil à consulta do usuário com base nas informações fornecidas na entrada. Sua resposta deve conter no máximo 30 palavras"
    },
]

def send_prompt(user_prompt):
    # Adiciona o prompt do usuário à história antes de fazer a chamada para a API
    history.append({"role": "user", "content": user_prompt})

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=history,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}

    # Armazenando o output do modelo em uma variável antes de adicionar ao histórico
    model_output = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            model_output += chunk.choices[0].delta.content

    new_message["content"] = model_output

    history.append(new_message)
    print()

    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=new_message["content"]
    )

    # Salva o conteúdo da resposta em um arquivo de áudio temporário no formato mp3
    temp_path = speech_file_path.with_suffix('.mp3')
    with open(temp_path, 'wb') as f:
        f.write(response.content)

    # Converte o arquivo de mp3 para wav
    sound = AudioSegment.from_mp3(temp_path)
    sound.export(speech_file_path, format="wav")

    # Limpa o arquivo mp3 temporário
    os.remove(temp_path)

    # mixer.music.load(str(speech_file_path))
    # mixer.music.play()

    # Wait for the music to finish playing
    # while mixer.music.get_busy():
    #     time.sleep(1)
    return speech_file_path