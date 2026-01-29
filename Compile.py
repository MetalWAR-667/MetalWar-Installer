#!/usr/bin/env python3
# compilador.py
# Herramienta de consola para compilar MetalWar con PyInstaller
# VERSIÓN CON AJUSTE AUTOMÁTICO DE TEXTO EN SPLASH

import os
import sys
import re
import json
import ast
import shutil
import time
import platform
import subprocess
import threading
import random
import math
from pathlib import Path
import glob


# Códigos de colores ANSI
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

    # Colores personalizados
    SUCCESS = GREEN
    ERROR = RED
    WARNING = YELLOW
    INFO = CYAN
    TITLE = MAGENTA + BOLD
    OPTION = BLUE
    FIELD = GREEN
    VALUE = YELLOW


def print_color(text, color=Colors.RESET, end="\n"):
    """Imprime texto con color"""
    print(f"{color}{text}{Colors.RESET}", end=end)


def print_header(title):
    """Imprime un encabezado con estilo"""
    print_color("\n" + "=" * 60, Colors.TITLE)
    print_color(title.center(60), Colors.TITLE)
    print_color("=" * 60, Colors.TITLE)


def print_success(msg):
    """Imprime un mensaje de éxito"""
    print_color(f"✓ {msg}", Colors.SUCCESS)


def print_error(msg):
    """Imprime un mensaje de error"""
    print_color(f"✗ {msg}", Colors.ERROR)


def print_warning(msg):
    """Imprime un mensaje de advertencia"""
    print_color(f"⚠ {msg}", Colors.WARNING)


def print_info(msg):
    """Imprime un mensaje informativo"""
    print_color(f"ℹ {msg}", Colors.INFO)


# ============================================================================
# CLASE DEMOSCENE FACTORY ORIGINAL (TODAS TUS FUNCIONES)
# ============================================================================

import random
import math
import time
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageChops,
    ImageEnhance,
    ImageOps,
)


