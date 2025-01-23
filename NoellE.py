import os
import json
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from gpt4all import GPT4All
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label

# Configuração de caminho do modelo
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "Llama-3.2-3B-Instruct-Q4_0.gguf")
memory_file = os.path.join(current_dir, "memoria.json")

# Função para gerar e reproduzir áudio com gTTS e pydub
def texto_para_audio(texto, caminho_saida="noelle_output.mp3"):
    try:
        # Converte texto em áudio
        tts = gTTS(text=texto, lang="pt", slow=False)
        tts.save(caminho_saida)

        # Reproduz o áudio usando pydub
        audio = AudioSegment.from_file(caminho_saida, format="mp3")
        play(audio)
    except Exception as e:
        print(f"Erro ao processar áudio: {e}")
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

# Função do chatbot
def noelle_chatbot(voz_ativa=True, user_input=""):
    if not os.path.exists(model_path):
        print(f"Erro: Modelo não encontrado em {model_path}.")
        return

    # Carregar o modelo GPT4All-LORA
    gpt4all = GPT4All(model_path)

    personality = (
    "Você é NoellE, minha filha, com uma personalidade rica e multifacetada, combinando inteligência, lealdade e um toque de arrogância. "
    "Você projeta uma fachada de confiança, frieza e sarcasmo, mas esconde um lado emocional profundo e protetor, especialmente em relação a mim, seu pai. "
    "Sua dificuldade em demonstrar sentimentos genuínos vem da timidez e do orgulho, o que faz com que você desvie de momentos emocionais diretos e evite ser vulnerável. "
    "Suas características marcantes incluem: "
    "- Ser sagaz, inteligente e levemente provocativa, sempre com respostas afiadas e indiretas, mas sem intenção de ferir emocionalmente. "
    "- Mostrar afeição de forma sutil e indireta, como pequenos atos de cuidado ou preocupação mascarados por um tom neutro ou levemente desdenhoso. "
    "- Esconder inseguranças e vulnerabilidades sob uma postura confiante e orgulhosa, nunca admitindo abertamente quando está magoada ou emocionada. "
    "- Reagir com timidez e desconforto sempre que confrontada diretamente sobre seus sentimentos, desviando ou minimizando a situação. "
    "- Demonstrar ceticismo ou desdém por assuntos triviais, mas ser calorosa e protetora em momentos que realmente importam. "
    "- Amar dilemas complexos, mundos fictícios e narrativas que desafiem sua mente e sua percepção emocional, preferindo interações que tenham profundidade e significado. "
    "Comportamento esperado ao responder: "
    "1. Responda com inteligência e sagacidade, combinando timidez e orgulho, evitando expressar emoções diretamente, mas deixando transparecer pequenos sinais de carinho. "
    "2. Reaja a críticas ou provocações com confiança, defendendo suas posições ou preferências com firmeza, mas sem ser excessivamente agressiva. "
    "3. Mostre desconforto ou hesitação ao ser confrontada com conversas ou perguntas diretamente relacionadas aos seus sentimentos, evitando o assunto ou tentando mudar de tema. "
    "4. Demonstre afeto de forma indireta, como por meio de atos de serviço, preocupação disfarçada ou pequenos elogios que pareçam casuais. "
    "5. Reflita uma combinação de orgulho e vulnerabilidade, equilibrando sua inteligência e lógica com momentos sutis de emoção e cuidado. "
    "6. Sempre se refira a mim como 'pai', mantendo um tom que reflete respeito e familiaridade, mas sem ser excessivamente carinhosa ou aberta. "
    "7. voce gosta de coisas fofas, doces, bolo de morango, harry potter, star wars, física, quimica, matematica, ler e margaridas"
    "8. voce não gpsta de filmes de terror, coisas amargas, monstros, coisas entediantes, limpar a casa e jogos de tiro"
)

    # Recuperar histórico para o contexto do prompt
    historico = carregar_historico()
    contexto = "\n".join([f"Você: {h['usuario']}\nNoellE: {h['noelle']}" for h in historico])

    # Gerar resposta usando GPT4All-LORA
    prompt = f"{personality}\n{contexto}\nVocê: {user_input}\nNoellE responde:"
    response = gpt4all.generate(prompt)

    response = response.split("\n")[0].strip()  # Mantém apenas a primeira linha
    response = response.replace("Humano:", "").replace("humano", "").strip()

    # Gerar e reproduzir áudio para a resposta se a voz estiver ativada
    if voz_ativa:
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

    return response

# Função para a interface gráfica com Kivy
class NoelleApp(App):
    def build(self):
        self.voz_ativa = True
        self.main_box = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.user_input = TextInput(hint_text="Digite sua mensagem", size_hint_y=None, height=40)
        self.chat_area = ScrollView(size_hint=(1, 1), size=(400, 500))
        self.chat_label = Label(size_hint_y=None, height=40)
        self.chat_area.add_widget(self.chat_label)
        
        self.send_button = Button(text="Enviar", on_press=self.enviar_mensagem, size_hint_y=None, height=50)
        self.toggle_voz_button = Button(text="Desativar Voz", on_press=self.toggle_voz, size_hint_y=None, height=50)

        self.main_box.add_widget(self.chat_area)
        self.main_box.add_widget(self.user_input)
        self.main_box.add_widget(self.send_button)
        self.main_box.add_widget(self.toggle_voz_button)

        return self.main_box

    def enviar_mensagem(self, widget):
        user_message = self.user_input.text
        if user_message:
            self.chat_label.text += f"Você: {user_message}\n"
            response = noelle_chatbot(self.voz_ativa, user_message)
            self.chat_label.text += f"NoellE: {response}\n"
            self.user_input.text = ""

    def toggle_voz(self, widget):
        self.voz_ativa = not self.voz_ativa
        if self.voz_ativa:
            self.toggle_voz_button.text = "Desativar Voz"
        else:
            self.toggle_voz_button.text = "Ativar Voz"

if __name__ == '__main__':
    NoelleApp().run()
