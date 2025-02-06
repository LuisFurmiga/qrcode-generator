import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser 
from PIL import Image, ImageTk
from viewmodel import QRCodeViewModel # type: ignore

class QRCodeView:

    LEFT_FRAME_WIDTH_SIZE = 350 # Largura Left Frame
    RIGHT_FRAME_WIDTH_SIZE = 330 # Largura Right Frame
    FRAME_HEIGHT_SIZE = 300 # Altura dos Frames, pois, como um frame está ao lado do outro, ambos possuem o mesmo tamanho
    
    QRCODE_SIZE = 200

    WINDOW_WIDTH_SIZE = int(LEFT_FRAME_WIDTH_SIZE) + int(RIGHT_FRAME_WIDTH_SIZE) 
    WINDOW_HEIGHT_SIZE = int(FRAME_HEIGHT_SIZE) + QRCODE_SIZE

    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de QR Code")
        self.WINDOWS_TOTAL_SIZE = str(self.WINDOW_WIDTH_SIZE)+"x"+str(self.WINDOW_HEIGHT_SIZE)
        self.root.geometry(self.WINDOWS_TOTAL_SIZE)
        self.root.resizable(False, False)

        self.viewmodel = QRCodeViewModel()

        # Frame principal
        self.frame_principal = ttk.Frame(self.root)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        self.frame_principal.grid_columnconfigure(0, weight=1)  # Frame esquerdo ocupa menos espaço
        self.frame_principal.grid_columnconfigure(1, weight=2)  # Frame direito ocupa mais espaço


        # Criar os frames esquerdo e direito
        self.frame_esquerdo = ttk.Frame(self.frame_principal, padding=10)
        self.frame_esquerdo.grid(row=0, column=0, sticky="ns")

        self.frame_direito = ttk.Frame(self.frame_principal, padding=10)
        self.frame_direito.grid(row=0, column=1, sticky="nsew")

        # Adicionando título ao frame esquerdo
        self.lbl_title = ttk.Label(self.frame_esquerdo, text="Gerador de QR Code", font=("Arial", 14, "bold"))
        self.lbl_title.grid(pady = 5, row = 0, columnspan = 2)

        # **Opções do QR Code no lado esquerdo**
        self.lbl_fg_color = ttk.Label(self.frame_esquerdo, text="Cor do QR Code:")
        self.lbl_fg_color.grid(pady = 5, row = 1, column = 0)

        self.btn_fg_color = ttk.Button(self.frame_esquerdo, text="Escolher Cor", command=self.selecionar_cor_fg)
        self.btn_fg_color.grid(pady = 5, row = 1, column = 1)

        self.lbl_bg_color = ttk.Label(self.frame_esquerdo, text="Cor de Fundo:")
        self.lbl_bg_color.grid(pady = 5, row = 2, column = 0)

        self.btn_bg_color = ttk.Button(self.frame_esquerdo, text="Escolher Cor", command=self.selecionar_cor_bg)
        self.btn_bg_color.grid(pady = 5, row = 2, column = 1)

        self.lbl_estilo = ttk.Label(self.frame_esquerdo, text="Estilo do QR Code:")
        self.lbl_estilo.grid(pady = 5, row = 3, column = 0)

        opcoes_estilo = ["Padrão", "Arredondado", "Quadrados Espaçados", "Círculos", "Barras Verticais", "Barras Horizontais"]
        self.combo_estilo = ttk.Combobox(self.frame_esquerdo, values=opcoes_estilo, state="readonly")
        self.combo_estilo.grid(pady = 5, row = 3, column = 1)
        self.combo_estilo.current(0)

        self.logo_var = tk.IntVar(value=0)
        self.chk_logo = ttk.Checkbutton(self.frame_esquerdo, text="Incluir logo no QR Code", variable=self.logo_var)
        self.chk_logo.grid(pady = 5, row = 4, column = 0)

        self.btn_selecionar_logo = ttk.Button(self.frame_esquerdo, text="Selecionar Logo", command=self.selecionar_logo)
        self.btn_selecionar_logo.grid(pady = 5, row = 4, column = 1)

        self.lbl_logo_path = ttk.Label(self.frame_esquerdo, text="Nenhuma logo selecionada", foreground="gray")
        self.lbl_logo_path.grid(pady = 5, row = 5, columnspan = 2)

        # Botão para gerar QR Code
        self.btn_gerar = ttk.Button(self.frame_esquerdo, text="Gerar QR Code", style="Primary.TButton", command=self.gerar_qr_code)
        self.btn_gerar.grid(pady = 5, row = 6, columnspan = 2)

        # Rótulo de status
        self.lbl_status = ttk.Label(self.frame_esquerdo, text="", foreground="blue")
        self.lbl_status.grid(pady = 5, row = 7, columnspan = 2)

        # Rótulo para exibir o QR Code gerado
        self.lbl_imagem = ttk.Label(self.frame_esquerdo)
        self.lbl_imagem.grid(pady = 5, row = 8, columnspan = 2)

        # Criar um frame para o QR Code com borda em baixo relevo
        self.qr_frame = tk.Frame(self.frame_esquerdo, width=self.QRCODE_SIZE + 5, height=self.QRCODE_SIZE + 5, relief="sunken", borderwidth=2)
        self.qr_frame.grid(pady = 5, row = 8, columnspan = 2)
        self.qr_frame.pack_propagate(False)  # Impede que o frame se redimensione

        # Criar o rótulo de imagem dentro do frame
        self.lbl_imagem = ttk.Label(self.qr_frame)
        self.lbl_imagem.pack(expand=True, fill="both")

        # **Campos de entrada no lado direito (com rolagem)**
        self.canvas = tk.Canvas(self.frame_direito, width=self.RIGHT_FRAME_WIDTH_SIZE, height=self.FRAME_HEIGHT_SIZE, highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self.frame_direito, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        # Seleção do tipo de QR Code
        self.lbl_tipo = ttk.Label(self.scroll_frame, text="Tipo de QR Code:")
        self.lbl_tipo.pack(pady=5, fill="both", expand=True)

        opcoes = ["URL", "Texto", "Número de telefone", "SMS", "E-mail", "Contato (vCard)", "Localização", "WhatsApp", "Wi-Fi"]
        self.combo_tipo = ttk.Combobox(self.scroll_frame, values=opcoes, state="readonly")
        self.combo_tipo.pack(pady=5, fill="both", expand=True)
        self.combo_tipo.bind("<<ComboboxSelected>>", self.atualizar_campos)

        # Criar frames para cada tipo de entrada
        self.frames = {}
        WIDTH_SETTED = 40
        def criar_frame(tipo, campos):
            """Cria um frame dentro do frame da direita (scroll_frame) e adiciona os campos"""
            frame = tk.Frame(self.scroll_frame)
            vars = []
            for label_text in campos:
                lbl = tk.Label(frame, text=label_text)
                lbl.pack(anchor="w")  # Alinhado à esquerda
                lbl.pack()
                entry = tk.Entry(frame, width=WIDTH_SETTED)
                entry.pack(anchor="w", pady=2)
                vars.append(entry)

            return frame, vars

        self.frames["URL"], self.entry_url = criar_frame("URL", ["Digite a URL:"])
        self.frames["Texto"], self.entry_texto = criar_frame("Texto", ["Digite o texto:"])
        self.frames["Número de telefone"], self.entry_telefone = criar_frame("Número de telefone", ["Digite o número:"])
        self.frames["SMS"], (self.entry_sms_numero, self.entry_sms_mensagem) = criar_frame("SMS", ["Número do destinatário:", "Mensagem:"])
        self.frames["Contato (vCard)"], (self.entry_vcard_nome, self.entry_vcard_telefone, self.entry_vcard_email, self.entry_vcard_url) = criar_frame("Contato (vCard)", ["Nome:", "Telefone:", "E-mail:", "Seu site:"])
        self.frames["Localização"], (self.entry_latitude, self.entry_longitude) = criar_frame("Localização", ["Latitude:", "Longitude:"])

        # Criar frame E-Mail
        self.frames["E-mail"] = tk.Frame(self.scroll_frame)
        self.lbl_email = tk.Label(self.frames["E-mail"], text="E-Mail:")
        self.lbl_email.pack(anchor="w")
        self.entry_email = tk.Entry(self.frames["E-mail"], width=WIDTH_SETTED)
        self.entry_email.pack(anchor="w")
        self.lbl_email_subject = tk.Label(self.frames["E-mail"], text="Assunto:")
        self.lbl_email_subject.pack(anchor="w")
        self.entry_email_subject = tk.Entry(self.frames["E-mail"], width=WIDTH_SETTED)
        self.entry_email_subject.pack(anchor="w")
        self.lbl_email_body = tk.Label(self.frames["E-mail"], text="Conteudo:")
        self.lbl_email_body.pack(anchor="w")
        self.entry_email_body = tk.Text(self.frames["E-mail"], width=WIDTH_SETTED, height=6)
        self.entry_email_body.pack(anchor="w", pady=2)

        # Criar frame WhatsApp
        self.frames["WhatsApp"] = tk.Frame(self.scroll_frame)
        self.lbl_whatsapp_pais = tk.Label(self.frames["WhatsApp"], text="Código do País:")
        self.lbl_whatsapp_pais.pack(anchor="w")
        self.combo_whatsapp_pais = ttk.Combobox(self.frames["WhatsApp"], values=["", "55"], state="readonly")
        self.combo_whatsapp_pais.current(0)
        self.combo_whatsapp_pais.pack(anchor="w")
        self.lbl_whatsapp_estado = tk.Label(self.frames["WhatsApp"], text="Código do Estado:")
        self.lbl_whatsapp_estado.pack(anchor="w")
        self.combo_whatsapp_estado = ttk.Combobox(self.frames["WhatsApp"], values=["", "11", "21", "31", "37"], state="readonly")
        self.combo_whatsapp_estado.current(0)
        self.combo_whatsapp_estado.pack(anchor="w")
        self.lbl_whatsapp_numero = tk.Label(self.frames["WhatsApp"], text="Número:")
        self.lbl_whatsapp_numero.pack(anchor="w")
        self.entry_whatsapp_numero = tk.Entry(self.frames["WhatsApp"], width=WIDTH_SETTED)
        self.entry_whatsapp_numero.pack(anchor="w")
        self.lbl_whatsapp_texto = tk.Label(self.frames["WhatsApp"], text="Mensagem:")
        self.lbl_whatsapp_texto.pack(anchor="w")
        self.entry_whatsapp_texto = tk.Text(self.frames["WhatsApp"], width=WIDTH_SETTED, height=6)
        self.entry_whatsapp_texto.pack(anchor="w", pady=2)

        # Criar frame Wi-Fi
        self.frames["Wi-Fi"] = tk.Frame(self.scroll_frame)
        self.lbl_ssid = tk.Label(self.frames["Wi-Fi"], text="Nome da Rede (SSID):")
        self.lbl_ssid.pack(anchor="w")
        self.entry_wifi_ssid = tk.Entry(self.frames["Wi-Fi"], width=WIDTH_SETTED)
        self.entry_wifi_ssid.pack(anchor="w")
        self.wifi_hidden_var = tk.IntVar()
        self.check_wifi_hidden = tk.Checkbutton(self.frames["Wi-Fi"], text="Rede Oculta", variable=self.wifi_hidden_var)
        self.check_wifi_hidden.pack()
        self.lbl_senha = tk.Label(self.frames["Wi-Fi"], text="Senha da Rede:")
        self.lbl_senha.pack(anchor="w")
        self.entry_wifi_senha = tk.Entry(self.frames["Wi-Fi"], width=WIDTH_SETTED)
        self.entry_wifi_senha.pack(anchor="w")
        self.lbl_tipo_wifi = tk.Label(self.frames["Wi-Fi"], text="Tipo de Segurança:")
        self.lbl_tipo_wifi.pack(anchor="w")
        self.combo_wifi_tipo = ttk.Combobox(self.frames["Wi-Fi"], values=["WPA/WPA2", "WEP", "Nenhuma"], state="readonly")
        self.combo_wifi_tipo.pack(anchor="w")

    def selecionar_cor_fg(self):
        """Abre o seletor de cor para a cor do QR Code"""
        cor = colorchooser.askcolor(title="Selecione a Cor do QR Code")[1]
        if cor:
            self.viewmodel.set_fg_color(cor)
            self.btn_fg_color.config(text=f"Cor: {cor}")

    def selecionar_cor_bg(self):
        """Abre o seletor de cor para o fundo do QR Code"""
        cor = colorchooser.askcolor(title="Selecione a Cor de Fundo")[1]
        if cor:
            self.viewmodel.set_bg_color(cor)
            self.btn_bg_color.config(text=f"Cor: {cor}")

    def selecionar_logo(self):
        """Abre o seletor de arquivos para escolher a logo"""
        path = filedialog.askopenfilename(title="Selecione a Logo", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if path:
            self.viewmodel.set_logo(path)
            self.lbl_logo_path.config(text=f"Logo: {path.split('/')[-1]}", foreground="black")

    def gerar_qr_code(self):
        """Gera o QR Code com base na entrada do usuário"""
        self.lbl_status.config(text="Gerando QR Code...")
        tipo = self.combo_tipo.get()
        estilo = self.combo_estilo.get()
        incluir_logo = self.chk_logo.instate(['selected'])
        dados = ""

        # Obtendo os dados corretos com base no tipo selecionado
        if tipo == "URL":
            dados = self.entry_url[0].get()
        elif tipo == "Texto":
            dados = self.entry_texto[0].get()
        elif tipo == "Número de telefone":
            dados = f"tel:{self.entry_telefone[0].get()}"
        elif tipo == "SMS":
            dados = f"smsto:{self.entry_sms_numero[0].get()}:{self.entry_sms_mensagem[0].get()}"
        elif tipo == "E-mail":
            dados = f"mailto:{self.entry_email.get()}?subject={self.entry_email_subject.get()}&body={self.entry_email_body.get('1.0', tk.END).strip()}"
        elif tipo == "Contato (vCard)":
            dados = f"BEGIN:VCARD\nFN:{self.entry_vcard_nome[0].get()}\nTEL:{self.entry_vcard_telefone[0].get()}\nEMAIL:{self.entry_vcard_email[0].get()}\nURL:{self.entry_vcard_url[0].get()}\nEND:VCARD"
        elif tipo == "Localização":
            dados = f"geo:{self.entry_latitude[0].get()},{self.entry_longitude[0].get()}"
        elif tipo == "WhatsApp":
            dados = f"https://wa.me/{self.combo_whatsapp_pais.get()}{self.combo_whatsapp_estado.get()}{self.entry_whatsapp_numero.get()}?text={self.entry_whatsapp_texto.get("1.0", tk.END).strip()}"
        elif tipo == "Wi-Fi":
            dados = f"WIFI:T:{self.combo_wifi_tipo.get()};S:{self.entry_wifi_ssid.get()};P:{self.entry_wifi_senha.get()};H:{self.wifi_hidden_var.get()};;"

        if not dados.strip():
            messagebox.showerror("Erro", "Por favor, preencha todos os campos necessários.")
            self.lbl_status.config(text="")
            return

        # Chama a ViewModel para gerar o QR Code em outra thread
        self.viewmodel.gerar_qr_code(dados, estilo, incluir_logo, self.atualizar_imagem)


    def atualizar_campos(self, event=None):
        """Exibe os campos corretos conforme o tipo de QR Code selecionado"""
        tipo = self.combo_tipo.get()

        # Esconder todos os frames antes de mostrar o necessário
        for frame in self.frames.values():
            frame.pack_forget()

        # Exibir o frame correspondente ao tipo selecionado
        if tipo in self.frames:
            self.frames[tipo].pack(pady=5)

    def atualizar_imagem(self, img_path):
        img = Image.open(img_path).resize((self.QRCODE_SIZE, self.QRCODE_SIZE))
        img = ImageTk.PhotoImage(img)
        self.lbl_imagem.config(image=img)
        self.lbl_imagem.image = img
        self.lbl_status.config(text="")
