#import nltk
#nltk.download('punkt')
#nltk.download('words')
import re
import tkinter as tk
from tkinter import ttk, messagebox
from transformers import pipeline
import logging

# Configuração de logging
logging.basicConfig(
    filename='corretor_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Carrega o modelo de correção ortográfica
try:
    corretor = pipeline("text2text-generation", model="unicamp-dl/ptt5-base-grammar-correction")
except Exception as e:
    logging.error(f"Erro ao carregar o modelo: {str(e)}")
    raise

# Função para corrigir texto usando o modelo do Hugging Face
def correct_text(text):
    try:
        if not text.strip():
            return "Erro: Texto vazio. Por favor, digite algo para corrigir."
        
        # Corrige o texto usando o modelo
        result = corretor(text)
        return result[0]['generated_text']
    except Exception as e:
        logging.error(f"Erro ao corrigir o texto: {str(e)}")
        return f"Erro: {str(e)}"

class CorretorApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface gráfica"""
        self.root.title("Corretor Ortográfico com Hugging Face")
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
        self.input_label = ttk.Label(main_frame, text="Digite seu texto:")
        self.input_label.pack(anchor='w')
        
        self.input_text = tk.Text(
            main_frame,
            height=8,
            width=70,
            wrap='word',
            font=('Arial', 10)
        )
        self.input_text.pack(pady=5)
        
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