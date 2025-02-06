from PIL import Image
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.pil import PilImage
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import (
    RoundedModuleDrawer, 
    GappedSquareModuleDrawer, 
    CircleModuleDrawer, 
    VerticalBarsDrawer, 
    HorizontalBarsDrawer
)

class QRCodeModel:
    def __init__(self, fg_color="#000000", bg_color="#FFFFFF", logo_path=""):
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.logo_path = logo_path

    def gerar_qr_code(self, dados, estilo, incluir_logo):
        """Gera o QR Code e retorna o caminho da imagem gerada"""
        estilos_modulos = {
            "Padrão": None,
            "Arredondado": RoundedModuleDrawer(),
            "Quadrados Espaçados": GappedSquareModuleDrawer(),
            "Círculos": CircleModuleDrawer(),
            "Barras Verticais": VerticalBarsDrawer(),
            "Barras Horizontais": HorizontalBarsDrawer(),
        }
        module_drawer = estilos_modulos.get(estilo, None)

        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        fg_rgb = hex_to_rgb(self.fg_color)
        bg_rgb = hex_to_rgb(self.bg_color)

        qr = qrcode.QRCode(
            version=6,
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(dados)
        qr.make(fit=True)

        if module_drawer:
            qr_img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=module_drawer,
                color_mask=SolidFillColorMask(front_color=fg_rgb, back_color=bg_rgb)
            ).convert("RGBA")
        else:
            qr_img = qr.make_image(
                image_factory=PilImage,
                fill_color=self.fg_color,
                back_color=self.bg_color
            ).convert("RGBA")

        if incluir_logo and self.logo_path:
            try:
                logo = Image.open(self.logo_path).convert("RGBA")
                logo_size = (qr_img.size[0] // 5, qr_img.size[1] // 5)
                logo = logo.resize(logo_size, Image.LANCZOS)

                qr_with_logo = qr_img.copy()
                logo_x = (qr_with_logo.size[0] - logo_size[0]) // 2
                logo_y = (qr_with_logo.size[1] - logo_size[1]) // 2
                qr_with_logo.paste(logo, (logo_x, logo_y), mask=logo)
            except Exception as e:
                print(f"Erro ao carregar logo: {e}")
                qr_with_logo = qr_img
        else:
            qr_with_logo = qr_img

        qr_with_logo.save("qrcode.png")
        return "qrcode.png"