class DemosceneFactory:
    """
    FACTORY DE ARTE DEMOSCENE PROCEDURAL
    ------------------------------------
    Genera splash screens únicos basados en algoritmos de la vieja escuela (1985-1999)
    actualizados con técnicas de post-procesado moderno.
    """

    def __init__(self, width=600, height=400):
        self.w = width
        self.h = height
        self.center = (width // 2, height // 2)
        random.seed(time.time())

    def _get_font(self, size, style="bold"):
        font_candidates = [
            "Impact.ttf",
            "Arial Black.ttf",
            "Verdana.ttf",
            "Tahoma.ttf",
            "DejaVuSans-Bold.ttf",
            "FreeSansBold.ttf",
            "Helvetica-Bold.ttf",
            "Arial.ttf",
        ]

        for font_name in font_candidates:
            try:
                return ImageFont.truetype(font_name, size)
            except IOError:
                continue
        return ImageFont.load_default()

    def _random_palette(self):
        modes = ["fire", "ice", "toxic", "royal", "alien", "candy"]
        mode = random.choice(modes)

        palette = []
        for i in range(256):
            if mode == "fire":
                r = min(255, i * 2)
                g = min(255, i)
                b = 0
            elif mode == "ice":
                r = int(i / 4)
                g = min(255, i + 50)
                b = min(255, i * 2 + 50)
            elif mode == "toxic":
                r = int(128 + 127 * math.sin(i * math.pi / 32))
                g = 255
                b = int(128 + 127 * math.cos(i * math.pi / 32))
            elif mode == "royal":
                r = min(255, i * 2)
                g = min(255, i // 2)
                b = min(255, i + 50)
            elif mode == "alien":
                r = 0
                g = int(128 + 127 * math.sin(i * 0.1))
                b = int(128 + 127 * math.cos(i * 0.1))
            else:  # Candy
                r = int(128 + 127 * math.sin(i * 0.05))
                g = int(128 + 127 * math.sin(i * 0.05 + 2))
                b = int(128 + 127 * math.sin(i * 0.05 + 4))
            palette.append((r, g, b))
        return palette

    def _apply_crt_effect(self, img):
        # Scanlines
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        step = 3
        for y in range(0, img.height, step):
            draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, 80), width=1)

        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

        # RGB Shift
        r, g, b = img.split()
        r = ImageChops.offset(r, -3, 0)
        b = ImageChops.offset(b, 3, 0)
        img = Image.merge("RGB", (r, g, b))

        # Bloom
        glow = img.filter(ImageFilter.GaussianBlur(12))
        img = ImageChops.screen(img, ImageEnhance.Brightness(glow).enhance(1.3))

        # Vignette
        vignette = Image.new("L", img.size, 255)
        draw_v = ImageDraw.Draw(vignette)
        draw_v.ellipse((50, 50, img.width - 50, img.height - 50), fill=0)
        vignette = vignette.filter(ImageFilter.GaussianBlur(100))
        img = Image.composite(Image.new("RGB", img.size, (0, 0, 0)), img, vignette)

        return img

    def _generate_chrome_text(self, text, size=80):
        # Ajuste de tamaño automático
        font_test = self._get_font(size)
        draw_test = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        bbox_test = draw_test.textbbox((0, 0), text, font=font_test)
        text_width = bbox_test[2] - bbox_test[0]

        max_width = self.w * 0.85
        if text_width > max_width:
            size = int(size * (max_width / text_width))
            size = max(40, size)

        font = self._get_font(size)

        # Máscara del texto
        mask = Image.new("L", (self.w, self.h), 0)
        draw_m = ImageDraw.Draw(mask)
        bbox = draw_m.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx, ty = (self.w - tw) // 2, (self.h - th) // 2
        draw_m.text((tx, ty), text, font=font, fill=255)

        # Gradiente metálico
        gradient = Image.new("RGB", (self.w, self.h), (0, 0, 0))
        draw_g = ImageDraw.Draw(gradient)

        horizon = ty + th // 2 + random.randint(-10, 10)

        sky_color_top = (0, 0, 100)
        sky_color_bot = (150, 200, 255)
        gnd_color_top = (50, 30, 0)
        gnd_color_bot = (255, 215, 0)

        for y in range(ty, ty + th):
            if y < horizon:
                ratio = (y - ty) / (horizon - ty) if horizon > ty else 0
                r = int(sky_color_top[0] * (1 - ratio) + sky_color_bot[0] * ratio)
                g = int(sky_color_top[1] * (1 - ratio) + sky_color_bot[1] * ratio)
                b = int(sky_color_top[2] * (1 - ratio) + sky_color_bot[2] * ratio)
            else:
                ratio = (
                    (y - horizon) / (ty + th - horizon) if (ty + th) > horizon else 0
                )
                r = int(gnd_color_bot[0] * ratio + gnd_color_top[0] * (1 - ratio))
                g = int(gnd_color_bot[1] * ratio + gnd_color_top[1] * (1 - ratio))
                b = int(gnd_color_bot[2] * ratio + gnd_color_top[2] * (1 - ratio))
            draw_g.line([(tx, y), (tx + tw, y)], fill=(r, g, b))

        # Componer texto
        chrome = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        chrome.paste(gradient, (0, 0), mask)

        # Borde brillante
        edge = mask.filter(ImageFilter.FIND_EDGES)
        edge = ImageEnhance.Brightness(edge).enhance(10.0)
        edge_layer = ImageOps.colorize(edge, black="black", white="white")

        # Sombra
        shadow = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        draw_s = ImageDraw.Draw(shadow)
        shadow_offset = max(3, size // 25)
        draw_s.text(
            (tx + shadow_offset, ty + shadow_offset),
            text,
            font=font,
            fill=(0, 0, 0, 180),
        )

        # Componer
        final = Image.alpha_composite(shadow, chrome)
        final.paste(edge_layer, (0, 0), edge)

        return final

    def generar_plasma(self, title, subtitle="Loading Resources..."):
        print_color("   ⚡ Tema: PLASMA CORE (Matemática procedural)", Colors.CYAN)

        palette = self._random_palette()
        c1 = random.randint(10, 80)
        c2 = random.randint(10, 80)
        c3 = random.randint(10, 80)
        c4 = random.choice([5, 10, 20, 50])
        offset = random.randint(0, 1000)

        low_w, low_h = 240, 135
        plasma = Image.new("RGB", (low_w, low_h))
        pixels = plasma.load()

        for y in range(low_h):
            for x in range(low_w):
                v1 = math.sin(x / c1 + offset)
                v2 = math.sin(y / c2 + offset)
                v3 = math.sin((x + y) / c3 + offset)
                v4 = math.sin(math.sqrt(x**2 + y**2) / c4)
                val = (v1 + v2 + v3 + v4) * 64 + 128
                pixels[x, y] = palette[int(val) % 256]

        bg = plasma.resize((self.w, self.h), Image.Resampling.BILINEAR)
        bg = ImageEnhance.Brightness(bg).enhance(0.7)

        chrome = self._generate_chrome_text(title, size=70)
        bg.paste(chrome, (0, 0), chrome)

        draw = ImageDraw.Draw(bg)
        font_s = self._get_font(18)
        t_w = draw.textbbox((0, 0), subtitle, font=font_s)[2]
        draw.text(
            ((self.w - t_w) // 2, self.h - 40),
            subtitle,
            font=font_s,
            fill=(255, 255, 0),
        )

        return self._apply_crt_effect(bg)

    def generar_copper(self, title, subtitle="Initializing System..."):
        print_color("   ⚡ Tema: COPPER BARS (Estilo Amiga/C64)", Colors.MAGENTA)

        bg_col = (random.randint(0, 20), random.randint(0, 20), random.randint(0, 30))
        bg = Image.new("RGB", (self.w, self.h), bg_col)
        draw = ImageDraw.Draw(bg)

        if random.random() > 0.5:
            step = random.randint(30, 60)
            for x in range(0, self.w, step):
                draw.line([(x, 0), (x, self.h)], fill=(40, 40, 60))
        else:
            step = random.randint(30, 60)
            for y in range(0, self.h, step):
                draw.line([(0, y), (self.w, y)], fill=(40, 40, 60))

        num_bars = random.randint(4, 8)
        amplitude = random.randint(20, 60)
        freq = random.uniform(0.5, 3.0)
        phase_shift = random.uniform(0, 3.14)

        r_base = random.choice([0, 1])
        g_base = random.choice([0, 1])
        b_base = random.choice([0, 1])
        if r_base + g_base + b_base == 0:
            r_base = 1

        for i in range(num_bars):
            base_y = (self.h // (num_bars + 1)) * (i + 1)
            bar_height = random.randint(20, 40)
            for h in range(bar_height):
                dist = abs(h - bar_height // 2)
                intensity = max(0, 255 - (dist * 255 // (bar_height // 2)))
                col = (intensity * r_base, intensity * g_base, intensity * b_base)
                y_wave = base_y + int(
                    math.sin(i * 0.5 + freq + phase_shift) * amplitude
                )
                draw.line([(0, y_wave + h), (self.w, y_wave + h)], fill=col)

        # Texto
        font_test = self._get_font(80)
        draw_test = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        bbox = draw_test.textbbox((0, 0), title, font=font_test)
        text_width = bbox[2] - bbox[0]

        max_width = self.w * 0.9
        if text_width > max_width:
            new_size = int(80 * (max_width / text_width))
            new_size = max(50, new_size)
            font = self._get_font(new_size)
        else:
            font = self._get_font(80)

        bbox = draw.textbbox((0, 0), title, font=font)
        tw = bbox[2] - bbox[0]
        tx, ty = (self.w - tw) // 2, (self.h) // 2 - 50

        draw.text((tx + 5, ty + 5), title, font=font, fill=(0, 0, 0))
        draw.text((tx, ty), title, font=font, fill=(255, 255, 255))

        font_s = self._get_font(16)
        st_w = draw.textbbox((0, 0), subtitle, font=font_s)[2]
        draw.text(
            ((self.w - st_w) // 2, self.h - 30), subtitle, font=font_s, fill=(0, 255, 0)
        )

        return self._apply_crt_effect(bg)

    def generar_synthwave(self, title, subtitle="Booting System..."):
        print_color("   ⚡ Tema: SYNTHWAVE GRID (Neón 80s)", Colors.GREEN)

        themes = [
            {"sky": (15, 0, 30), "sun": (255, 0, 128), "grid": (0, 255, 255)},
            {"sky": (0, 10, 20), "sun": (255, 200, 0), "grid": (255, 0, 128)},
            {"sky": (5, 5, 5), "sun": (255, 255, 255), "grid": (0, 255, 0)},
            {"sky": (30, 0, 0), "sun": (255, 255, 0), "grid": (255, 50, 0)},
        ]
        theme = random.choice(themes)

        bg = Image.new("RGB", (self.w, self.h), theme["sky"])
        draw = ImageDraw.Draw(bg)

        # Sol
        sun_r = random.randint(80, 120)
        sun_x = self.w // 2
        sun_y = self.h // 2 - 30

        sr, sg, sb = theme["sun"]
        for r in range(sun_r, 0, -1):
            ratio = r / sun_r
            cr = int(sr * ratio + 255 * (1 - ratio))
            cg = int(sg * ratio + 255 * (1 - ratio))
            cb = int(sb * ratio + 255 * (1 - ratio))
            draw.ellipse(
                (sun_x - r, sun_y - r, sun_x + r, sun_y + r), fill=(cr, cg, cb)
            )

        cut_start = sun_y
        cut_height = 3
        cut_gap = 8
        while cut_start < sun_y + sun_r:
            draw.rectangle(
                (sun_x - sun_r, cut_start, sun_x + sun_r, cut_start + cut_height),
                fill=theme["sky"],
            )
            cut_start += cut_gap
            cut_gap += 1
            cut_height += 1

        # Grid
        horizon = sun_y + sun_r // 2 + 20

        step_x = random.randint(40, 80)
        for x in range(-self.w, self.w * 2, step_x):
            draw.line(
                [(x, self.h), (self.w // 2, horizon)], fill=theme["grid"], width=1
            )

        y = horizon
        dist = 2
        accel = 1.2
        while y < self.h:
            draw.line([(0, int(y)), (self.w, int(y))], fill=theme["grid"], width=1)
            y += dist
            dist *= accel

        # Estrellas
        for _ in range(50):
            sx = random.randint(0, self.w)
            sy = random.randint(0, horizon)
            if math.hypot(sx - sun_x, sy - sun_y) > sun_r + 5:
                draw.point((sx, sy), fill=(255, 255, 255))

        bg = bg.filter(ImageFilter.GaussianBlur(1))

        # Texto Chrome
        chrome = self._generate_chrome_text(title, size=70)
        bg.paste(chrome, (0, 0), chrome)

        # Subtítulo
        font_s = self._get_font(18)
        st_bbox = draw.textbbox((0, 0), subtitle, font=font_s)
        st_w = st_bbox[2] - st_bbox[0]
        st_x = (self.w - st_w) // 2
        st_y = self.h - 50

        draw.text((st_x + 2, st_y + 2), subtitle, font=font_s, fill=(0, 0, 0, 180))
        draw.text((st_x, st_y), subtitle, font=font_s, fill=(255, 255, 0))

        return self._apply_crt_effect(bg)


# ============================================================================
# GENERADORES DE SPLASH SIMPLIFICADOS (CON AJUSTE AUTOMÁTICO DE TEXTO)
# ============================================================================


def obtener_nombre_producto():
    """Obtiene el nombre del producto desde version_info.txt"""
    product_name = "METALWAR"
    if Path("version_info.txt").exists():
        try:
            with open("version_info.txt", "r", encoding="utf-8") as f:
                content = f.read()
            product_match = re.search(r"'ProductName', '([^']*)'", content)
            if product_match:
                product_name = product_match.group(1).upper()
        except:
            pass
    return product_name


def ajustar_fuente_auto(
    draw, texto, ancho_maximo, fuente_base="arialbd.ttf", tamaño_inicial=48
):
    """
    Ajusta automáticamente el tamaño de fuente para que el texto quepa en el ancho máximo

    Args:
        draw: objeto ImageDraw
        texto: texto a renderizar
        ancho_maximo: ancho máximo permitido (píxeles)
        fuente_base: nombre de la fuente
        tamaño_inicial: tamaño inicial a probar

    Returns:
        tupla: (font_object, font_size)
    """
    # Intentar con diferentes tamaños
    for size in range(tamaño_inicial, 20, -2):
        try:
            font = ImageFont.truetype(fuente_base, size)
        except:
            try:
                # Intentar con fuente por defecto si no encuentra la específica
                font = ImageFont.truetype("arial.ttf", size)
            except:
                # Último recurso: fuente por defecto del sistema
                font = ImageFont.load_default()
                return font, size

        # Calcular ancho del texto
        bbox = draw.textbbox((0, 0), texto, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= ancho_maximo:
            return font, size

    # Si no cabe ni con tamaño 20, usar tamaño mínimo y fuente por defecto
    return ImageFont.load_default(), 20


def dibujar_barra_progreso(draw, x, y, width, height, progress, color):
    """Dibuja una barra de progreso animada"""
    # Fondo de la barra
    draw.rectangle([x, y, x + width, y + height], outline=color, width=2)

    # Progreso animado
    anim_offset = int((time.time() * 10) % width)
    progress_width = min(width * 0.8, anim_offset)

    # Relleno de progreso
    if progress_width > 10:
        draw.rectangle(
            [x + 5, y + 3, x + 5 + progress_width, y + height - 3], fill=color
        )

    # Puntos animados
    dot_spacing = 15
    for i in range(0, width - 20, dot_spacing):
        dot_pos = (i + anim_offset) % (width - 20)
        draw.ellipse(
            [
                x + 10 + dot_pos,
                y + height // 2 - 2,
                x + 10 + dot_pos + 4,
                y + height // 2 + 2,
            ],
            fill=color,
        )


def generar_splash_lite():
    """Generador 1: Minimalista CON AJUSTE AUTOMÁTICO"""
    try:
        width, height = 600, 400
        img = Image.new("RGB", (width, height), color="black")
        draw = ImageDraw.Draw(img)

        product_name = obtener_nombre_producto()

        # Título - CON AJUSTE AUTOMÁTICO
        max_width = width * 0.85  # 85% del ancho de pantalla
        font, font_size = ajustar_fuente_auto(
            draw, product_name, max_width, "arialbd.ttf", 48
        )

        title_bbox = draw.textbbox((0, 0), product_name, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 80), product_name, font=font, fill="white")

        # Barra de progreso
        bar_x, bar_y = 100, 200
        bar_width, bar_height = 400, 20
        dibujar_barra_progreso(draw, bar_x, bar_y, bar_width, bar_height, 0.7, "white")

        # Texto PLEASE WAIT - TAMBIÉN CON AJUSTE
        wait_text = "PLEASE WAIT..."
        small_font, small_size = ajustar_fuente_auto(
            draw, wait_text, width * 0.5, "arial.ttf", 18
        )

        wait_bbox = draw.textbbox((0, 0), wait_text, font=small_font)
        wait_width = wait_bbox[2] - wait_bbox[0]
        wait_x = (width - wait_width) // 2
        draw.text((wait_x, 280), wait_text, font=small_font, fill="gray")

        img.save("splash.png", "PNG", optimize=True)
        print_success("Splash Lite generado (con ajuste automático)")
        return True

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def Industrial_muthafuckaed():
    """Generador 2: Industrial Cyberpunk CON AJUSTE AUTOMÁTICO"""
    try:
        width, height = 600, 400
        img = Image.new("RGB", (width, height), color=(5, 5, 10))
        draw = ImageDraw.Draw(img)

        product_name = obtener_nombre_producto()

        # Fondo con líneas
        for i in range(8):
            start_x = random.randint(0, width)
            start_y = random.randint(0, height)
            for j in range(4):
                end_x = random.randint(0, width)
                end_y = random.randint(0, height)
                draw.line(
                    [(start_x, start_y), (end_x, end_y)], fill=(0, 150, 200), width=1
                )

        # Título - CON AJUSTE AUTOMÁTICO
        max_width = width * 0.85  # 85% del ancho de pantalla
        font, font_size = ajustar_fuente_auto(
            draw, product_name, max_width, "arialbd.ttf", 48
        )

        title_bbox = draw.textbbox((0, 0), product_name, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2

        draw.text((title_x + 2, 82), product_name, font=font, fill=(255, 0, 255))
        draw.text((title_x, 80), product_name, font=font, fill=(0, 255, 255))

        # Barra de progreso
        bar_x, bar_y = 100, 200
        bar_width, bar_height = 400, 20
        dibujar_barra_progreso(
            draw, bar_x, bar_y, bar_width, bar_height, 0.7, (0, 255, 255)
        )

        # Texto PLEASE WAIT - TAMBIÉN CON AJUSTE
        wait_text = "PLEASE WAIT..."
        small_font, small_size = ajustar_fuente_auto(
            draw, wait_text, width * 0.5, "arial.ttf", 18
        )

        wait_bbox = draw.textbbox((0, 0), wait_text, font=small_font)
        wait_width = wait_bbox[2] - wait_bbox[0]
        wait_x = (width - wait_width) // 2

        draw.text((wait_x + 1, 282), wait_text, font=small_font, fill=(255, 0, 255))
        draw.text((wait_x, 280), wait_text, font=small_font, fill=(0, 255, 255))

        img.save("splash.png", "PNG", optimize=True)
        print_success("Splash Industrial generado (con ajuste automático)")
        return True

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def generar_splash_brutal():
    """Generador 3: Heavy Metal CON AJUSTE AUTOMÁTICO"""
    try:
        width, height = 600, 400
        img = Image.new("RGB", (width, height), color="black")
        draw = ImageDraw.Draw(img)

        product_name = obtener_nombre_producto()

        # Rayos
        for i in range(15):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(-100, 100)
            y2 = y1 + random.randint(-100, 100)
            draw.line([(x1, y1), (x2, y2)], fill="darkred", width=2)

        # Título - CON AJUSTE AUTOMÁTICO
        max_width = width * 0.85  # 85% del ancho de pantalla
        font, font_size = ajustar_fuente_auto(
            draw, product_name, max_width, "arialbd.ttf", 52
        )

        title_bbox = draw.textbbox((0, 0), product_name, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2

        for offset in range(3, 0, -1):
            draw.text(
                (title_x + offset, 60 + offset), product_name, font=font, fill="darkred"
            )

        draw.text((title_x, 60), product_name, font=font, fill="gold")

        # Barra de progreso
        bar_x, bar_y = 100, 200
        bar_width, bar_height = 400, 20
        dibujar_barra_progreso(draw, bar_x, bar_y, bar_width, bar_height, 0.7, "gold")

        # Texto PLEASE WAIT - TAMBIÉN CON AJUSTE
        wait_text = "PLEASE WAIT..."
        small_font, small_size = ajustar_fuente_auto(
            draw, wait_text, width * 0.5, "arial.ttf", 18
        )

        wait_bbox = draw.textbbox((0, 0), wait_text, font=small_font)
        wait_width = wait_bbox[2] - wait_bbox[0]
        wait_x = (width - wait_width) // 2

        draw.text((wait_x + 2, 282), wait_text, font=small_font, fill="darkred")
        draw.text((wait_x, 280), wait_text, font=small_font, fill="gold")

        img.save("splash.png", "PNG", optimize=True)
        print_success("Splash Brutal generado (con ajuste automático)")
        return True

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def generar_splash_random_madness():
    """Generador 4: Random Madness CON AJUSTE AUTOMÁTICO"""
    try:
        width, height = 600, 400

        themes = ["cyber", "retro", "abstract"]
        theme = random.choice(themes)

        if theme == "cyber":
            bg_color = (
                random.randint(0, 30),
                random.randint(0, 30),
                random.randint(30, 60),
            )
        elif theme == "retro":
            bg_color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        else:
            bg_color = "black"

        img = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

        product_name = obtener_nombre_producto()

        # Título - CON AJUSTE AUTOMÁTICO
        max_width = width * 0.85  # 85% del ancho de pantalla
        font_sizes = [42, 48, 52]
        font_size = random.choice(font_sizes)

        font, actual_size = ajustar_fuente_auto(
            draw, product_name, max_width, "arialbd.ttf", font_size
        )

        title_bbox = draw.textbbox((0, 0), product_name, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2

        title_color = (
            random.randint(150, 255),
            random.randint(150, 255),
            random.randint(150, 255),
        )
        draw.text((title_x, 60), product_name, font=font, fill=title_color)

        # Barra de progreso
        bar_x, bar_y = 100, 200
        bar_width, bar_height = 400, 20

        bar_color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        )
        draw.rectangle(
            [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
            outline=bar_color,
            width=2,
        )

        anim_pos = int((time.time() * 8) % bar_width)
        if anim_pos > 20:
            draw.rectangle(
                [bar_x + 5, bar_y + 3, bar_x + 5 + anim_pos, bar_y + bar_height - 3],
                fill=bar_color,
            )

        # Texto PLEASE WAIT - TAMBIÉN CON AJUSTE
        wait_text = "PLEASE WAIT..."
        small_font, small_size = ajustar_fuente_auto(
            draw, wait_text, width * 0.5, "arial.ttf", 18
        )

        wait_bbox = draw.textbbox((0, 0), wait_text, font=small_font)
        wait_width = wait_bbox[2] - wait_bbox[0]
        wait_x = (width - wait_width) // 2

        wait_color = (
            random.randint(150, 255),
            random.randint(150, 255),
            random.randint(150, 255),
        )
        draw.text((wait_x, 280), wait_text, font=small_font, fill=wait_color)

        img.save("splash.png", "PNG", optimize=True)
        print_success(f"Splash Random ({theme}) generado (con ajuste automático)")
        return True

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def generar_splash_pixel_terror():
    """Generador 5: Pixel Terror CON AJUSTE AUTOMÁTICO"""
    try:
        width, height = 600, 400
        small_w, small_h = width // 2, height // 2

        img_small = Image.new("RGB", (small_w, small_h), color="black")
        draw_small = ImageDraw.Draw(img_small)

        product_name = obtener_nombre_producto()

        # Píxeles aleatorios
        for i in range(500):
            x = random.randint(0, small_w - 1)
            y = random.randint(0, small_h - 1)
            if random.random() > 0.5:
                color = (random.randint(100, 200), 0, 0)
            else:
                color = (
                    random.randint(50, 100),
                    random.randint(50, 100),
                    random.randint(50, 100),
                )
            draw_small.point((x, y), fill=color)

        # Escalar
        img = img_small.resize((width, height), Image.NEAREST)
        draw = ImageDraw.Draw(img)

        # Título - CON AJUSTE AUTOMÁTICO
        max_width = width * 0.85  # 85% del ancho de pantalla
        font, font_size = ajustar_fuente_auto(
            draw, product_name, max_width, "arial.ttf", 36
        )

        title_bbox = draw.textbbox((0, 0), product_name, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2

        for offset in range(3, 0, -1):
            draw.text(
                (title_x + offset, 60 + offset),
                product_name,
                font=font,
                fill=(50, 0, 0),
            )
        draw.text((title_x, 60), product_name, font=font, fill=(200, 0, 0))

        # Barra de progreso
        bar_x, bar_y = 100, 200
        bar_width, bar_height = 400, 20

        draw.rectangle(
            [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=(30, 30, 30)
        )

        anim_pos = int((time.time() * 6) % bar_width)
        if anim_pos > 30:
            for i in range(0, anim_pos, 10):
                block_width = min(8, anim_pos - i)
                draw.rectangle(
                    [
                        bar_x + 5 + i,
                        bar_y + 5,
                        bar_x + 5 + i + block_width,
                        bar_y + bar_height - 5,
                    ],
                    fill=(200, 0, 0),
                )

        # Texto PLEASE WAIT - TAMBIÉN CON AJUSTE
        wait_text = "PLEASE WAIT..."
        small_font, small_size = ajustar_fuente_auto(
            draw, wait_text, width * 0.5, "arial.ttf", 14
        )

        wait_bbox = draw.textbbox((0, 0), wait_text, font=small_font)
        wait_width = wait_bbox[2] - wait_bbox[0]
        wait_x = (width - wait_width) // 2

        for offset in range(2, 0, -1):
            draw.text(
                (wait_x + offset, 282 + offset),
                wait_text,
                font=small_font,
                fill=(50, 0, 0),
            )
        draw.text((wait_x, 280), wait_text, font=small_font, fill=(150, 150, 150))

        img.save("splash.png", "PNG", optimize=True)
        print_success("Splash Pixel generado (con ajuste automático)")
        return True

    except Exception as e:
        print_error(f"Error: {e}")
        return False


# ============================================================================
# TODAS TUS FUNCIONES ORIGINALES (SIN MODIFICAR)
# ============================================================================


def guardar_config(config):
    """Guarda la configuración en config.py con TODAS las claves necesarias"""
    try:
        # Crear backup
        if Path("config.py").exists():
            shutil.copy2("config.py", "config.py.backup")

        # Asegurar que todas las claves necesarias existan
        config_completo = {
            # Información básica - CLAVES COMPLETAS
            "GAME_FOLDER_NAME": config.get("GAME_FOLDER_NAME", "CARPETA DEL JUEGO"),
            "GAME_NAME_DISPLAY": config.get("GAME_NAME_DISPLAY", "TITULO DEL JUEGO"),
            "WINDOW_CAPTION": config.get("WINDOW_CAPTION", "MetalWar - Instalador"),
            "SCROLLER_MESSAGE": config.get(
                "SCROLLER_MESSAGE", ">>> METALWAR LOADING... SYSTEM INITIALIZED >>>"
            ),
            "SUBTITLE_DISPLAY": config.get("SUBTITLE_DISPLAY", ""),
            "SPANISH_TEXT": config.get("SPANISH_TEXT", "In Awesome Spanish"),
            # Configuración de ventana
            "WINDOW_SIZE": config.get("WINDOW_SIZE", (800, 600)),
            "FPS": config.get("FPS", 60),
            "IDLE_TIMEOUT": config.get("IDLE_TIMEOUT", 20.0),
            # Post-instalación
            "POST_INSTALL": config.get(
                "POST_INSTALL",
                {
                    "ENABLED": False,
                    "PATCHER_EXE": "example.exe",
                    "TARGET_FILE": "catalog.json",
                    "ARGUMENT": "patchcrc",
                },
            ),
            # Colores - CON TODAS LAS CLAVES NECESARIAS
            "COLORS": config.get(
                "COLORS",
                {
                    "BLACK": (10, 10, 18),
                    "WHITE": (255, 255, 255),
                    "BLUE_NEON": (0, 255, 255),
                    "RED_ALERT": (255, 0, 0),
                    "CYAN_NEON": (0, 255, 200),
                    "PEACE_GREEN": (50, 255, 100),
                    "BUTTON_GRAY": (40, 40, 50),
                    "BUTTON_HOVER": (60, 60, 75),
                    "GREEN_SUCCESS": (50, 220, 50),
                    "LIGHT_TEXT": (135, 206, 250),
                    "HUD_BG": (0, 0, 0, 180),
                    # Añadir claves para SPAIN_TEXT si faltan
                    "SPAIN_TEXT": config.get("COLORS", {}).get(
                        "SPAIN_TEXT",
                        {
                            "SPANISH_TEXT_SCALE": 1.5,
                            "SUBTITLE_SCALE": 1.2,
                            "FLAG_RED": (255, 0, 0),
                            "FLAG_YELLOW": (255, 215, 0),
                            "FLAG_YELLOW_2": (255, 200, 0),
                            "TEXT_WHITE": (255, 255, 255),
                            "TEXT_CYAN": (0, 255, 255),
                            "TEXT_GREEN": (0, 255, 0),
                            "SHINE_COLOR": (255, 255, 200),
                            "GLOW_COLOR": (255, 255, 100),
                            "OUTLINE_COLOR": (0, 0, 0),
                            "PARTICLE_FIRE": (255, 100, 0),
                            "PARTICLE_GOLD": (255, 215, 0),
                            "PARTICLE_LIGHT": (255, 255, 200),
                            "CHROMATIC_RED": (255, 50, 50),
                            "CHROMATIC_BLUE": (50, 150, 255),
                            "TEXTURE_LINES": (255, 255, 255),
                        },
                    ),
                    # Añadir claves para SPAIN_ANIMATION si faltan
                    "SPAIN_ANIMATION": config.get("COLORS", {}).get(
                        "SPAIN_ANIMATION",
                        {
                            "WAVE_SPEED": 0.05,
                            "WAVE_AMPLITUDE": 0.3,
                            "ROTATION_MAX": 0.3,
                            "SHINE_SPEED": 0.02,
                            "PULSE_SPEED": 0.03,
                        },
                    ),
                },
            ),
            # Audio
            "AUDIO": config.get("AUDIO", {"BPM": 128, "MUSIC_OFFSET": 0.12}),
            # Efectos BPM
            "BPM_EFFECT": config.get(
                "BPM_EFFECT", {"IN_NORMAL_MODE": False, "IN_RAVE_MODE": True}
            ),
        }

        # Construir contenido del archivo
        contenido = """# config.py
# Configuración principal del juego MetalWar
# Contiene todos los parámetros ajustables del sistema

GAME_CONFIG = {
"""

        # Función para formatear valores
        def formatear_valor(valor, nivel_indent=1):
            indent = "    " * nivel_indent

            if isinstance(valor, dict):
                lineas = ["{"]
                for k, v in valor.items():
                    lineas.append(
                        f'{indent}"{k}": {formatear_valor(v, nivel_indent + 1)},'
                    )
                lineas.append("    " * (nivel_indent - 1) + "}")
                return "\n".join(lineas)

            elif isinstance(valor, tuple):
                if len(valor) == 2:  # WINDOW_SIZE
                    return f"({valor[0]}, {valor[1]})"
                elif len(valor) == 4:  # RGBA
                    return f"({valor[0]}, {valor[1]}, {valor[2]}, {valor[3]})"
                elif len(valor) == 3:  # RGB
                    return f"({valor[0]}, {valor[1]}, {valor[2]})"
                else:
                    return str(valor)

            elif isinstance(valor, bool):
                return "True" if valor else "False"

            elif isinstance(valor, (int, float)):
                return str(valor)

            elif isinstance(valor, str):
                valor_escaped = valor.replace('"', '\\"')
                return f'"{valor_escaped}"'

            else:
                return repr(valor)

        # Añadir cada sección con TODAS las claves
        secciones = [
            (
                "INFORMACIÓN BÁSICA",
                [
                    ("GAME_FOLDER_NAME", "Nombre de la carpeta donde se instalará"),
                    ("GAME_NAME_DISPLAY", "Título que se muestra en pantalla"),
                    ("WINDOW_CAPTION", "Título de la ventana"),
                    ("SCROLLER_MESSAGE", "Mensaje del scroller animado"),
                    ("SUBTITLE_DISPLAY", "Subtítulo opcional"),
                    ("SPANISH_TEXT", "Texto personalizable"),
                ],
            ),
            (
                "CONFIGURACIÓN DE VENTANA Y RENDIMIENTO",
                [
                    ("WINDOW_SIZE", "Resolución de pantalla"),
                    ("FPS", "Fotogramas por segundo objetivo"),
                    (
                        "IDLE_TIMEOUT",
                        "Tiempo de inactividad antes de activar modo avatar",
                    ),
                ],
            ),
            (
                "CONFIGURACIÓN DE POST-INSTALACIÓN",
                [
                    ("POST_INSTALL", "Parche automático post-instalación"),
                ],
            ),
            (
                "PALETA DE COLORES DEL JUEGO",
                [
                    ("COLORS", "Paleta de colores (RGB y RGBA)"),
                ],
            ),
            (
                "CONFIGURACIÓN DE AUDIO Y SINCRONIZACIÓN BPM",
                [
                    ("AUDIO", "Audio y sincronización BPM"),
                ],
            ),
            (
                "CONTROL DE EFECTOS BPM",
                [
                    ("BPM_EFFECT", "Efectos BPM en formas geométricas por modo"),
                ],
            ),
        ]

        primera_clave = True

        for titulo_seccion, claves in secciones:
            if not primera_clave:
                contenido += "\n"
            contenido += f"\n    # {titulo_seccion}\n"

            for clave, comentario in claves:
                if clave in config_completo:
                    valor = config_completo[clave]
                    contenido += f'    "{clave}": {formatear_valor(valor)},\n'
                    primera_clave = False

        # Cerrar diccionario
        contenido += "}\n"

        # Guardar archivo
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(contenido)

        # Verificar que el archivo es válido
        try:
            test_vars = {}
            with open("config.py", "r", encoding="utf-8") as f:
                exec(f.read(), {}, test_vars)

            if "GAME_CONFIG" in test_vars:
                # Verificar claves críticas
                claves_criticas = [
                    "SCROLLER_MESSAGE",
                    "WINDOW_CAPTION",
                    "GAME_NAME_DISPLAY",
                ]
                claves_faltantes = []

                for clave in claves_criticas:
                    if clave not in test_vars["GAME_CONFIG"]:
                        claves_faltantes.append(clave)

                if not claves_faltantes:
                    print_success(
                        "config.py guardado correctamente con TODAS las claves necesarias"
                    )
                    print_info(f"Incluye: {', '.join(claves_criticas)} y más")
                    return True
                else:
                    print_error(
                        f"Faltan claves críticas: {', '.join(claves_faltantes)}"
                    )
                    if Path("config.py.backup").exists():
                        shutil.copy2("config.py.backup", "config.py")
                        print_info("Restaurado desde backup")
                    return False
            else:
                print_error("No se encontró GAME_CONFIG en el archivo")
                if Path("config.py.backup").exists():
                    shutil.copy2("config.py.backup", "config.py")
                    print_info("Restaurado desde backup")
                return False

        except Exception as e:
            print_error(f"Error validando config.py: {e}")
            if Path("config.py.backup").exists():
                shutil.copy2("config.py.backup", "config.py")
                print_info("Restaurado desde backup")
            return False

    except Exception as e:
        print_error(f"Error al guardar config.py: {e}")
        if Path("config.py.backup").exists():
            try:
                shutil.copy2("config.py.backup", "config.py")
                print_info("Restaurado desde backup")
            except:
                pass
        return False

    except Exception as e:
        print_error(f"Error al guardar config.py: {e}")
        if Path("config.py.backup").exists():
            try:
                shutil.copy2("config.py.backup", "config.py")
                print_info("Restaurado desde backup")
            except:
                pass
        return False


def leer_config():
    """Lee config.py y devuelve GAME_CONFIG directamente"""
    try:
        if not Path("config.py").exists():
            return None

        with open("config.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Extraer GAME_CONFIG
        match = re.search(r"GAME_CONFIG\s*=\s*({.*?})\s*(?:\n|$)", content, re.DOTALL)
        if match:
            try:
                config_str = match.group(1)
                # Convertir a dict
                config = ast.literal_eval(config_str)
                return config  # ← ESTO ES IMPORTANTE: Devuelve GAME_CONFIG directamente
            except:
                return None

        return None

    except Exception as e:
        print_error(f"Error leyendo config: {e}")
        return None


def mostrar_config_actual(config):
    """Muestra la configuración actual"""
    print_header("CONFIGURACIÓN ACTUAL")

    if not config:
        print_error("No hay configuración")
        return

    for clave, valor in config.items():
        if clave == "COLORS":
            print_color(f"\n{clave}:", Colors.TITLE)
            for color, rgb in valor.items():
                if isinstance(rgb, tuple):
                    print_color(f"  {color}: {rgb}", Colors.INFO)
        elif isinstance(valor, dict):
            print_color(f"\n{clave}:", Colors.TITLE)
            for subclave, subvalor in valor.items():
                print_color(f"  {subclave}: {subvalor}", Colors.INFO)
        else:
            print_color(f"{clave}: {valor}", Colors.INFO)


def editar_campo(config, clave, seccion=None, es_tupla=False):
    """Edita un campo de configuración"""
    try:
        # Asegurarnos de que config es GAME_CONFIG
        if not isinstance(config, dict):
            print_error("Configuración no válida")
            return False

        # Si hay sección, buscar dentro de ella
        if seccion:
            if seccion in config:
                if clave in config[seccion]:
                    valor_actual = config[seccion][clave]
                else:
                    # Buscar en subsecciones de COLORS
                    if seccion == "COLORS":
                        if (
                            "SPAIN_TEXT" in config["COLORS"]
                            and clave in config["COLORS"]["SPAIN_TEXT"]
                        ):
                            valor_actual = config["COLORS"]["SPAIN_TEXT"][clave]
                        elif (
                            "SPAIN_ANIMATION" in config["COLORS"]
                            and clave in config["COLORS"]["SPAIN_ANIMATION"]
                        ):
                            valor_actual = config["COLORS"]["SPAIN_ANIMATION"][clave]
                        else:
                            valor_actual = ""
                    else:
                        valor_actual = ""
            else:
                valor_actual = ""
        else:
            # Buscar directamente en GAME_CONFIG
            valor_actual = config.get(clave, "")

        print_color(f"\n{clave}:", Colors.TITLE)

        # Mostrar valor actual de forma legible
        if isinstance(valor_actual, tuple):
            print_color(f"  Actual (tupla): {valor_actual}", Colors.INFO)
        elif isinstance(valor_actual, dict):
            print_color(f"  Actual (dict): {valor_actual}", Colors.INFO)
        else:
            print_color(f"  Actual: {valor_actual}", Colors.INFO)

        nuevo = input("  Nuevo [Enter para mantener]: ").strip()

        if nuevo:
            # Procesar entrada según el tipo esperado
            if es_tupla and nuevo.startswith("(") and nuevo.endswith(")"):
                try:
                    # Intentar evaluar como tupla
                    import ast

                    valor_procesado = ast.literal_eval(nuevo)
                except:
                    valor_procesado = nuevo
            elif nuevo.lower() == "true":
                valor_procesado = True
            elif nuevo.lower() == "false":
                valor_procesado = False
            elif nuevo.isdigit():
                valor_procesado = int(nuevo)
            elif nuevo.replace(".", "", 1).isdigit():
                valor_procesado = float(nuevo)
            else:
                valor_procesado = nuevo

            if seccion:
                if seccion not in config:
                    config[seccion] = {}

                if seccion == "COLORS" and clave in [
                    "SPANISH_TEXT_SCALE",
                    "SUBTITLE_SCALE",
                    "FLAG_RED",
                    "FLAG_YELLOW",
                    "FLAG_YELLOW_2",
                    "TEXT_WHITE",
                    "TEXT_CYAN",
                    "TEXT_GREEN",
                    "SHINE_COLOR",
                    "GLOW_COLOR",
                    "OUTLINE_COLOR",
                    "PARTICLE_FIRE",
                    "PARTICLE_GOLD",
                    "PARTICLE_LIGHT",
                    "CHROMATIC_RED",
                    "CHROMATIC_BLUE",
                    "TEXTURE_LINES",
                    "WAVE_SPEED",
                    "WAVE_AMPLITUDE",
                    "ROTATION_MAX",
                    "SHINE_SPEED",
                    "PULSE_SPEED",
                ]:
                    # Estos son campos dentro de COLORS pero en subsecciones
                    if clave in [
                        "SPANISH_TEXT_SCALE",
                        "SUBTITLE_SCALE",
                        "FLAG_RED",
                        "FLAG_YELLOW",
                        "FLAG_YELLOW_2",
                        "TEXT_WHITE",
                        "TEXT_CYAN",
                        "TEXT_GREEN",
                        "SHINE_COLOR",
                        "GLOW_COLOR",
                        "OUTLINE_COLOR",
                        "PARTICLE_FIRE",
                        "PARTICLE_GOLD",
                        "PARTICLE_LIGHT",
                        "CHROMATIC_RED",
                        "CHROMATIC_BLUE",
                        "TEXTURE_LINES",
                    ]:
                        if "SPAIN_TEXT" not in config["COLORS"]:
                            config["COLORS"]["SPAIN_TEXT"] = {}
                        config["COLORS"]["SPAIN_TEXT"][clave] = valor_procesado
                    elif clave in [
                        "WAVE_SPEED",
                        "WAVE_AMPLITUDE",
                        "ROTATION_MAX",
                        "SHINE_SPEED",
                        "PULSE_SPEED",
                    ]:
                        if "SPAIN_ANIMATION" not in config["COLORS"]:
                            config["COLORS"]["SPAIN_ANIMATION"] = {}
                        config["COLORS"]["SPAIN_ANIMATION"][clave] = valor_procesado
                else:
                    config[seccion][clave] = valor_procesado
            else:
                config[clave] = valor_procesado

            return True
        return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def editar_version_info():
    """Edita version_info.txt en formato CORRECTO para PyInstaller"""
    try:
        print_header("📝 EDITAR INFORMACIÓN DE VERSIÓN")

        # Valores actuales (si el archivo existe)
        valores = {
            "ProductName": "MetalWar",
            "CompanyName": "TuEstudio",
            "FileDescription": "MetalWar Game",
            "FileVersion": "1.0.0.0",
            "ProductVersion": "1.0.0.0",
            "LegalCopyright": "Copyright © 2024 TuEstudio",
            "OriginalFilename": "MetalWar.exe",
            "InternalName": "METALWAR",
        }

        # Intentar leer valores existentes
        if Path("version_info.txt").exists():
            try:
                with open("version_info.txt", "r", encoding="utf-8") as f:
                    contenido = f.read()

                # Extraer valores del formato VSVersionInfo
                import re

                patterns = {
                    "ProductName": r"StringStruct\(u'ProductName', u'([^']*)'\)",
                    "CompanyName": r"StringStruct\(u'CompanyName', u'([^']*)'\)",
                    "FileDescription": r"StringStruct\(u'FileDescription', u'([^']*)'\)",
                    "FileVersion": r"StringStruct\(u'FileVersion', u'([^']*)'\)",
                    "ProductVersion": r"StringStruct\(u'ProductVersion', u'([^']*)'\)",
                    "LegalCopyright": r"StringStruct\(u'LegalCopyright', u'([^']*)'\)",
                    "OriginalFilename": r"StringStruct\(u'OriginalFilename', u'([^']*)'\)",
                    "InternalName": r"StringStruct\(u'InternalName', u'([^']*)'\)",
                }

                for key, pattern in patterns.items():
                    match = re.search(pattern, contenido)
                    if match:
                        valores[key] = match.group(1)

            except Exception as e:
                print_warning(f"No se pudo leer version_info.txt: {e}")

        print_color("\n✏️  EDITAR CAMPOS DE VERSIÓN:", Colors.TITLE)
        print_color("   (Formato: número.mayor.menor.revisión)", Colors.INFO)

        campos = [
            ("ProductName", "Nombre del producto"),
            ("CompanyName", "Nombre de la compañía"),
            ("FileDescription", "Descripción del archivo"),
            ("FileVersion", "Versión del archivo (ej: 1.0.0.0)"),
            ("ProductVersion", "Versión del producto (ej: 1.0.0.0)"),
            ("LegalCopyright", "Texto de copyright"),
            ("OriginalFilename", "Nombre del archivo .exe"),
            ("InternalName", "Nombre interno"),
        ]

        for i, (campo, desc) in enumerate(campos, 1):
            print_color(f"\n{i}. {desc}", Colors.OPTION)
            print_color(f"   Actual: {valores[campo]}", Colors.INFO)

            nuevo = input(f"   Nuevo [Enter para mantener]: ").strip()
            if nuevo:
                valores[campo] = nuevo

        # Crear contenido en formato CORRECTO para PyInstaller
        version_content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({valores['FileVersion'].replace('.', ', ')}),
    prodvers=({valores['ProductVersion'].replace('.', ', ')}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{valores['CompanyName']}'),
        StringStruct(u'FileDescription', u'{valores['FileDescription']}'),
        StringStruct(u'FileVersion', u'{valores['FileVersion']}'),
        StringStruct(u'InternalName', u'{valores['InternalName']}'),
        StringStruct(u'LegalCopyright', u'{valores['LegalCopyright']}'),
        StringStruct(u'OriginalFilename', u'{valores['OriginalFilename']}'),
        StringStruct(u'ProductName', u'{valores['ProductName']}'),
        StringStruct(u'ProductVersion', u'{valores['ProductVersion']}')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

        # Preguntar confirmación
        print_color("\n📄 VISTA PREVIA:", Colors.TITLE)
        print_color(
            (
                version_content[:500] + "..."
                if len(version_content) > 500
                else version_content
            ),
            Colors.INFO,
        )

        print_color("\n¿Guardar? (s/n): ", Colors.WARNING, end="")
        if input().strip().lower() in ["s", "si", "sí"]:
            with open("version_info.txt", "w", encoding="utf-8") as f:
                f.write(version_content)

            print_success("✅ version_info.txt guardado en formato CORRECTO")

            # Mostrar que ahora SÍ funcionará
            print_color("\n✅ AHORA SÍ funcionará con PyInstaller:", Colors.GREEN)
            print_color("   • Formato VSVersionInfo correcto", Colors.INFO)
            print_color(f"   • ProductName: {valores['ProductName']}", Colors.INFO)
            print_color(f"   • Versión: {valores['FileVersion']}", Colors.INFO)

            return True
        else:
            print_info("No se guardaron cambios")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def listar_recursos():
    """Lista archivos de recursos"""
    print_header("ARCHIVOS DE RECURSOS")

    tipos = {
        "Python": ["*.py"],
        "Imágenes": ["*.png", "*.jpg", "*.ico"],
        "Audio": ["*.mp3", "*.ogg", "*.wav", "*.mod"],
        "Datos": ["*.dat", "*.json", "*.txt"],
        "Ejecutables": ["*.exe", "*.dll"],
        "Fuentes": ["*.ttf", "*.otf"],
    }

    total = 0
    for tipo, patrones in tipos.items():
        archivos = []
        for patron in patrones:
            for f in Path(".").glob(patron):
                if f.name not in ["compilador.py"]:
                    archivos.append(f)

        if archivos:
            print_color(f"\n[{tipo.upper()}]", Colors.TITLE)
            for archivo in sorted(archivos):
                tamaño = archivo.stat().st_size
                if tamaño < 1024:
                    tamaño_str = f"{tamaño} B"
                elif tamaño < 1024 * 1024:
                    tamaño_str = f"{tamaño/1024:.1f} KB"
                else:
                    tamaño_str = f"{tamaño/(1024*1024):.1f} MB"

                print_color(f"  {archivo.name} ", Colors.FIELD, end="")
                print_color(f"({tamaño_str})", Colors.GRAY)
                total += 1

    print_color(f"\nTotal: {total} archivos", Colors.INFO)
    return total


def crear_spec(config, usar_upx=False):
    """Crea archivo .spec con TODOS los recursos del juego"""
    try:
        # Nombre del ejecutable
        if config and "GAME_NAME_DISPLAY" in config:
            nombre_juego = config["GAME_NAME_DISPLAY"].replace(" ", "_")
        else:
            nombre_juego = "MetalWar"

        nombre_exe = f"{nombre_juego}.exe"
        spec_file = f"{nombre_juego}.spec"

        print_header("📝 CREANDO SPEC CON RECURSOS")

        # Verificar archivos esenciales
        if not Path("main.py").exists():
            print_error("❌ main.py no encontrado")
            return None

        if not Path("config.py").exists():
            print_error("❌ config.py no encontrado")
            return None

        # ============================================================
        # RECOLECTAR TODOS LOS RECURSOS
        # ============================================================
        print_color("\n🔍 BUSCANDO RECURSOS...", Colors.INFO)

        datos = []

        # 1. Archivos Python esenciales
        archivos_py = [
            "config.py",
            "main.py",
            "ui.py",
            "utils.py",
            "effects.py",
            "audio.py",
            "installer.py",
        ]

        for archivo in archivos_py:
            if Path(archivo).exists():
                datos.append((archivo, "."))
                print_success(f"   📄 {archivo}")

        # 2. Archivos gráficos y multimedia
        patrones_multimedia = [
            # Imágenes
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.ico",
            "*.bmp",
            # Audio estándar
            "*.mp3",
            "*.ogg",
            "*.wav",
            "*.flac",
            # Módulos tracker
            "*.mod",
            "*.xm",
            "*.s3m",
            "*.it",
            "*.stm",
            "*.mtm",
            # Fuentes
            "*.ttf",
            "*.otf",
            # Datos
            "*.json",
            "*.txt",
            "*.dat",
            "*.xml",
            # Ejecutables (parcheadores)
            "*.exe",
            "*.dll",
        ]

        import glob

        recursos_encontrados = 0

        for patron in patrones_multimedia:
            for archivo in glob.glob(patron):
                # Excluir archivos de desarrollo
                if archivo in ["compile.py", "compilador.py"]:
                    continue

                if Path(archivo).is_file():
                    if (archivo, ".") not in datos:
                        datos.append((archivo, "."))
                        recursos_encontrados += 1

                        # Mostrar tipos especiales
                        if archivo.endswith((".mod", ".xm", ".s3m", ".it")):
                            print_color(f"   🎵 {archivo}", Colors.CYAN)
                        elif archivo.endswith(".exe"):
                            print_color(f"   ⚙  {archivo}", Colors.MAGENTA)

        print_success(f"✅ {recursos_encontrados} recursos multimedia encontrados")

        # 3. Verificar archivos críticos
        archivos_criticos = {
            "icon.ico": "Icono",
            "splash.png": "Splash screen",
            "version_info.txt": "Información de versión",
        }

        for archivo, descripcion in archivos_criticos.items():
            if Path(archivo).exists():
                if (archivo, ".") not in datos:
                    datos.append((archivo, "."))
                print_success(f"   ✅ {descripcion}: {archivo}")
            else:
                print_warning(f"   ⚠  {descripcion}: {archivo} NO ENCONTRADO")

        print_color(f"\n📊 TOTAL RECURSOS: {len(datos)} archivos", Colors.INFO)

        # ============================================================
        # GENERAR SPEC
        # ============================================================
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
# MetalWar - Archivo de especificación
# Generado automáticamente por compile.py

import os

block_cipher = None

# ========== ANÁLISIS CON TODOS LOS RECURSOS ==========
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas={datos},  # ← TODOS los recursos incluidos aquí
    hiddenimports=[
        'pygame',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ========== PAQUETE PYTHON ==========
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ========== SPLASH SCREEN ==========
"""

        # Configurar splash si existe
        if Path("splash.png").exists():
            spec_content += """splash = Splash(
    'splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

"""

        # ========== EJECUTABLE FINAL ==========
        spec_content += f"""# ========== EJECUTABLE FINAL ==========
exe = EXE(
    pyz,
    a.scripts,
"""

        if Path("splash.png").exists():
            spec_content += """    splash,
    splash.binaries,
"""

        spec_content += f"""    [],
    a.binaries,
    a.datas,
    [],
    name='{nombre_exe}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx={'True' if usar_upx else 'False'},
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # ← Ventana sin consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
"""

        # Añadir icono si existe
        if Path("icon.ico").exists():
            spec_content += f"    icon='icon.ico',\n"

        # Añadir splash si existe
        if Path("splash.png").exists():
            spec_content += f"    splash='splash.png',\n"

        # Añadir versión si existe
        if Path("version_info.txt").exists():
            spec_content += f"    version='version_info.txt',\n"

        # Cerrar EXE
        spec_content += ")\n"

        # Guardar archivo
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(spec_content)

        print_success(f"\n✅ {spec_file} CREADO CORRECTAMENTE")

        # Mostrar resumen final
        print_color("\n⚙  CONFIGURACIÓN FINAL:", Colors.TITLE)
        print_color(f"   • Ejecutable: {nombre_exe}", Colors.INFO)
        print_color(f"   • Recursos incluidos: {len(datos)} archivos", Colors.INFO)
        print_color(f"   • Modo: 📦 UN SOLO ARCHIVO (onefile)", Colors.GREEN)
        print_color(f"   • Consola: 🚫 OCULTA", Colors.RED)

        # Contar tipos de archivos
        tipos = {}
        for archivo, _ in datos:
            ext = Path(archivo).suffix.lower()
            if ext in [".py"]:
                tipos["Scripts Python"] = tipos.get("Scripts Python", 0) + 1
            elif ext in [".png", ".jpg", ".jpeg", ".ico", ".bmp"]:
                tipos["Imágenes"] = tipos.get("Imágenes", 0) + 1
            elif ext in [".mod", ".xm", ".s3m", ".it", ".mp3", ".ogg", ".wav"]:
                tipos["Audio"] = tipos.get("Audio", 0) + 1
            elif ext in [".ttf", ".otf"]:
                tipos["Fuentes"] = tipos.get("Fuentes", 0) + 1
            elif ext in [".exe", ".dll"]:
                tipos["Ejecutables"] = tipos.get("Ejecutables", 0) + 1
            else:
                tipos["Otros"] = tipos.get("Otros", 0) + 1

        print_color(f"\n📋 DISTRIBUCIÓN DE RECURSOS:", Colors.TITLE)
        for tipo, cantidad in tipos.items():
            print_color(f"   • {tipo}: {cantidad}", Colors.GRAY)

        return spec_file

    except Exception as e:
        print_error(f"❌ Error creando spec: {e}")
        import traceback

        traceback.print_exc()
        return None


def diagnosticar_compilacion():
    """Diagnóstico de problemas de compilación"""
    print_header("🔍 DIAGNÓSTICO DE COMPILACIÓN")

    print_color("\n📁 ARCHIVOS ESENCIALES:", Colors.TITLE)
    archivos_esenciales = ["main.py", "config.py", "ui.py", "utils.py"]
    for archivo in archivos_esenciales:
        existe = Path(archivo).exists()
        estado = "✅ PRESENTE" if existe else "❌ FALTANTE"
        color = Colors.GREEN if existe else Colors.RED
        print_color(f"  {archivo}: {estado}", color)

    print_color("\n🐍 VERSIÓN DE PYTHON:", Colors.TITLE)
    print_color(f"  {sys.version}", Colors.INFO)

    print_color("\n📦 PYINSTALLER:", Colors.TITLE)
    try:
        resultado = subprocess.run(
            ["pyinstaller", "--version"], capture_output=True, text=True, timeout=5
        )
        if resultado.returncode == 0:
            print_color(f"  ✅ Versión: {resultado.stdout.strip()}", Colors.GREEN)
        else:
            print_color("  ❌ No responde", Colors.RED)
    except:
        print_color("  ❌ No encontrado", Colors.RED)

    print_color("\n💡 PRUEBA MANUAL:", Colors.TITLE)
    print_color("  Ejecuta este comando para ver errores completos:", Colors.INFO)
    print_color("  pyinstaller --clean main.py --onefile --windowed", Colors.VALUE)

    input("\nPresiona Enter para continuar...")


def compilar_proyecto(spec_file):
    """Compila con .spec - VERSIÓN MEJORADA CON MEJOR DIAGNÓSTICO"""
    try:
        print_header("COMPILACIÓN")

        # Verificar que el spec existe
        if not Path(spec_file).exists():
            print_error(f"❌ Archivo {spec_file} no encontrado")
            return False

        # Verificar que main.py existe (CRÍTICO)
        if not Path("main.py").exists():
            print_error("❌ main.py NO ENCONTRADO")
            print_color(
                "   El archivo main.py debe estar en el directorio actual", Colors.INFO
            )
            return False

        print_success(f"✅ main.py encontrado")

        # Verificar splash
        if Path("splash.png").exists():
            print_success(f"✅ splash.png encontrado")
        else:
            print_warning(f"⚠  splash.png no encontrado")

        print_info(f"📦 Usando spec: {spec_file}")

        # Comando SIMPLIFICADO - sin --log-level para ver TODO
        comando = [
            "pyinstaller",
            "--clean",
            "--noconfirm",
            spec_file,
        ]

        print_color(f"\n🔨 Comando:", Colors.TITLE)
        print_color(f"   {' '.join(comando)}", Colors.VALUE)
        print_color("\n⚠  Esto puede tomar varios minutos...", Colors.YELLOW)

        # Animación simple
        def mostrar_progreso():
            chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            i = 0
            while not hasattr(mostrar_progreso, "detener"):
                print(f"\r{chars[i % len(chars)]} Compilando...", end="", flush=True)
                i += 1
                time.sleep(0.3)

        progreso_thread = threading.Thread(target=mostrar_progreso)
        progreso_thread.start()

        try:
            # Ejecutar con timeout extendido
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",  # Ignorar errores de encoding
                shell=True,
                timeout=900,  # 15 minutos timeout
            )

            mostrar_progreso.detener = True
            progreso_thread.join()
            print("\r" + " " * 50 + "\r", end="")  # Limpiar línea

            # ANALIZAR RESULTADO
            if resultado.returncode == 0:
                print_success("✅ ¡COMPILACIÓN EXITOSA!")
                print_color("\n" + "=" * 60, Colors.GREEN)
                print_color("🎮 ¡EJECUTABLE CREADO!", Colors.GREEN + Colors.BOLD)
                print_color("=" * 60, Colors.GREEN)

                # Buscar ejecutable
                spec_path = Path(spec_file)
                nombre_base = spec_path.stem
                exe_path = Path("dist") / f"{nombre_base}.exe"

                if exe_path.exists():
                    tamaño = exe_path.stat().st_size / (1024 * 1024)
                    print_color(f"\n📍 Ubicación: {exe_path}", Colors.CYAN)
                    print_color(f"📏 Tamaño: {tamaño:.2f} MB", Colors.INFO)

                    # Mostrar información del spec
                    try:
                        with open(spec_file, "r", encoding="utf-8") as f:
                            spec_content = f.read()

                        # Verificar características
                        tiene_splash = "splash = Splash(" in spec_content
                        upx_activado = "upx=True" in spec_content

                        print_color("\n⚙  CARACTERÍSTICAS INCLUIDAS:", Colors.TITLE)
                        print_color(
                            f"   • Splash Screen: {'✅ SÍ' if tiene_splash else '🚫 NO'}",
                            Colors.GREEN if tiene_splash else Colors.YELLOW,
                        )
                        print_color(
                            f"   • UPX: {'✅ ACTIVADO' if upx_activado else '🚫 DESACTIVADO'}",
                            Colors.GREEN if not upx_activado else Colors.YELLOW,
                        )
                        print_color(f"   • Consola: 🚫 OCULTA", Colors.RED)

                    except:
                        pass

                    # Preguntar por abrir carpeta
                    print_color(
                        "\n¿Abrir carpeta del ejecutable? (s/n): ", Colors.INFO, end=""
                    )
                    respuesta = input().strip().lower()
                    if respuesta in ["s", "si", "sí", "y", "yes"]:
                        abrir_carpeta_ejecutable()

                    return True
                else:
                    # Buscar cualquier .exe en dist
                    exe_files = list(Path("dist").rglob("*.exe"))
                    if exe_files:
                        exe_reciente = max(exe_files, key=lambda x: x.stat().st_mtime)
                        print_success(f"✅ Ejecutable encontrado: {exe_reciente.name}")
                        print_color(f"   Ruta: {exe_reciente}", Colors.CYAN)
                        return True
                    else:
                        print_warning("⚠  No se encontró ningún .exe en 'dist/'")
                        print_color(
                            "   Revisa los mensajes de error anteriores", Colors.INFO
                        )
                        return False

            else:
                # ERROR - Mostrar TODO el output
                print_error(f"❌ COMPILACIÓN FALLIDA (código: {resultado.returncode})")
                print_color("\n" + "=" * 60, Colors.RED)
                print_color("📋 SALIDA COMPLETA DEL ERROR:", Colors.RED + Colors.BOLD)
                print_color("=" * 60, Colors.RED)

                # Mostrar stderr completo
                if resultado.stderr:
                    print_color("\n📛 ERRORES (stderr):", Colors.TITLE)
                    print_color(
                        resultado.stderr[:5000], Colors.ERROR
                    )  # Primeros 5000 chars
                    if len(resultado.stderr) > 5000:
                        print_color(
                            f"... (mostrando primeros 5000 de {len(resultado.stderr)} caracteres)",
                            Colors.GRAY,
                        )

                # Mostrar stdout completo
                if resultado.stdout:
                    print_color("\n📄 INFORMACIÓN (stdout):", Colors.TITLE)

                    # Filtrar líneas importantes
                    lineas = resultado.stdout.split("\n")
                    lineas_importantes = []

                    for linea in lineas:
                        linea_lower = linea.lower()
                        # Filtrar líneas críticas
                        if any(
                            keyword in linea_lower
                            for keyword in [
                                "error",
                                "failed",
                                "fail",
                                "traceback",
                                "exception",
                                "missing",
                                "not found",
                                "cannot",
                                "can't",
                                "import",
                            ]
                        ):
                            lineas_importantes.append(("ERROR", linea))
                        elif any(
                            keyword in linea_lower
                            for keyword in ["warning", "warn", "deprecated"]
                        ):
                            lineas_importantes.append(("WARNING", linea))
                        elif any(
                            keyword in linea_lower
                            for keyword in [
                                "info:",
                                "checking",
                                "analyzing",
                                "processing",
                            ]
                        ):
                            lineas_importantes.append(("INFO", linea))

                    # Mostrar líneas importantes
                    for tipo, linea in lineas_importantes[-50:]:  # Últimas 50 líneas
                        if tipo == "ERROR":
                            print_color(f"  ✗ {linea}", Colors.ERROR)
                        elif tipo == "WARNING":
                            print_color(f"  ⚠ {linea}", Colors.YELLOW)
                        else:
                            print_color(f"  ℹ {linea}", Colors.GRAY)

                    if not lineas_importantes:
                        print_color(
                            resultado.stdout[-2000:], Colors.GRAY
                        )  # Últimas 2000 chars

                # Diagnóstico común
                print_color("\n🔍 DIAGNÓSTICO RÁPIDO:", Colors.TITLE)
                print_color(
                    "1. ¿main.py existe en el directorio actual?",
                    Colors.GREEN if Path("main.py").exists() else Colors.ERROR,
                )
                print_color(
                    "2. ¿config.py existe?",
                    Colors.GREEN if Path("config.py").exists() else Colors.ERROR,
                )
                print_color("3. ¿Tienes permisos de escritura?", Colors.INFO)
                print_color("4. ¿Hay suficiente espacio en disco?", Colors.INFO)

                # Sugerencia
                print_color("\n💡 SUGERENCIA:", Colors.TITLE)
                print_color(
                    "   Intenta compilar manualmente para ver el error completo:",
                    Colors.INFO,
                )
                print_color(
                    f"   pyinstaller --clean --noconfirm {spec_file}", Colors.VALUE
                )

                return False

        except subprocess.TimeoutExpired:
            mostrar_progreso.detener = True
            progreso_thread.join()
            print_error("⏰ TIMEOUT - La compilación tardó más de 15 minutos")
            print_color("   Esto puede ser normal para proyectos grandes", Colors.INFO)
            print_color("   Intenta nuevamente o compila manualmente", Colors.INFO)
            return False

        except Exception as e:
            mostrar_progreso.detener = True
            progreso_thread.join()
            print_error(f"❌ Error inesperado: {e}")
            return False

    except Exception as e:
        print_error(f"❌ Error inicial: {e}")
        return False


def abrir_carpeta_ejecutable():
    """Abre la carpeta del ejecutable - VERSIÓN MEJORADA"""
    try:
        # Buscar cualquier .exe en dist
        exe_files = []
        for archivo in Path("dist").rglob("*.exe"):
            if archivo.is_file():
                exe_files.append(archivo)

        if not exe_files:
            print_warning("No se encontraron ejecutables en 'dist/'")

            # Ver si existe la carpeta
            if Path("dist").exists():
                carpeta = Path("dist")
                print_info(f"Carpeta 'dist' existe (sin .exe)")
            else:
                print_error("No existe carpeta 'dist'")
                return False
        else:
            # Tomar el más reciente
            exe_reciente = max(exe_files, key=lambda x: x.stat().st_mtime)
            carpeta = exe_reciente.parent
            print_success(f"Ejecutable: {exe_reciente.name}")

        print_info(f"Abriendo: {carpeta.absolute()}")

        sistema = platform.system()

        if sistema == "Windows":
            try:
                # Método más confiable para Windows
                os.startfile(str(carpeta.absolute()))
                print_success("✓ Carpeta abierta")
                return True
            except Exception as e:
                try:
                    # Método alternativo
                    subprocess.run(
                        ["explorer", str(carpeta.absolute())], shell=True, check=False
                    )
                    print_success("✓ Carpeta abierta con Explorer")
                    return True
                except:
                    print_warning(f"✗ No se pudo abrir automáticamente")

        elif sistema == "Darwin":
            subprocess.run(["open", str(carpeta)])
            print_success("✓ Carpeta abierta")
            return True

        elif sistema == "Linux":
            subprocess.run(["xdg-open", str(carpeta)])
            print_success("✓ Carpeta abierta")
            return True

        # Mostrar ruta manual
        print_color(f"\n📍 RUTA MANUAL: {carpeta.absolute()}", Colors.CYAN)
        print_color("Abre el explorador de archivos y navega a esa ruta", Colors.INFO)
        return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def reparar_config():
    """Crea un config.py completo"""
    try:
        # Configuración por defecto
        config_completo = {
            "GAME_FOLDER_NAME": "CARPETA DEL JUEGO",
            "GAME_NAME_DISPLAY": "TITULO DEL JUEGO",
            "SUBTITLE_DISPLAY": "",
            "SPANISH_TEXT": "In Awesome Spanish",
            "WINDOW_SIZE": (800, 600),
            "FPS": 60,
            "IDLE_TIMEOUT": 20.0,
            "POST_INSTALL": {
                "ENABLED": False,
                "PATCHER_EXE": "example.exe",
                "TARGET_FILE": "catalog.json",
                "ARGUMENT": "patchcrc",
            },
            "COLORS": {
                "BLACK": (10, 10, 18),
                "WHITE": (255, 255, 255),
                "BLUE_NEON": (0, 255, 255),
                "RED_ALERT": (255, 0, 0),
                "CYAN_NEON": (0, 255, 200),
                "PEACE_GREEN": (50, 255, 100),
                "BUTTON_GRAY": (40, 40, 50),
                "BUTTON_HOVER": (60, 60, 75),
                "GREEN_SUCCESS": (50, 220, 50),
                "LIGHT_TEXT": (135, 206, 250),
                "HUD_BG": (0, 0, 0, 180),
            },
            "AUDIO": {"BPM": 128, "MUSIC_OFFSET": 0.12},
            "BPM_EFFECT": {"IN_NORMAL_MODE": False, "IN_RAVE_MODE": True},
        }

        # Usar guardar_config
        if guardar_config(config_completo):
            print_success("config.py reparado")
            return True
        else:
            print_error("No se pudo reparar config.py")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False


def probar_splash():
    """Prueba si el splash.png es compatible"""
    try:
        if not Path("splash.png").exists():
            print_error("No hay splash.png para probar")
            return False

        print_header("PROBANDO SPLASH.PNG")

        try:
            from PIL import Image

            with Image.open("splash.png") as img:
                width, height = img.size
                formato = img.format
                modo = img.mode

                print_success(f"✅ Archivo válido: {width}x{height} pixels")
                print_color(f"   Formato: {formato}", Colors.INFO)
                print_color(f"   Modo: {modo}", Colors.INFO)

                # Verificar compatibilidad
                if formato != "PNG":
                    print_warning(f"⚠  Formato {formato}, debería ser PNG")

                if modo not in ["RGB", "RGBA"]:
                    print_warning(f"⚠  Modo {modo}, ideal RGB o RGBA")

                # Tamaño recomendado
                if width >= 400 and height >= 300 and width <= 1200 and height <= 800:
                    print_success(f"✅ Tamaño adecuado")
                else:
                    print_warning(f"⚠  Tamaño inusual: {width}x{height}")
                    print_color("   Recomendado: 600x400 a 800x600", Colors.INFO)

                return True

        except ImportError:
            print_warning("Instala Pillow para análisis detallado:")
            print_color("  pip install Pillow", Colors.VALUE)
            print_info("El archivo existe, pero no se pudo analizar")
            return True

    except Exception as e:
        print_error(f"Error probando splash: {e}")
        return False


def crear_icono_desde_logo():
    """Crea un archivo icon.ico a partir de logo.png usando Pillow"""
    try:
        print_header("CREAR ICONO .ICO DESDE LOGO.PNG")

        # Verificar que existe logo.png
        if not Path("logo.png").exists():
            print_error("❌ No se encontró logo.png")
            print_color(
                "Asegúrate de tener un archivo logo.png en el directorio actual",
                Colors.INFO,
            )
            return False

        # Verificar si ya existe icon.ico
        if Path("icon.ico").exists():
            print_warning("⚠  Ya existe icon.ico")
            print_color("¿Sobrescribir? (s/n): ", Colors.WARNING, end="")
            respuesta = input().strip().lower()
            if respuesta not in ["s", "si", "sí"]:
                print_info("Operación cancelada")
                return False

        print_info("Intentando crear icon.ico...")

        try:
            from PIL import Image

            # Abrir el logo
            img = Image.open("logo.png")

            # Mostrar información del logo
            width, height = img.size
            formato = img.format
            modo = img.mode

            print_success(f"✅ Logo encontrado: {width}x{height} pixels")
            print_color(f"   Formato: {formato}", Colors.INFO)
            print_color(f"   Modo: {modo}", Colors.INFO)

            # Verificar si el logo es adecuado
            if width < 256 or height < 256:
                print_warning(f"⚠  Logo pequeño: {width}x{height}")
                print_color(
                    "   Para un icono de buena calidad, se recomienda mínimo 256x256",
                    Colors.YELLOW,
                )
                print_color(
                    "   ¿Continuar de todas formas? (s/n): ", Colors.WARNING, end=""
                )
                if input().strip().lower() not in ["s", "si", "sí"]:
                    return False

            # Crear el icono con múltiples tamaños
            print_info("Creando icon.ico con múltiples resoluciones...")

            # Lista de tamaños estándar para iconos Windows
            tamanos = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

            # Guardar como .ico con múltiples tamaños
            img.save("icon.ico", format="ICO", sizes=tamanos)

            print_success("✅ ¡Icono creado exitosamente!")

            # Verificar que se creó correctamente
            if Path("icon.ico").exists():
                tamaño = Path("icon.ico").stat().st_size
                if tamaño < 1024:
                    tamaño_str = f"{tamaño} B"
                elif tamaño < 1024 * 1024:
                    tamaño_str = f"{tamaño/1024:.1f} KB"
                else:
                    tamaño_str = f"{tamaño/(1024*1024):.1f} MB"

                print_color(f"\n📄 Archivo: icon.ico", Colors.CYAN)
                print_color(f"📏 Tamaño: {tamaño_str}", Colors.INFO)
                print_color(f"🎨 Resoluciones incluidas:", Colors.INFO)
                for tam in tamanos:
                    print_color(f"   • {tam[0]}x{tam[1]}", Colors.GRAY)

                print_color(
                    "\n✅ El icono está listo para usar en la compilación", Colors.GREEN
                )
                return True
            else:
                print_error("❌ No se pudo crear icon.ico")
                return False

        except ImportError:
            print_error("❌ Pillow no está instalado")
            print_color(
                "Pillow es necesario para crear iconos desde imágenes PNG", Colors.INFO
            )
            print_color("\n📦 Instala Pillow con:", Colors.CYAN)
            print_color("   pip install Pillow", Colors.VALUE)

            # Preguntar si instalar ahora
            print_color("\n¿Instalar Pillow ahora? (s/n): ", Colors.WARNING, end="")
            if input().strip().lower() in ["s", "si", "sí"]:
                try:
                    print_info("Instalando Pillow...")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "Pillow"], check=True
                    )
                    print_success("✅ Pillow instalado")

                    # Intentar nuevamente
                    return crear_icono_desde_logo()
                except:
                    print_error("❌ No se pudo instalar Pillow")
                    return False
            return False

    except Exception as e:
        print_error(f"❌ Error creando icono: {e}")
        return False


def generar_splash_pro():
    """Genera splash screen profesional usando DemosceneFactory"""
    try:
        print_header("GENERADOR DE SPLASH - DEMOSCENE FACTORY")

        # Verificar si Pillow está instalado
        try:
            from PIL import Image

            pillow_disponible = True
        except ImportError:
            print_warning("⚠  Pillow no está instalado")
            print_color("Pillow es necesario para generar splash screens", Colors.INFO)
            print_color("\n📦 Instalar Pillow ahora? (s/n): ", Colors.WARNING, end="")
            if input().strip().lower() in ["s", "si", "sí"]:
                try:
                    print_info("Instalando Pillow...")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "Pillow"], check=True
                    )
                    print_success("✅ Pillow instalado")
                    pillow_disponible = True
                except:
                    print_error("❌ No se pudo instalar Pillow")
                    return False
            else:
                return False

        # Obtener nombre del producto desde version_info.txt
        product_name = "MetalWar"
        if Path("version_info.txt").exists():
            try:
                with open("version_info.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                product_match = re.search(r"'ProductName', '([^']*)'", content)
                if product_match:
                    product_name = product_match.group(1)
            except:
                pass

        print_color(f"\n📄 Nombre del producto: {product_name}", Colors.INFO)
        print_color(f"📏 Tamaño: 600x400 (óptimo para PyInstaller)", Colors.INFO)

        # Mostrar opciones de temas DEMOSCENE
        print_color("\n🎨 TEMAS DEMOSCENE PROCEDURALES:", Colors.TITLE)
        print_color(
            "1. ⚡ PLASMA CORE (Matemática procedural)", Colors.CYAN + Colors.BOLD
        )
        print_color(
            "   Ondas sinusoidales, paletas rotativas, algoritmos 90s", Colors.GRAY
        )

        print_color("2. 🎛️ COPPER BARS (Estilo Amiga/C64)", Colors.MAGENTA + Colors.BOLD)
        print_color("   Barras de gradiente, efectos retro de demoscene", Colors.GRAY)

        print_color("3. 🌌 SYNTHWAVE GRID (Neón 80s)", Colors.GREEN + Colors.BOLD)
        print_color(
            "   Grid de perspectiva, sol retrowave, ambiente cyberpunk", Colors.GRAY
        )

        print_color("4. 🎲 ALEATORIO (elige un tema al azar)", Colors.YELLOW)

        try:
            opcion = input("\nSelecciona tema (1-4): ").strip()

            if opcion == "4":
                opcion = str(random.randint(1, 3))
                temas = ["PLASMA CORE", "COPPER BARS", "SYNTHWAVE GRID"]
                tema_elegido = temas[int(opcion) - 1]
                print_color(f"🎲 Tema aleatorio: {tema_elegido}", Colors.YELLOW)
            else:
                temas = ["PLASMA CORE", "COPPER BARS", "SYNTHWAVE GRID"]
                tema_elegido = (
                    temas[int(opcion) - 1]
                    if opcion in ["1", "2", "3"]
                    else "DESCONOCIDO"
                )

            if opcion not in ["1", "2", "3"]:
                print_error("Opción inválida")
                return False

            # Verificar si ya existe splash.png
            if Path("splash.png").exists():
                print_warning("⚠  Ya existe splash.png")
                print_color("¿Sobrescribir? (s/n): ", Colors.WARNING, end="")
                respuesta = input().strip().lower()
                if respuesta not in ["s", "si", "sí"]:
                    print_info("Operación cancelada")
                    return False

            # Crear generador profesional
            print_info("🎨 Generando splash screen demoscene...")
            print_color(
                "   (Usando algoritmos procedurales de la vieja escuela)", Colors.INFO
            )

            # Configurar tamaño óptimo para PyInstaller (600x400)
            factory = DemosceneFactory(width=600, height=400)

            # Generar según el tema seleccionado
            if opcion == "1":  # PLASMA
                img = factory.generar_plasma(
                    product_name, "> Loading Resources... Please Wait"
                )

            elif opcion == "2":  # COPPER
                img = factory.generar_copper(
                    product_name, "> Initializing System... Please Wait"
                )

            elif opcion == "3":  # SYNTHWAVE
                img = factory.generar_synthwave(
                    product_name, "> Unpacking Assets... Please Wait"
                )

            # Guardar imagen
            img.save("splash.png", "PNG", optimize=True, quality=95)

            print_success(f"✅ Splash screen '{tema_elegido}' generado exitosamente!")

            # Mostrar información
            print_color(f"\n📄 Archivo: splash.png", Colors.CYAN)
            print_color(
                f"📏 Tamaño: 600x400 pixels (óptimo para PyInstaller)", Colors.INFO
            )
            print_color(f"🎨 Tema: {tema_elegido}", Colors.INFO)
            print_color(f"📝 Texto: {product_name}", Colors.INFO)
            print_color(
                f"✨ Efectos: CRT Scanlines + RGB Shift + Vignette", Colors.GREEN
            )
            print_color(
                f"🎲 Procedural: Generado con parámetros aleatorios únicos",
                Colors.GREEN,
            )

            # Preguntar si ver el splash
            print_color("\n¿Ver el splash generado? (s/n): ", Colors.WARNING, end="")
            if input().strip().lower() in ["s", "si", "sí"]:
                try:
                    img.show()
                except:
                    print_info(
                        "No se pudo mostrar la imagen (pero se guardó correctamente)"
                    )

            return True

        except Exception as e:
            print_error(f"❌ Error generando splash: {e}")
            return False

    except Exception as e:
        print_error(f"❌ Error: {e}")
        return False


def verificar_dependencias():
    """Verifica que todas las dependencias necesarias estén instaladas correctamente"""
    try:
        print_header("VERIFICACIÓN DE DEPENDENCIAS PYINSTALLER")

        print_color("🔍 Comprobando instalación de paquetes críticos...", Colors.INFO)

        dependencias_criticas = ["pyinstaller", "pillow", "pygame"]

        import subprocess
        import sys

        # 1. Verificar con pip check
        print_color("\n📦 Ejecutando 'pip check'...", Colors.TITLE)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print_success("✓ Todas las dependencias están correctas")
            else:
                print_warning("⚠ Problemas detectados con pip check:")
                if result.stdout:
                    print_color(f"   {result.stdout.strip()}", Colors.YELLOW)
                if result.stderr:
                    print_color(f"   Errores: {result.stderr.strip()}", Colors.ERROR)
        except subprocess.TimeoutExpired:
            print_warning("⚠ 'pip check' tardó demasiado (saltando...)")
        except Exception as e:
            print_warning(f"⚠ No se pudo ejecutar 'pip check': {e}")

        # 2. Verificar módulos individualmente
        print_color("\n🔧 Verificando módulos críticos para compilación:", Colors.TITLE)

        for dep in dependencias_criticas:
            try:
                if dep == "pillow":
                    import PIL
                    from PIL import Image, ImageDraw, ImageFont

                    print_success(
                        f"  ✓ PIL (Pillow) {PIL.__version__} - OK para generar splash"
                    )
                elif dep == "pygame":
                    import pygame

                    print_success(
                        f"  ✓ PyGame {pygame.version.ver} - OK para efectos de juego"
                    )
                elif dep == "pyinstaller":
                    try:
                        result = subprocess.run(
                            ["pyinstaller", "--version"],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )

                        if result.returncode == 0:
                            version = result.stdout.strip()
                            print_success(
                                f"  ✓ PyInstaller {version} - OK para compilación"
                            )
                        else:
                            try:
                                pip_result = subprocess.run(
                                    [
                                        sys.executable,
                                        "-m",
                                        "pip",
                                        "show",
                                        "pyinstaller",
                                    ],
                                    capture_output=True,
                                    text=True,
                                )
                                if pip_result.returncode == 0:
                                    version_line = [
                                        line
                                        for line in pip_result.stdout.split("\n")
                                        if "Version:" in line
                                    ]
                                    version = (
                                        version_line[0].split(": ")[1]
                                        if version_line
                                        else "desconocida"
                                    )
                                    print_success(
                                        f"  ✓ PyInstaller {version} - OK para compilación"
                                    )
                                else:
                                    print_error(f"  ✗ PyInstaller NO encontrado")
                                    print_color(
                                        f"     Instala con: pip install pyinstaller",
                                        Colors.INFO,
                                    )
                            except:
                                print_error(f"  ✗ PyInstaller NO encontrado")
                                print_color(
                                    f"     Instala con: pip install pyinstaller",
                                    Colors.INFO,
                                )
                    except FileNotFoundError:
                        try:
                            result = subprocess.run(
                                [sys.executable, "-m", "PyInstaller", "--version"],
                                capture_output=True,
                                text=True,
                                timeout=10,
                            )
                            if result.returncode == 0:
                                version = result.stdout.strip()
                                print_success(
                                    f"  ✓ PyInstaller {version} (vía python -m) - OK para compilación"
                                )
                            else:
                                print_error(f"  ✗ PyInstaller NO encontrado")
                                print_color(
                                    f"     Instala con: pip install pyinstaller",
                                    Colors.INFO,
                                )
                        except:
                            print_error(f"  ✗ PyInstaller NO encontrado")
                            print_color(
                                f"     Instala con: pip install pyinstaller",
                                Colors.INFO,
                            )
                    except Exception as e:
                        print_warning(f"  ⚠ PyInstaller - Error verificando: {e}")
            except ImportError as e:
                if dep != "pyinstaller":
                    print_error(f"  ✗ {dep.upper()} NO disponible: {e}")
                    if dep == "pillow":
                        print_color(
                            f"     Instala con: pip install Pillow", Colors.INFO
                        )
                    elif dep == "pygame":
                        print_color(
                            f"     Instala con: pip install pygame", Colors.INFO
                        )
            except Exception as e:
                if dep != "pyinstaller":
                    print_warning(f"  ⚠ {dep.upper()} - Error verificando: {e}")

        # 3. Verificar Python y sistema
        print_color("\n🐍 Información del sistema:", Colors.TITLE)
        print_color(f"   Python: {sys.version.split()[0]}", Colors.INFO)
        print_color(
            f"   Plataforma: {platform.system()} {platform.release()}", Colors.INFO
        )
        print_color(f"   Arquitectura: {platform.machine()}", Colors.INFO)

        # 4. Verificar si estamos en entorno virtual
        print_color("\n🌐 Entorno:", Colors.TITLE)
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )
        if in_venv:
            print_success("   ✓ Entorno virtual activado")
        else:
            print_warning("   ⚠ No estás en un entorno virtual (recomendado)")

        # 5. Recomendaciones
        print_color("\n💡 RECOMENDACIONES:", Colors.TITLE)
        if Path("requirements.txt").exists():
            print_color(
                "   Tienes requirements.txt. Puedes instalar todo con:", Colors.INFO
            )
            print_color("   pip install -r requirements.txt", Colors.VALUE)
        else:
            print_color(
                "   Si hay problemas, instala los paquetes manualmente:", Colors.INFO
            )
            print_color("   pip install pyinstaller pillow pygame", Colors.VALUE)

        print_success("\n✅ Verificación completada")

    except Exception as e:
        print_error(f"❌ Error durante la verificación: {e}")

    input(f"\n{Colors.INFO}Presiona Enter para continuar...{Colors.RESET}")


# ============================================================================
# MENÚ PRINCIPAL COMPLETO CON TODAS TUS OPCIONES + LAS NUEVAS
# ============================================================================


def menu_principal():
    """Menú principal COMPLETO con todas tus opciones"""
    usar_upx = False

    while True:
        print_header("COMPILADOR METALWAR")

        # Mostrar estado UPX actual
        estado_upx = "✅ ACTIVADO" if usar_upx else "🚫 DESACTIVADO"
        color_upx = Colors.GREEN if usar_upx else Colors.RED
        print_color(f"UPX: {estado_upx} (para evitar antivirus)", color_upx)

        # Mostrar estado de archivos importantes
        tiene_logo = Path("logo.png").exists()
        tiene_icono = Path("icon.ico").exists()
        tiene_splash = Path("splash.png").exists()

        print_color("\n📁 ARCHIVOS:", Colors.TITLE)
        print_color(
            f"  logo.png: {'✅ PRESENTE' if tiene_logo else '🚫 FALTANTE'}",
            Colors.GREEN if tiene_logo else Colors.RED,
        )
        print_color(
            f"  icon.ico: {'✅ PRESENTE' if tiene_icono else '🚫 FALTANTE'}",
            (
                Colors.GREEN
                if tiene_icono
                else Colors.YELLOW if tiene_logo else Colors.RED
            ),
        )
        print_color(
            f"  splash.png: {'✅ PRESENTE' if tiene_splash else '🚫 FALTANTE'}",
            Colors.GREEN if tiene_splash else Colors.YELLOW,
        )

        # TODAS TUS OPCIONES ORIGINALES RE-NUMERADAS
        print_color("\n1. Ver configuración", Colors.OPTION)
        print_color("2. Editar configuración", Colors.OPTION)
        print_color("3. Editar información de versión", Colors.OPTION)
        print_color("4. Ver recursos", Colors.OPTION)
        print_color("5. COMPILAR PROYECTO (.spec)", Colors.OPTION + Colors.BOLD)
        print_color("6. Crear solo .spec", Colors.OPTION)
        print_color("7. 🎨 Crear icon.ico desde logo.png", Colors.MAGENTA)
        print_color(
            "8. 🎨 GENERAR SPLASH SCREEN (11 estilos disponibles)",
            Colors.CYAN + Colors.BOLD + Colors.UNDERLINE,
        )
        print_color(
            f"9. Configurar UPX (ahora: {'ACTIVADO' if usar_upx else 'DESACTIVADO'})",
            Colors.OPTION,
        )
        print_color("10. Reparar config.py", Colors.OPTION)
        print_color("11. Probar splash.png", Colors.OPTION)
        print_color(
            "12. 🔧 Verificar dependencias PyInstaller", Colors.YELLOW + Colors.BOLD
        )
        print_color("13. Salir", Colors.OPTION)

        opcion = input("\nOpción (1-13): ").strip()

        if opcion == "1":
            config = leer_config()
            if config:
                mostrar_config_actual(config)
            else:
                print_warning("No se pudo leer la configuración")

        elif opcion == "2":
            config = leer_config()
            if not config:
                print_warning("No hay configuración. Creando nueva...")
                config = {}

            print_header("EDITAR CONFIGURACIÓN")

            campos = [
                ("GAME_NAME_DISPLAY", None, "Nombre del juego", False),
                ("GAME_FOLDER_NAME", None, "Carpeta de instalación", False),
                ("WINDOW_CAPTION", None, "Título de ventana", False),
                ("SCROLLER_MESSAGE", None, "Mensaje del scroller", False),
                ("SUBTITLE_DISPLAY", None, "Subtítulo", False),
                ("SPANISH_TEXT", None, "Texto español", False),
                ("WINDOW_SIZE", None, "Resolución (ancho,alto)", True),  # Es tupla
                ("FPS", None, "FPS", False),
                ("IDLE_TIMEOUT", None, "Tiempo inactividad", False),
                # Nuevos campos para SPAIN_TEXT dentro de COLORS
                ("SPANISH_TEXT_SCALE", "COLORS", "Escala texto español", False),
                ("SUBTITLE_SCALE", "COLORS", "Escala subtítulo", False),
                ("FLAG_RED", "COLORS", "Color rojo bandera (tupla RGB)", True),
                ("FLAG_YELLOW", "COLORS", "Color amarillo bandera (tupla RGB)", True),
                ("WAVE_SPEED", "COLORS", "Velocidad de onda animación", False),
                ("WAVE_AMPLITUDE", "COLORS", "Amplitud de onda", False),
                ("ROTATION_MAX", "COLORS", "Rotación máxima caracteres", False),
            ]

            for i, (clave, seccion, desc, es_tupla) in enumerate(campos, 1):
                print_color(f"{i}. {desc}", Colors.OPTION)

            print_color("0. Volver", Colors.OPTION)

            try:
                sel = int(input("\nSeleccionar: "))
                if sel == 0:
                    continue
                elif 1 <= sel <= len(campos):
                    clave, seccion, desc, es_tupla = campos[sel - 1]
                    if editar_campo(config, clave, seccion, es_tupla):
                        guardar_config(config)
                else:
                    print_error("Opción inválida")
            except:
                print_error("Entrada inválida")

        elif opcion == "3":
            editar_version_info()

        elif opcion == "4":
            listar_recursos()

        elif opcion == "5":
            print_header("COMPILAR PROYECTO (.spec)")

            # Verificar archivos esenciales
            esenciales = ["main.py", "config.py"]
            faltan = []
            for archivo in esenciales:
                if not Path(archivo).exists():
                    faltan.append(archivo)

            if faltan:
                print_error(f"Faltan: {', '.join(faltan)}")
                continue

            # Leer configuración
            config = leer_config()
            if not config:
                print_warning("No se pudo leer config.py")
                print_color(
                    "¿Usar valores por defecto? (s/n): ", Colors.WARNING, end=""
                )
                if input().strip().lower() in ["s", "si", "sí"]:
                    config = {"GAME_NAME_DISPLAY": "MetalWar"}
                else:
                    continue

            # Crear spec con UPX actual
            spec = crear_spec(config, usar_upx)
            if not spec:
                continue

            # Confirmar
            print_color(f"\n📦 Archivo .spec: {spec}", Colors.INFO)
            print_color("¿Compilar ahora? (s/n): ", Colors.WARNING, end="")
            if input().strip().lower() in ["s", "si", "sí"]:
                compilar_proyecto(spec)

        elif opcion == "6":
            print_header("CREAR SOLO .spec")

            # Verificar archivos esenciales
            if not Path("main.py").exists():
                print_error("main.py no encontrado")
                continue

            # Leer configuración o usar valores por defecto
            config = leer_config()
            if not config:
                print_warning("No se pudo leer config.py")
                print_color(
                    "¿Usar valores por defecto? (s/n): ", Colors.WARNING, end=""
                )
                if input().strip().lower() in ["s", "si", "sí"]:
                    config = {"GAME_NAME_DISPLAY": "MetalWar"}
                else:
                    continue

            # Crear spec con UPX actual
            spec = crear_spec(config, usar_upx)
            if spec:
                print_color(f"\n📄 Archivo .spec creado: {spec}", Colors.SUCCESS)
                print_color(
                    "Puedes editarlo manualmente o usar la opción 5 para compilar",
                    Colors.INFO,
                )
            else:
                print_error("No se pudo crear el archivo .spec")

        elif opcion == "7":
            crear_icono_desde_logo()

        elif opcion == "8":
            # FUSIONADO: TODOS los generadores de splash en un solo menú
            print_header("🎨 GENERADOR DE SPLASH SCREEN")
            print_color("🎯 11 ESTILOS DISPONIBLES", Colors.INFO)
            print_color(
                "📏 Todos en 600x400 pixels (óptimo para PyInstaller)", Colors.INFO
            )

            print_color("\n🎨 ELIGE UN ESTILO:", Colors.TITLE + Colors.BOLD)

            # GRUPO 1: Generadores simplificados (5 opciones)
            print_color("\n🌀 SIMPLIFICADOS (rápidos):", Colors.CYAN)
            print_color("  1. 🌀 Lite - Minimalista profesional", Colors.CYAN)
            print_color("  2. 🤖 Industrial Muthafuck@ed - Cyberpunk", Colors.MAGENTA)
            print_color("  3. 🎸 Brutal - Heavy metal", Colors.RED)
            print_color("  4. 🎲 Random Madness - Aleatorio", Colors.YELLOW)
            print_color("  5. 👾 Pixel Terror - 8-bit", Colors.GRAY)

            # GRUPO 2: DemosceneFactory clásicos (3 opciones - versión simplificada)
            print_color("\n🎭 DEMOSCENE CLÁSICOS:", Colors.GREEN)
            print_color("  6. ⚡ Plasma Core - Matemática procedural", Colors.BLUE)
            print_color("  7. 🎛️ Copper Bars - Estilo Amiga/C64", Colors.GREEN)
            print_color("  8. 🌌 Synthwave Grid - Neón 80s", Colors.CYAN)

            # GRUPO 3: DemosceneFactory PRO (3 opciones - versión completa)
            print_color("\n✨ DEMOSCENE PRO (completos):", Colors.MAGENTA + Colors.BOLD)
            print_color(
                "  9. ⚡ Plasma Core PRO - Con efectos CRT completos", Colors.BLUE
            )
            print_color(
                "  10. 🎛️ Copper Bars PRO - Con subtítulo específico", Colors.GREEN
            )
            print_color("  11. 🌌 Synthwave Grid PRO - Con neón y grid", Colors.CYAN)

            print_color("\n  0. ↩️  Volver", Colors.OPTION)

            estilo = input("\nEstilo (0-11): ").strip()

            if estilo == "0":
                continue

            if Path("splash.png").exists():
                print_warning("⚠  Ya existe splash.png")
                print_color("¿Sobrescribir? (s/n): ", Colors.WARNING, end="")
                if input().strip().lower() not in ["s", "si", "sí"]:
                    continue

            # Obtener nombre del producto
            product_name = obtener_nombre_producto()

            # DICCIONARIO DE GENERADORES SIMPLIFICADOS (estilos 1-5)
            generadores_simplificados = {
                "1": generar_splash_lite,
                "2": Industrial_muthafuckaed,
                "3": generar_splash_brutal,
                "4": generar_splash_random_madness,
                "5": generar_splash_pixel_terror,
            }

            # GENERADORES DEMOSCENE (estilos 6-11)
            if estilo in generadores_simplificados:
                # Ejecutar generador simplificado (estilos 1-5)
                generadores_simplificados[estilo]()

            elif estilo in ["6", "7", "8", "9", "10", "11"]:
                # Configurar factory Demoscene
                factory = DemosceneFactory(width=600, height=400)

                # Determinar tipo y subtítulo según el estilo
                if estilo == "6":  # Plasma Core (simplificado)
                    img = factory.generar_plasma(product_name, "PLEASE WAIT...")
                    print_success("✅ Plasma Core generado (versión simplificada)")

                elif estilo == "7":  # Copper Bars (simplificado)
                    img = factory.generar_copper(product_name, "PLEASE WAIT...")
                    print_success("✅ Copper Bars generado (versión simplificada)")

                elif estilo == "8":  # Synthwave Grid (simplificado)
                    img = factory.generar_synthwave(product_name, "PLEASE WAIT...")
                    print_success("✅ Synthwave Grid generado (versión simplificada)")

                elif estilo == "9":  # Plasma Core PRO
                    img = factory.generar_plasma(
                        product_name, "> Loading Resources... Please Wait"
                    )
                    print_success("✅ Plasma Core PRO generado")

                elif estilo == "10":  # Copper Bars PRO
                    img = factory.generar_copper(
                        product_name, "> Initializing System... Please Wait"
                    )
                    print_success("✅ Copper Bars PRO generado")

                elif estilo == "11":  # Synthwave Grid PRO
                    img = factory.generar_synthwave(
                        product_name, "> Unpacking Assets... Please Wait"
                    )
                    print_success("✅ Synthwave Grid PRO generado")

                # Guardar imagen
                quality = 95 if estilo in ["9", "10", "11"] else 85
                img.save("splash.png", "PNG", optimize=True, quality=quality)

                # Mostrar información adicional para versiones PRO
                if estilo in ["9", "10", "11"]:
                    nombres_pro = {
                        "9": "Plasma Core PRO",
                        "10": "Copper Bars PRO",
                        "11": "Synthwave Grid PRO",
                    }
                    print_color(f"\n📄 Archivo: splash.png", Colors.CYAN)
                    print_color(f"📏 Tamaño: 600x400 pixels", Colors.INFO)
                    print_color(f"🎨 Tema: {nombres_pro[estilo]}", Colors.INFO)
                    print_color(
                        f"✨ Efectos: CRT Scanlines + RGB Shift + Vignette",
                        Colors.GREEN,
                    )

                    # Preguntar si ver el splash
                    print_color(
                        "\n¿Ver el splash generado? (s/n): ", Colors.WARNING, end=""
                    )
                    if input().strip().lower() in ["s", "si", "sí"]:
                        try:
                            from PIL import Image

                            img.show()
                        except:
                            print_info(
                                "(No se pudo mostrar la imagen, pero se guardó correctamente)"
                            )

            else:
                print_error("❌ Opción inválida")

        elif opcion == "9":
            # Configurar UPX
            print_header("CONFIGURAR UPX")
            print_color(
                f"\nUPX actualmente: {'✅ ACTIVADO' if usar_upx else '🚫 DESACTIVADO'}",
                Colors.GREEN if usar_upx else Colors.RED,
            )
            print_color("\n⚠  IMPORTANTE:", Colors.YELLOW + Colors.BOLD)
            print_color(
                "• UPX ACTIVADO: Ejecutable más pequeño, pero puede causar", Colors.INFO
            )
            print_color(
                "  falsos positivos en antivirus (recomendado para test interno)",
                Colors.INFO,
            )
            print_color(
                "• UPX DESACTIVADO: Ejecutable más grande, pero menos problemas",
                Colors.INFO,
            )
            print_color("  con antivirus (recomendado para distribución)", Colors.INFO)

            print_color(
                "\n¿Activar UPX? (s=activar/n=desactivar [Enter para mantener]): ",
                Colors.WARNING,
                end="",
            )
            respuesta = input().strip().lower()

            if respuesta == "s":
                usar_upx = True
                print_success("✅ UPX ACTIVADO")
            elif respuesta == "n":
                usar_upx = False
                print_success("🚫 UPX DESACTIVADO")
            else:
                print_info("UPX no modificado")

        elif opcion == "10":
            print_header("REPARAR CONFIG.PY")
            print_color("¿Reparar config.py? (s/n): ", Colors.WARNING, end="")
            if input().strip().lower() in ["s", "si", "sí"]:
                reparar_config()

        elif opcion == "11":
            probar_splash()

        elif opcion == "12":
            verificar_dependencias()

        elif opcion == "13":
            print_color("\n¡Hasta luego! 🎮", Colors.TITLE)
            break

        else:
            print_error("Opción inválida")

        if opcion != "13":
            input("\nEnter para continuar...")


# ============================================================================
# INICIO DEL PROGRAMA
# ============================================================================

if __name__ == "__main__":
    # Limpiar pantalla
    os.system("cls" if os.name == "nt" else "clear")

    print_color("╔══════════════════════════════════════════════════════╗", Colors.CYAN)
    print_color(
        "║                COMPILADOR METALWAR                   ║",
        Colors.MAGENTA + Colors.BOLD,
    )
    print_color("║               (Para PyInstaller)                     ║", Colors.CYAN)
    print_color(
        "║         VERSIÓN COMPLETA CON SPLASH UNIFICADO        ║",
        Colors.GREEN + Colors.BOLD,
    )
    print_color("╚══════════════════════════════════════════════════════╝", Colors.CYAN)

    # Verificar archivos
    if not Path("main.py").exists():
        print_warning("main.py no encontrado")

    if not Path("config.py").exists():
        print_warning("config.py no encontrado")
        print_color(
            "Se creará uno automáticamente al editar configuración", Colors.INFO
        )

    # Verificar archivos gráficos
    tiene_logo = Path("logo.png").exists()
    tiene_icono = Path("icon.ico").exists()
    tiene_splash = Path("splash.png").exists()

    if not tiene_logo:
        print_warning("logo.png no encontrado (necesario para crear iconos)")

    if not tiene_icono and tiene_logo:
        print_warning("icon.ico no encontrado")
        print_color("Usa la opción 7 para crear icon.ico desde logo.png", Colors.INFO)
    elif not tiene_icono:
        print_warning("icon.ico no encontrado")

    if not tiene_splash:
        print_warning("splash.png no encontrado")
        print_color("Usa la opción 8 para generar splash (11 estilos)", Colors.INFO)
    else:
        print_color("✅ splash.png encontrado", Colors.GREEN)

    print_color("\n🎨 OPCIÓN 8 UNIFICADA:", Colors.CYAN + Colors.BOLD)
    print_color("   11 generadores de splash en 3 categorías:", Colors.INFO)
    print_color("   • Simplificados (rápidos)", Colors.INFO)
    print_color("   • Demoscene clásicos (procedurales)", Colors.INFO)
    print_color("   • Demoscene PRO (completos con efectos)", Colors.INFO)

    # Ejecutar menú
    try:
        menu_principal()
    except KeyboardInterrupt:
        print_color("\n\nInterrumpido", Colors.YELLOW)
    except Exception as e:
        print_error(f"Error: {e}")
        input("\nEnter para salir...")
