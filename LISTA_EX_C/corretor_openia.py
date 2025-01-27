import os
import re
import tkinter as tk
import logging
from tkinter import ttk, messagebox
import openai
from dotenv import load_dotenv

# Configuração de ambiente
load_dotenv()  # Carrega variáveis do arquivo .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuração de logging
logging.basicConfig(
    filename='corretor_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constantes
MAX_TEXT_LENGTH = 500  # Limite máximo de caracteres

def correct_text(text):
    """Corrige texto usando a API da OpenAI com tratamento robusto de erros"""
    try:
        if not text.strip():
            return "Erro: Texto vazio. Por favor, digite algo para corrigir."
            
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "Você é um especialista em correção ortográfica e gramatical. "
                    "Corrija o texto preservando o estilo e formato original. "
                    "Mantenha a estrutura de parágrafos e pontuação."
                )},
                {"role": "user", "content": text}
            ],
            max_tokens=300,
            temperature=0.2,
            request_timeout=15  # Timeout de 15 segundos
        )
        return response.choices[0].message.content.strip()

    except openai.error.AuthenticationError:
        logging.error("Falha de autenticação na API")
        return "Erro: Chave de API inválida. Verifique as configurações."
    except openai.error.RateLimitError:
        logging.error("Limite de taxa excedido")
        return "Erro: Limite de requisições excedido. Tente novamente mais tarde."
    except openai.error.Timeout:
        logging.error("Timeout na requisição")
        return "Erro: Tempo de conexão esgotado. Verifique sua internet."
    except openai.error.APIError as e:
        logging.error(f"Erro de API: {str(e)}")
        return f"Erro na API: {str(e)}"
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}", exc_info=True)
        return f"Erro inesperado: {str(e)}"

class CorretorApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface gráfica"""
        self.root.title("Corretor Avançado GPT-3.5")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Estilos
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))
        
        # Controles
        self.create_widgets()
        
    def create_widgets(self):
        """Cria e posiciona os elementos da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Entrada de texto
        self.input_label = ttk.Label(main_frame, text="Digite seu texto (máximo 500 caracteres):")
        self.input_label.pack(anchor='w')
        
        self.input_text = tk.Text(
            main_frame,
            height=8,
            width=70,
            wrap='word',
            font=('Arial', 10)
        )
        self.input_text.pack(pady=5)
        
        # Contador de caracteres
        self.char_count = ttk.Label(main_frame, text="Caracteres: 0/500")
        self.char_count.pack(anchor='e')
        
        # Botão de correção
        self.btn_corrigir = ttk.Button(
            main_frame,
            text="Corrigir Texto",
            command=self.start_correction
        )
        self.btn_corrigir.pack(pady=10)
        
        # Saída de texto
        self.output_label = ttk.Label(main_frame, text="Texto Corrigido:")
        self.output_label.pack(anchor='w')
        
        self.output_text = tk.Text(
            main_frame,
            height=8,
            width=70,
            wrap='word',
            font=('Arial', 10),
            state='disabled'
        )
        self.output_text.pack()
        
        # Barra de progresso
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=200
        )
        
        # Eventos
        self.input_text.bind('<KeyRelease>', self.update_char_count)
        
    def update_char_count(self, event=None):
        """Atualiza o contador de caracteres"""
        text = self.input_text.get("1.0", "end-1c")
        count = len(text)
        self.char_count.config(text=f"Caracteres: {count}/500")
        
        # Altera cor se exceder o limite
        if count > MAX_TEXT_LENGTH:
            self.char_count.config(foreground='red')
        else:
            self.char_count.config(foreground='black')
            
    def toggle_loading(self, show=True):
        """Controla a exibição da barra de progresso"""
        if show:
            self.progress.pack(pady=5)
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.pack_forget()
            
    def start_correction(self):
        """Inicia o processo de correção"""
        text = self.input_text.get("1.0", "end-1c")
        
        # Validação de entrada
        if len(text) > MAX_TEXT_LENGTH:
            messagebox.showwarning(
                "Texto Muito Longo",
                f"O texto excede o limite de {MAX_TEXT_LENGTH} caracteres!"
            )
            return
            
        if not text.strip():
            messagebox.showwarning(
                "Texto Vazio",
                "Por favor, digite algum texto para corrigir."
            )
            return
            
        # Desabilita controles durante o processamento
        self.btn_corrigir.config(state='disabled')
        self.input_text.config(state='disabled')
        self.toggle_loading(True)
        
        # Executa em background para não travar a UI
        self.root.after(100, lambda: self.process_correction(text))
        
    def process_correction(self, text):
        """Executa a correção e atualiza a interface"""
        try:
            corrected = correct_text(text)
            self.show_result(corrected)
        finally:
            # Reabilita controles
            self.btn_corrigir.config(state='normal')
            self.input_text.config(state='normal')
            self.toggle_loading(False)
            
    def show_result(self, result):
        """Exibe o resultado na caixa de texto"""
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        
        # Destaque de erros
        if result.startswith("Erro:"):
            self.output_text.tag_configure('error', foreground='red')
            self.output_text.insert('1.0', result, 'error')
        else:
            self.output_text.insert('1.0', result)
            
        self.output_text.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = CorretorApp(root)
    root.mainloop()