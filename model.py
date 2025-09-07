# model.py — versão 3.0
from PIL import Image, ImageDraw, ImageFilter
import qrcode
from qrcode.constants import (
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
    ERROR_CORRECT_H,
)
from qrcode.image.pil import PilImage
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import (
    RoundedModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer,
)
from qrcode.image.svg import SvgPathImage

import math
import os
from typing import Tuple, Optional

def _hex_to_rgb_tuple(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def _create_linear_gradient(size: Tuple[int, int], start_rgb: Tuple[int, int, int], end_rgb: Tuple[int, int, int], angle_deg: float = 0.0) -> Image.Image:
    w, h = size
    base = Image.new("RGBA", (1, h), color=0)
    draw = ImageDraw.Draw(base)
    for y in range(h):
        t = y / (h - 1) if h > 1 else 0
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * t)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * t)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * t)
        draw.point((0, y), fill=(r, g, b, 255))
    gradient = base.resize((w, h), Image.NEAREST)
    if angle_deg % 360 == 0:
        return gradient
    gradient = gradient.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
    gw, gh = gradient.size
    left = (gw - w) // 2
    top = (gh - h) // 2
    return gradient.crop((left, top, left + w, top + h))

def _create_radial_gradient(size: Tuple[int, int], inner_rgb: Tuple[int, int, int], outer_rgb: Tuple[int, int, int]) -> Image.Image:
    w, h = size
    cx, cy = w / 2, h / 2
    max_dist = math.hypot(cx, cy)
    gradient = Image.new("RGBA", (w, h))
    px = gradient.load()
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            t = min(d / max_dist, 1.0)
            r = int(inner_rgb[0] + (outer_rgb[0] - inner_rgb[0]) * t)
            g = int(inner_rgb[1] + (outer_rgb[1] - inner_rgb[1]) * t)
            b = int(inner_rgb[2] + (outer_rgb[2] - inner_rgb[2]) * t)
            px[x, y] = (r, g, b, 255)
    return gradient

def _round_corners(im: Image.Image, radius: int) -> Image.Image:
    if radius <= 0:
        return im
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w, h)], radius=radius, fill=255)
    im_rounded = im.copy()
    im_rounded.putalpha(mask)
    return im_rounded

EC_MAP = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}

