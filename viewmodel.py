import threading
from model import QRCodeModel

class QRCodeViewModel:
    def __init__(self):
        self.model = QRCodeModel()

    def set_fg_color(self, color):
        self.model.fg_color = color

    def set_bg_color(self, color):
        self.model.bg_color = color

    def set_logo(self, path):
        self.model.logo_path = path

    def gerar_qr_code(self, dados, estilo, incluir_logo, callback):
        """Executa a geração do QR Code em uma thread separada"""
        def thread_target():
            img_path = self.model.gerar_qr_code(dados, estilo, incluir_logo)
            callback(img_path)
        threading.Thread(target=thread_target, daemon=True).start()
