# view.py — versão 3.2 (fix: container fixo para frames dinâmicos)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from PIL import Image, ImageTk
from viewmodel import QRCodeViewModel  # type: ignore
import os

class QRCodeView:

    LEFT_FRAME_WIDTH_SIZE = 420
    RIGHT_FRAME_WIDTH_SIZE = 300
    FRAME_HEIGHT_SIZE = 850

    QRCODE_SIZE = 240

    WINDOW_WIDTH_SIZE = int(LEFT_FRAME_WIDTH_SIZE) + int(RIGHT_FRAME_WIDTH_SIZE)
    WINDOW_HEIGHT_SIZE = int(FRAME_HEIGHT_SIZE)

    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de QR Code")
        self.WINDOWS_TOTAL_SIZE = str(self.WINDOW_WIDTH_SIZE) + "x" + str(self.WINDOW_HEIGHT_SIZE)
        self.root.geometry(self.WINDOWS_TOTAL_SIZE)
        self.root.resizable(False, False)

        self.viewmodel = QRCodeViewModel()
        self.output_path = "qrcode.png"

        self.frame_principal = ttk.Frame(self.root); self.frame_principal.pack(fill=tk.BOTH, expand=True)
        self.frame_principal.grid_columnconfigure(0, weight=1); self.frame_principal.grid_columnconfigure(1, weight=2)

        self.frame_esquerdo = ttk.Frame(self.frame_principal, padding=10); self.frame_esquerdo.grid(row=0, column=0, sticky="ns")
        self.frame_direito = ttk.Frame(self.frame_principal, padding=10); self.frame_direito.grid(row=0, column=1, sticky="nsew")

        row = 0
        ttk.Label(self.frame_esquerdo, text="Aparência", font=("Arial", 13, "bold")).grid(row=row, column=0, columnspan=2, pady=(0,6)); row+=1

        ttk.Label(self.frame_esquerdo, text="Cor do QR Code:").grid(pady=3, row=row, column=0, sticky="w")
        ttk.Button(self.frame_esquerdo, text="Escolher", command=self.selecionar_cor_fg).grid(pady=3, row=row, column=1, sticky="e"); row+=1
        ttk.Label(self.frame_esquerdo, text="Cor de Fundo:").grid(pady=3, row=row, column=0, sticky="w")
        ttk.Button(self.frame_esquerdo, text="Escolher", command=self.selecionar_cor_bg).grid(pady=3, row=row, column=1, sticky="e"); row+=1

        ttk.Label(self.frame_esquerdo, text="Estilo do QR Code:").grid(pady=3, row=row, column=0, sticky="w")
        opcoes_estilo = ["Padrão", "Quadrado", "Arredondado", "Quadrados Espaçados", "Círculos", "Barras Verticais", "Barras Horizontais"]
        self.combo_estilo = ttk.Combobox(self.frame_esquerdo, values=opcoes_estilo, state="readonly"); self.combo_estilo.grid(pady=3, row=row, column=1, sticky="ew"); self.combo_estilo.current(0); row+=1

        ttk.Label(self.frame_esquerdo, text="Olhos (Finders):").grid(pady=3, row=row, column=0, sticky="w")
        opcoes_olhos = ["Padrão", "Quadrado", "Arredondado", "Círculos"]
        self.combo_olhos = ttk.Combobox(self.frame_esquerdo, values=opcoes_olhos, state="readonly"); self.combo_olhos.grid(pady=3, row=row, column=1, sticky="ew"); self.combo_olhos.current(0); row+=1

        ttk.Label(self.frame_esquerdo, text="Preenchimento:").grid(pady=3, row=row, column=0, sticky="w")
        self.fill_options = ["Sólido", "Gradiente Horizontal", "Gradiente Vertical", "Gradiente Radial", "Imagem"]
        self.combo_fill = ttk.Combobox(self.frame_esquerdo, values=self.fill_options, state="readonly"); self.combo_fill.grid(pady=3, row=row, column=1, sticky="ew"); self.combo_fill.current(0); self.combo_fill.bind("<<ComboboxSelected>>", self._on_fill_changed); row+=1
        self.btn_fill_image = ttk.Button(self.frame_esquerdo, text="Imagem de Preenchimento", command=self.selecionar_imagem_preenchimento)
        self.btn_fill_image.grid(pady=2, row=row, column=0, columnspan=2); self.btn_fill_image.grid_remove(); row+=1

        ttk.Label(self.frame_esquerdo, text="Fundo (imagem):").grid(pady=3, row=row, column=0, sticky="w")
        ttk.Button(self.frame_esquerdo, text="Selecionar", command=self.selecionar_fundo).grid(pady=3, row=row, column=1, sticky="e"); row+=1
        ttk.Label(self.frame_esquerdo, text="Fundo alpha (0-100%):").grid(pady=3, row=row, column=0, sticky="w")
        self.scale_bg_alpha = ttk.Scale(self.frame_esquerdo, from_=0, to=100, orient="horizontal"); self.scale_bg_alpha.set(100); self.scale_bg_alpha.grid(pady=3, row=row, column=1, sticky="ew"); row+=1
        self.bg_image_path = None

        ttk.Label(self.frame_esquerdo, text="Logo").grid(pady=(10,3), row=row, column=0, columnspan=2, sticky="w"); row+=1
        self.logo_var = tk.IntVar(value=0)
        ttk.Checkbutton(self.frame_esquerdo, text="Incluir logo", variable=self.logo_var).grid(pady=3, row=row, column=0, sticky="w")
        ttk.Button(self.frame_esquerdo, text="Selecionar Logo", command=self.selecionar_logo).grid(pady=3, row=row, column=1, sticky="e"); row+=1
        ttk.Label(self.frame_esquerdo, text="Escala (2=maior, 10=menor):").grid(pady=3, row=row, column=0, sticky="w")
        self.spin_logo_scale = tk.Spinbox(self.frame_esquerdo, from_=2, to=10, width=5); self.spin_logo_scale.delete(0,"end"); self.spin_logo_scale.insert(0,"5"); self.spin_logo_scale.grid(pady=3, row=row, column=1, sticky="e"); row+=1
        ttk.Label(self.frame_esquerdo, text="Borda da logo (px):").grid(pady=3, row=row, column=0, sticky="w")
        self.spin_logo_border = tk.Spinbox(self.frame_esquerdo, from_=0, to=32, width=5); self.spin_logo_border.delete(0,"end"); self.spin_logo_border.insert(0,"8"); self.spin_logo_border.grid(pady=3, row=row, column=1, sticky="e"); row+=1
        ttk.Label(self.frame_esquerdo, text="Raio dos cantos (px):").grid(pady=3, row=row, column=0, sticky="w")
        self.spin_logo_radius = tk.Spinbox(self.frame_esquerdo, from_=0, to=64, width=5); self.spin_logo_radius.delete(0,"end"); self.spin_logo_radius.insert(0,"20"); self.spin_logo_radius.grid(pady=3, row=row, column=1, sticky="e"); row+=1
        ttk.Label(self.frame_esquerdo, text="Cor da borda:").grid(pady=3, row=row, column=0, sticky="w")
        ttk.Button(self.frame_esquerdo, text="Escolher", command=self.selecionar_cor_borda_logo).grid(pady=3, row=row, column=1, sticky="e"); row+=1
        self.logo_border_color = "#FFFFFF"
        self.logo_path = None

        ttk.Label(self.frame_direito, text="Conteúdo e Exportação", font=("Arial", 13, "bold")).pack(pady=(0,6), anchor="w")
        self.canvas = tk.Canvas(self.frame_direito, width=self.RIGHT_FRAME_WIDTH_SIZE, height=self.FRAME_HEIGHT_SIZE, highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self.frame_direito, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        ttk.Label(self.scroll_frame, text="Tipo de QR Code:").pack(pady=3, anchor="w")
        opcoes = ["URL", "Texto", "Número de telefone", "SMS", "E-mail", "Contato (vCard)", "Localização", "WhatsApp", "Wi-Fi"]
        self.combo_tipo = ttk.Combobox(self.scroll_frame, values=opcoes, state="readonly")
        self.combo_tipo.pack(pady=3, fill="x"); self.combo_tipo.bind("<<ComboboxSelected>>", self.atualizar_campos)

        # >>> Container fixo para frames dinâmicos <<<
        self.dynamic_container = tk.Frame(self.scroll_frame)
        self.dynamic_container.pack(fill="x", pady=5, anchor="w")

        self.frames = {}
        WIDTH_SETTED = 40
        def criar_frame(campos):
            frame = tk.Frame(self.dynamic_container)  # OBS: dentro do dynamic_container
            vars = []
            for label_text in campos:
                lbl = tk.Label(frame, text=label_text); lbl.pack(anchor="w")
                entry = tk.Entry(frame, width=WIDTH_SETTED); entry.pack(anchor="w", pady=2); vars.append(entry)
            return frame, vars

        # Frames de conteúdo
        self.frames["URL"], self.entry_url = criar_frame(["Digite a URL:"])
        self.frames["Texto"], self.entry_texto = criar_frame(["Digite o texto:"])
        self.frames["Número de telefone"], self.entry_telefone = criar_frame(["Digite o número:"])
        self.frames["SMS"], (self.entry_sms_numero, self.entry_sms_mensagem) = criar_frame(["Número do destinatário:", "Mensagem:"])
        self.frames["Contato (vCard)"], (self.entry_vcard_nome, self.entry_vcard_telefone, self.entry_vcard_email, self.entry_vcard_url) = criar_frame(["Nome:", "Telefone:", "E-mail:", "Seu site:"])
        self.frames["Localização"], (self.entry_latitude, self.entry_longitude) = criar_frame(["Latitude:", "Longitude:"])

        # E-mail (tem Text multi-linha)
        self.frames["E-mail"] = tk.Frame(self.dynamic_container)
        tk.Label(self.frames["E-mail"], text="E-Mail:").pack(anchor="w")
        self.entry_email = tk.Entry(self.frames["E-mail"], width=WIDTH_SETTED); self.entry_email.pack(anchor="w")
        tk.Label(self.frames["E-mail"], text="Assunto:").pack(anchor="w")
        self.entry_email_subject = tk.Entry(self.frames["E-mail"], width=WIDTH_SETTED); self.entry_email_subject.pack(anchor="w")
        tk.Label(self.frames["E-mail"], text="Conteudo:").pack(anchor="w")
        self.entry_email_body = tk.Text(self.frames["E-mail"], width=WIDTH_SETTED, height=6); self.entry_email_body.pack(anchor="w", pady=2)

        # WhatsApp
        self.frames["WhatsApp"] = tk.Frame(self.dynamic_container)
        tk.Label(self.frames["WhatsApp"], text="Código do País:").pack(anchor="w")
        self.combo_whatsapp_pais = ttk.Combobox(self.frames["WhatsApp"], values=["", "55"], state="readonly"); self.combo_whatsapp_pais.current(0); self.combo_whatsapp_pais.pack(anchor="w")
        tk.Label(self.frames["WhatsApp"], text="Código do Estado:").pack(anchor="w")
        self.combo_whatsapp_estado = ttk.Combobox(self.frames["WhatsApp"], values=["", "11", "21", "31", "37"], state="readonly"); self.combo_whatsapp_estado.current(0); self.combo_whatsapp_estado.pack(anchor="w")
        tk.Label(self.frames["WhatsApp"], text="Número:").pack(anchor="w")
        self.entry_whatsapp_numero = tk.Entry(self.frames["WhatsApp"], width=WIDTH_SETTED); self.entry_whatsapp_numero.pack(anchor="w")
        tk.Label(self.frames["WhatsApp"], text="Mensagem:").pack(anchor="w")
        self.entry_whatsapp_texto = tk.Text(self.frames["WhatsApp"], width=WIDTH_SETTED, height=6); self.entry_whatsapp_texto.pack(anchor="w", pady=2)

        # Wi-Fi
        self.frames["Wi-Fi"] = tk.Frame(self.dynamic_container)
        tk.Label(self.frames["Wi-Fi"], text="Nome da Rede (SSID):").pack(anchor="w")
        self.entry_wifi_ssid = tk.Entry(self.frames["Wi-Fi"], width=WIDTH_SETTED); self.entry_wifi_ssid.pack(anchor="w")
        self.wifi_hidden_var = tk.IntVar()
        tk.Checkbutton(self.frames["Wi-Fi"], text="Rede Oculta", variable=self.wifi_hidden_var).pack(anchor="w")
        tk.Label(self.frames["Wi-Fi"], text="Senha da Rede:").pack(anchor="w")
        self.entry_wifi_senha = tk.Entry(self.frames["Wi-Fi"], width=WIDTH_SETTED); self.entry_wifi_senha.pack(anchor="w")
        tk.Label(self.frames["Wi-Fi"], text="Tipo de Segurança:").pack(anchor="w")
        self.combo_wifi_tipo = ttk.Combobox(self.frames["Wi-Fi"], values=["WPA/WPA2", "WEP", "Nenhuma"], state="readonly")
        self.combo_wifi_tipo.pack(anchor="w")

        # Seleciona um tipo padrão e exibe apenas ele no container
        self.combo_tipo.current(0)  # "URL"
        self.atualizar_campos()

        # Opções de exportação (fora do container, mantêm posição fixa abaixo)
        sep = ttk.Separator(self.scroll_frame, orient="horizontal"); sep.pack(fill="x", pady=8)
        tk.Label(self.scroll_frame, text="Formato de Saída:").pack(anchor="w")
        self.combo_formato = ttk.Combobox(self.scroll_frame, values=["PNG", "SVG"], state="readonly"); self.combo_formato.current(0); self.combo_formato.pack(fill="x")
        tk.Label(self.scroll_frame, text="Versão (1–40):").pack(anchor="w")
        self.entry_version = tk.Entry(self.scroll_frame); self.entry_version.insert(0, "6"); self.entry_version.pack(fill="x")
        tk.Label(self.scroll_frame, text="EC Level:").pack(anchor="w")
        self.combo_ec = ttk.Combobox(self.scroll_frame, values=["L","M","Q","H"], state="readonly"); self.combo_ec.current(3); self.combo_ec.pack(fill="x")
        tk.Label(self.scroll_frame, text="Box Size (PNG):").pack(anchor="w")
        self.entry_box_size = tk.Entry(self.scroll_frame); self.entry_box_size.insert(0, "10"); self.entry_box_size.pack(fill="x")
        tk.Label(self.scroll_frame, text="Borda (módulos):").pack(anchor="w")
        self.entry_border = tk.Entry(self.scroll_frame); self.entry_border.insert(0, "2"); self.entry_border.pack(fill="x")

        tk.Button(self.scroll_frame, text="Escolher arquivo de saída…", command=self.escolher_saida).pack(pady=6, fill="x")
        tk.Button(self.scroll_frame, text="Gerar QR Code", command=self.gerar_qr_code).pack(pady=6, fill="x")
        self.lbl_status = ttk.Label(self.scroll_frame, text="", foreground="blue"); self.lbl_status.pack()

        self.qr_frame = tk.Frame(self.scroll_frame, width=self.QRCODE_SIZE + 5, height=self.QRCODE_SIZE + 5, relief="sunken", borderwidth=2)
        self.qr_frame.pack(pady=8); self.qr_frame.pack_propagate(False)
        self.lbl_imagem = ttk.Label(self.qr_frame); self.lbl_imagem.pack(expand=True, fill="both")

    def _on_fill_changed(self, event=None):
        choice = self.combo_fill.get()
        if choice == "Imagem":
            self.btn_fill_image.grid()
        else:
            self.btn_fill_image.grid_remove()
            self.fill_image_path = None

    def selecionar_imagem_preenchimento(self):
        path = filedialog.askopenfilename(title="Imagem de Preenchimento", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if path:
            self.fill_image_path = path
            self.btn_fill_image.config(text=f"Imagem: {os.path.basename(path)}")

    def selecionar_fundo(self):
        path = filedialog.askopenfilename(title="Imagem de Fundo", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if path:
            self.bg_image_path = path

    def selecionar_cor_fg(self):
        cor = colorchooser.askcolor(title="Cor do QR Code")[1]
        if cor:
            self.viewmodel.set_fg_color(cor)

    def selecionar_cor_bg(self):
        cor = colorchooser.askcolor(title="Cor de Fundo")[1]
        if cor:
            self.viewmodel.set_bg_color(cor)

    def selecionar_cor_borda_logo(self):
        cor = colorchooser.askcolor(title="Cor da Borda da Logo")[1]
        if cor:
            self.logo_border_color = cor

    def selecionar_logo(self):
        path = filedialog.askopenfilename(title="Logo", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if path:
            self.viewmodel.set_logo(path)
            self.logo_path = path

    def escolher_saida(self):
        fmt = self.combo_formato.get().lower()
        default_ext = ".png" if fmt == "png" else ".svg"
        path = filedialog.asksaveasfilename(defaultextension=default_ext, filetypes=[("PNG", "*.png"), ("SVG", "*.svg")])
        if path:
            self.output_path = path

    def gerar_qr_code(self):
        self.lbl_status.config(text="Gerando QR Code...")

        tipo = self.combo_tipo.get()
        estilo = self.combo_estilo.get()
        incluir_logo = hasattr(self, "logo_var") and bool(self.logo_var.get())

        dados = ""
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
            dados = f"BEGIN:VCARD\\nFN:{self.entry_vcard_nome[0].get()}\\nTEL:{self.entry_vcard_telefone[0].get()}\\nEMAIL:{self.entry_vcard_email[0].get()}\\nURL:{self.entry_vcard_url[0].get()}\\nEND:VCARD"
        elif tipo == "Localização":
            dados = f"geo:{self.entry_latitude[0].get()},{self.entry_longitude[0].get()}"
        elif tipo == "WhatsApp":
            dados = f"https://wa.me/{self.combo_whatsapp_pais.get()}{self.combo_whatsapp_estado.get()}{self.entry_whatsapp_numero.get()}?text={self.entry_whatsapp_texto.get('1.0', tk.END).strip()}"
        elif tipo == "Wi-Fi":
            dados = f"WIFI:T:{self.combo_wifi_tipo.get()};S:{self.entry_wifi_ssid.get()};P:{self.entry_wifi_senha.get()};H:{getattr(self,'wifi_hidden_var',tk.IntVar()).get()};;"

        if not dados.strip():
            messagebox.showerror("Erro", "Preencha os campos necessários.")
            self.lbl_status.config(text=""); return

        try:
            version = int(self.entry_version.get() or "6")
            box_size = int(self.entry_box_size.get() or "10")
            border = int(self.entry_border.get() or "2")
            ec = self.combo_ec.get() or "H"
        except Exception as e:
            messagebox.showerror("Erro", f"Parâmetros inválidos: {e}")
            self.lbl_status.config(text=""); return

        fmt = self.combo_formato.get() or "PNG"
        if not self.output_path:
            self.output_path = f"qrcode.{fmt.lower()}"

        m = self.viewmodel.model
        m.set_output(self.output_path, fmt)
        m.set_size_params(box_size=box_size, border=border, version=version, ec_level=ec)
        if hasattr(self, "combo_olhos"):
            m.set_eye_style(self.combo_olhos.get())

        alpha = float(self.scale_bg_alpha.get()) / 100.0
        m.set_background_image(getattr(self, "bg_image_path", None), alpha=alpha)

        fill_choice = self.combo_fill.get()
        try:
            if fill_choice == "Sólido":
                m.set_fill_image(None); m.disable_gradient()
            elif fill_choice == "Gradiente Horizontal":
                m.set_fill_image(None); m.enable_linear_gradient(m.fg_color, m.bg_color, angle_deg=0.0)
            elif fill_choice == "Gradiente Vertical":
                m.set_fill_image(None); m.enable_linear_gradient(m.fg_color, m.bg_color, angle_deg=90.0)
            elif fill_choice == "Gradiente Radial":
                m.set_fill_image(None); m.enable_radial_gradient(m.fg_color, m.bg_color)
            elif fill_choice == "Imagem":
                m.set_fill_image(getattr(self, "fill_image_path", None))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no preenchimento: {e}")
            self.lbl_status.config(text=""); return

        try:
            m.set_logo_options(
                scale=int(getattr(self, "spin_logo_scale", tk.Spinbox()).get() or "5"),
                border_size=int(getattr(self, "spin_logo_border", tk.Spinbox()).get() or "8"),
                border_color=getattr(self, "logo_border_color", "#FFFFFF"),
                corner_radius=int(getattr(self, "spin_logo_radius", tk.Spinbox()).get() or "20"),
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Parâmetros da logo inválidos: {e}")
            self.lbl_status.config(text=""); return

        self.viewmodel.gerar_qr_code(dados, estilo, incluir_logo, self.atualizar_imagem)

    def atualizar_campos(self, event=None):
        tipo = self.combo_tipo.get()
        # Esconde todos os frames dinâmicos (apenas dentro do container dedicado)
        for frame in self.frames.values():
            frame.pack_forget()
        if tipo in self.frames:
            self.frames[tipo].pack(pady=5, anchor="w", fill="x")

    def atualizar_imagem(self, result):
        self.lbl_status.config(text="")
        img_path = result.get("path") if isinstance(result, dict) else result
        if not img_path or not os.path.exists(img_path):
            if str(self.output_path).lower().endswith(".svg"):
                messagebox.showinfo("Sucesso", f"QR Code SVG salvo em:\n{self.output_path}")
                return
            messagebox.showerror("Erro", "Arquivo de imagem não encontrado após a geração.")
            return
        img = Image.open(img_path).resize((self.QRCODE_SIZE, self.QRCODE_SIZE))
        img = ImageTk.PhotoImage(img)
        self.lbl_imagem.config(image=img)
        self.lbl_imagem.image = img