class QRCodeModel:
    def __init__(self, fg_color: str = "#000000", bg_color: str = "#FFFFFF", logo_path: str = ""):
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.logo_path = logo_path

        self.output_path = "qrcode.png"
        self.export_format = "PNG"
        self.box_size = 10
        self.border = 2
        self.version = 6
        self.error_correction = ERROR_CORRECT_H

        self.estilos_modulos = {
            "Padrão": None,
            "Quadrado": None,
            "Arredondado": RoundedModuleDrawer(),
            "Quadrados Espaçados": GappedSquareModuleDrawer(),
            "Círculos": CircleModuleDrawer(),
            "Barras Verticais": VerticalBarsDrawer(),
            "Barras Horizontais": HorizontalBarsDrawer(),
        }
        self.estilos_olhos = {
            "Padrão": None,
            "Quadrado": None,
            "Arredondado": RoundedModuleDrawer(),
            "Círculos": CircleModuleDrawer(),
        }

        self.use_gradient = False
        self.gradient_mode = "linear"
        self.gradient_start = "#000000"
        self.gradient_end = "#5555FF"
        self.gradient_angle = 0.0
        self.fill_image_path: Optional[str] = None

        self.background_image_path: Optional[str] = None
        self.background_alpha = 1.0

        self.image_scale_for_logo = 5
        self.logo_border_size = 8
        self.logo_border_color = "#FFFFFF"
        self.logo_corner_radius = 20

        self.eye_style_name = "Padrão"

    def set_output(self, path: str, export_format: str = "PNG"):
        self.output_path = path
        self.export_format = export_format.upper()

    def set_size_params(self, box_size: int = 10, border: int = 2, version: int = 6, ec_level: str = "H"):
        self.box_size = max(2, int(box_size))
        self.border = max(0, int(border))
        self.version = max(1, min(40, int(version)))
        self.error_correction = EC_MAP.get(ec_level.upper(), ERROR_CORRECT_H)

    def set_eye_style(self, name: str):
        self.eye_style_name = name if name in self.estilos_olhos else "Padrão"

    def set_logo_options(self, scale: int = 5, border_size: int = 8, border_color: str = "#FFFFFF", corner_radius: int = 20):
        self.image_scale_for_logo = max(2, scale)
        self.logo_border_size = max(0, border_size)
        self.logo_border_color = border_color
        self.logo_corner_radius = max(0, corner_radius)

    def enable_linear_gradient(self, start_color: str, end_color: str, angle_deg: float = 0.0):
        self.use_gradient = True
        self.gradient_mode = "linear"
        self.gradient_start = start_color
        self.gradient_end = end_color
        self.gradient_angle = angle_deg
        self.fill_image_path = None

    def enable_radial_gradient(self, inner_color: str, outer_color: str):
        self.use_gradient = True
        self.gradient_mode = "radial"
        self.gradient_start = inner_color
        self.gradient_end = outer_color
        self.fill_image_path = None

    def disable_gradient(self):
        self.use_gradient = False

    def set_fill_image(self, path: Optional[str]):
        self.fill_image_path = path
        self.use_gradient = False

    def set_background_image(self, path: Optional[str], alpha: float = 1.0):
        self.background_image_path = path
        self.background_alpha = float(max(0.0, min(1.0, alpha)))

    def _render_qr_gray(self, dados: str, module_drawer, eye_drawer) -> Image.Image:
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(dados)
        qr.make(fit=True)

        if module_drawer or eye_drawer:
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=module_drawer,
                eye_drawer=eye_drawer,
                color_mask=SolidFillColorMask(front_color=(0, 0, 0), back_color=(255, 255, 255)),
            ).convert("L")
        else:
            img = qr.make_image(
                image_factory=PilImage,
                fill_color=(0, 0, 0),
                back_color=(255, 255, 255),
            ).convert("L")
        return img

    def _make_modules_mask(self, gray_qr: Image.Image) -> Image.Image:
        inv = Image.eval(gray_qr, lambda p: 255 - p)
        return inv.point(lambda p: 255 if p > 40 else 0, mode="1").convert("L")

    def _apply_foreground_fill(self, size: Tuple[int, int], mask: Image.Image) -> Image.Image:
        w, h = size
        if self.fill_image_path and os.path.exists(self.fill_image_path):
            try:
                tex = Image.open(self.fill_image_path).convert("RGBA")
                ratio = max(w / tex.width, h / tex.height)
                new_size = (int(tex.width * ratio), int(tex.height * ratio))
                tex = tex.resize(new_size, Image.LANCZOS)
                left = (tex.width - w) // 2
                top = (tex.height - h) // 2
                tex = tex.crop((left, top, left + w, top + h))
                colored = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                colored.paste(tex, (0, 0), mask=mask)
                return colored
            except Exception as e:
                print(f"[Aviso] Imagem de preenchimento inválida: {e}")
        if self.use_gradient:
            start_rgb = _hex_to_rgb_tuple(self.gradient_start)
            end_rgb = _hex_to_rgb_tuple(self.gradient_end)
            grad = _create_radial_gradient((w, h), start_rgb, end_rgb) if self.gradient_mode == "radial" \
                   else _create_linear_gradient((w, h), start_rgb, end_rgb, self.gradient_angle)
            out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            out.paste(grad, (0, 0), mask=mask)
            return out
        fg = _hex_to_rgb_tuple(self.fg_color)
        out = Image.new("RGBA", (w, h), (*fg, 255))
        out.putalpha(mask)
        return out

    def _compose_background(self, size: Tuple[int, int]) -> Image.Image:
        w, h = size
        base = Image.new("RGBA", (w, h), (*_hex_to_rgb_tuple(self.bg_color), 255))
        if self.background_image_path and os.path.exists(self.background_image_path):
            try:
                bg = Image.open(self.background_image_path).convert("RGBA")
                ratio = max(w / bg.width, h / bg.height)
                new_size = (int(bg.width * ratio), int(bg.height * ratio))
                bg = bg.resize(new_size, Image.LANCZOS)
                left = (bg.width - w) // 2; top = (bg.height - h) // 2
                bg = bg.crop((left, top, left + w, top + h))
                if self.background_alpha < 1.0:
                    r, g, b, a = bg.split()
                    a = a.point(lambda p: int(p * self.background_alpha))
                    bg = Image.merge("RGBA", (r, g, b, a))
                base = bg
            except Exception as e:
                print(f"[Aviso] Fundo inválido: {e}")
        return base

    def _paste_logo(self, canvas: Image.Image) -> Image.Image:
        if not self.logo_path:
            return canvas
        try:
            logo = Image.open(self.logo_path).convert("RGBA")
        except Exception as e:
            print(f"[Aviso] Erro ao carregar logo: {e}"); return canvas
        w, h = canvas.size
        logo_size = (w // self.image_scale_for_logo, h // self.image_scale_for_logo)
        logo = logo.resize(logo_size, Image.LANCZOS); logo = _round_corners(logo, self.logo_corner_radius)
        if self.logo_border_size > 0:
            plate = Image.new("RGBA", (logo_size[0] + 2*self.logo_border_size, logo_size[1] + 2*self.logo_border_size),
                              _hex_to_rgb_tuple(self.logo_border_color) + (255,))
            plate = _round_corners(plate, self.logo_corner_radius + self.logo_border_size // 2)
            plate = plate.filter(ImageFilter.GaussianBlur(radius=0.5))
            plate_pos = ((w - plate.size[0]) // 2, (h - plate.size[1]) // 2)
            canvas.alpha_composite(plate, plate_pos)
        logo_pos = ((w - logo_size[0]) // 2, (h - logo_size[1]) // 2)
        canvas.alpha_composite(logo, logo_pos); return canvas

    def gerar_qr_code(self, dados: str, estilo: str, incluir_logo: bool) -> str:
        module_drawer = self.estilos_modulos.get(estilo, None)
        eye_drawer = self.estilos_olhos.get(self.eye_style_name, None)

        if self.export_format == "SVG":
            qr = qrcode.QRCode(version=self.version, error_correction=self.error_correction, box_size=self.box_size, border=self.border)
            qr.add_data(dados); qr.make(fit=True)
            img = qr.make_image(image_factory=SvgPathImage, fill_color=self.fg_color, back_color=self.bg_color)
            img.save(self.output_path)
            return self.output_path

        gray_qr = self._render_qr_gray(dados, module_drawer, eye_drawer)
        mask = self._make_modules_mask(gray_qr)
        colored_qr = self._apply_foreground_fill(gray_qr.size, mask)
        base = self._compose_background(colored_qr.size)
        base.alpha_composite(colored_qr)
        if incluir_logo and self.logo_path:
            base = self._paste_logo(base)
        base.save(self.output_path)
        return self.output_path
