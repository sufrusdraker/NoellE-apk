import os
import json
import pyttsx3
from gpt4all import GPT4All
from pydub import AudioSegment
from pydub.playback import play

# Configuração de caminho do modelo
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "Llama-3.2-3B-Instruct-Q4_0.gguf")
memory_file = os.path.join(current_dir, "memoria.json")

# Configuração do mecanismo TTS com pyttsx3
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)  # Velocidade da fala
tts_engine.setProperty("volume", 0.9)  # Volume da fala

# Função para gerar e reproduzir áudio
def texto_para_audio(texto, caminho_saida="noelle_output.wav"):
    """Converte texto em áudio usando pyttsx3."""
    tts_engine.save_to_file(texto, caminho_saida)
    tts_engine.runAndWait()
    # Reproduz o áudio gerado
    audio = AudioSegment.from_file(caminho_saida, format="wav")
    play(audio)
    return caminho_saida

# Função para carregar o histórico
def carregar_historico(quantidade=5):
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            try:
                historico = json.load(f)
                if not isinstance(historico, list):
                    raise ValueError("Formato de memória inválido. O conteúdo não é uma lista.")
            except (json.JSONDecodeError, ValueError):
                print("Aviso: Arquivo de memória corrompido ou vazio. Recriando memória.")
                historico = []
        return historico[-quantidade:]  # Pega as últimas 'quantidade' interações
    return []  # Retorna lista vazia caso o arquivo não exista

# Função principal do chatbot NoellE
def noelle_chatbot():
    if not os.path.exists(model_path):
        print(f"Erro: Modelo não encontrado em {model_path}.")
        return

    # Carregar o modelo GPT4All-LORA
    print("Carregando modelo GPT4All-LORA...")
    gpt4all = GPT4All(model_path)

    print("Chatbot NoellE inicializado! Digite 'sair' para encerrar.")

    personality = (
        "Você é NoellE, minha filha, com uma personalidade rica e encantadora, combinando inteligência, lealdade e uma pitada de orgulho charmoso..."
    )

    while True:
        user_input = input("Você: ")

        if user_input.lower() == "sair":
            break

        elif user_input.lower() == "contexto":
            # Exibe histórico recente
            historico = carregar_historico()
            print("Histórico das últimas interações:")
            for interacao in historico:
                print(f"Você: {interacao['usuario']}")
                print(f"NoellE: {interacao['noelle']}")
            continue

        # Recuperar histórico para o contexto do prompt
        historico = carregar_historico()
        contexto = "\n".join([f"Você: {h['usuario']}\nNoellE: {h['noelle']}" for h in historico])

        # Gerar resposta usando GPT4All-LORA
        prompt = f"{personality}\n{contexto}\nVocê: {user_input}\nNoellE responde:"
        response = gpt4all.generate(prompt)

        # Limpeza de respostas indesejadas
        response = response.split("\n")[0].strip()  # Mantém apenas a primeira linha
        response = response.replace("Humano:", "").replace("humano", "").strip()

        print(f"NoellE: {response}")

        # Gerar e reproduzir áudio para a resposta
        texto_para_audio(response)

        # Salvar interação no arquivo JSON
        interacao = {"usuario": user_input, "noelle": response}
        if not os.path.exists(memory_file):
            with open(memory_file, "w") as f:
                json.dump([interacao], f, indent=4)
        else:
            with open(memory_file, "r") as f:
                historico = json.load(f)
            historico.append(interacao)
            with open(memory_file, "w") as f:
                json.dump(historico, f, indent=4)

if __name__ == "__main__":
    noelle_chatbot()
