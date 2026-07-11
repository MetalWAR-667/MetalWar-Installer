#!/usr/bin/env python3
# CompileGUI_v3.py
# Herramienta gráfica para compilar INSTALADOR DEMOSCENE con PyInstaller
# By MetalWAR - I relied on Deepseek & Gemini to create this shit.
# CORRECCIÓN: Solucionado error "unhashable type StringVar"

import os
import sys
import re
import ast
import time
import subprocess
import threading
import random
import math
import glob
import shutil
from pathlib import Path

# Intentar importar dependencias
try:
    import customtkinter as ctk
    from tkinter import messagebox
    from PIL import (
        Image,
        ImageTk,
        ImageDraw,
        ImageFont,
        ImageFilter,
        ImageChops,
        ImageEnhance,
    )
except ImportError as e:
    print("Error: Faltan librerías. Ejecuta: pip install customtkinter pillow")
    sys.exit(1)

# Configuración visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ============================================================================
# FUNCIONES DE CONFIGURACIÓN DE COMPILE.PY (COPIAS EXACTAS)
# ============================================================================


def leer_config():
    """Lee config.py y devuelve GAME_CONFIG"""
    try:
        if not Path("config.py").exists():
            return None

        with open("config.py", "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r"GAME_CONFIG\s*=\s*({.*?})\s*(?:\n|$)", content, re.DOTALL)
        if match:
            try:
                config_str = match.group(1)
                config = ast.literal_eval(config_str)
                return config
            except:
                return None

        return None

    except Exception as e:
        print(f"❌ Error leyendo config: {e}")
        return None


def guardar_config(config):
    """Guarda la configuración en config.py"""
    try:
        if Path("config.py").exists():
            shutil.copy2("config.py", "config.py.backup")

        config_completo = {
            "GAME_FOLDER_NAME": config.get("GAME_FOLDER_NAME", "CARPETA DEL JUEGO"),
            "GAME_NAME_DISPLAY": config.get("GAME_NAME_DISPLAY", "TITULO DEL JUEGO"),
            "WINDOW_CAPTION": config.get("WINDOW_CAPTION", "MetalWar - Instalador"),
            "SCROLLER_MESSAGE": config.get(
                "SCROLLER_MESSAGE", ">>> METALWAR LOADING... SYSTEM INITIALIZED >>>"
            ),
            "SUBTITLE_DISPLAY": config.get("SUBTITLE_DISPLAY", ""),
            "SPANISH_TEXT": config.get("SPANISH_TEXT", "In Awesome Spanish"),
            "WINDOW_SIZE": config.get("WINDOW_SIZE", (800, 600)),
            "FPS": config.get("FPS", 60),
            "IDLE_TIMEOUT": config.get("IDLE_TIMEOUT", 20.0),
            "POST_INSTALL": config.get(
                "POST_INSTALL",
                {
                    "ENABLED": False,
                    "PATCHER_EXE": "example.exe",
                    "TARGET_FILE": "catalog.json",
                    "ARGUMENT": "patchcrc",
                },
            ),
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
                },
            ),
            "AUDIO": config.get("AUDIO", {"BPM": 128, "MUSIC_OFFSET": 0.12}),
            "BPM_EFFECT": config.get(
                "BPM_EFFECT", {"IN_NORMAL_MODE": False, "IN_RAVE_MODE": True}
            ),
        }

        contenido = """# config.py
# Configuración principal del juego MetalWar
# Contiene todos los parámetros ajustables del sistema

GAME_CONFIG = {
"""

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
                if len(valor) == 2:
                    return f"({valor[0]}, {valor[1]})"
                elif len(valor) == 4:
                    return f"({valor[0]}, {valor[1]}, {valor[2]}, {valor[3]})"
                elif len(valor) == 3:
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

        contenido += "}\n"

        with open("config.py", "w", encoding="utf-8") as f:
            f.write(contenido)

        print("✅ config.py guardado correctamente")
        return True

    except Exception as e:
        print(f"❌ Error al guardar config.py: {e}")
        if Path("config.py.backup").exists():
            try:
                shutil.copy2("config.py.backup", "config.py")
                print("✅ Restaurado desde backup")
            except:
                pass
        return False


# ============================================================================
# CLASE DEMOSCENE FACTORY (Lógica Original)
# ============================================================================
class DemosceneFactory:
    def __init__(self, width=600, height=400):
        self.w = width
        self.h = height
        random.seed(time.time())

    def _get_font(self, size):
        font_candidates = [
            "Seldom Scene.otf",
            "Arial Black.ttf",
            "Impact.ttf",
            "Verdana.ttf",
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
                r, g, b = min(255, i * 2), min(255, i), 0
            elif mode == "ice":
                r, g, b = int(i / 4), min(255, i + 50), min(255, i * 2 + 50)
            elif mode == "toxic":
                r, g, b = (
                    int(128 + 127 * math.sin(i * math.pi / 32)),
                    255,
                    int(128 + 127 * math.cos(i * math.pi / 32)),
                )
            elif mode == "royal":
                r, g, b = min(255, i * 2), min(255, i // 2), min(255, i + 50)
            elif mode == "alien":
                r, g, b = (
                    0,
                    int(128 + 127 * math.sin(i * 0.1)),
                    int(128 + 127 * math.cos(i * 0.1)),
                )
            else:  # candy
                r, g, b = (
                    int(128 + 127 * math.sin(i * 0.05)),
                    int(128 + 127 * math.sin(i * 0.05 + 2)),
                    int(128 + 127 * math.sin(i * 0.05 + 4)),
                )
            palette.append((r, g, b))
        return palette

    def _apply_crt_effect(self, img):
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for y in range(0, img.height, 3):
            draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, 80), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        r, g, b = img.split()
        r = ImageChops.offset(r, -3, 0)
        b = ImageChops.offset(b, 3, 0)
        img = Image.merge("RGB", (r, g, b))
        glow = img.filter(ImageFilter.GaussianBlur(12))
        img = ImageChops.screen(img, ImageEnhance.Brightness(glow).enhance(1.3))
        return img

    def _generate_chrome_text(self, text, size=80):
        # 1. PRUEBA con tamaño solicitado
        font_test = self._get_font(size)
        draw_test = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        bbox_test = draw_test.textbbox((0, 0), text, font=font_test)
        text_width = bbox_test[2] - bbox_test[0]

        # 2. AUTO-AJUSTE HORIZONTAL (igual que en dibujar_texto_gigante)
        ancho_maximo = self.w * 0.85  # 85% del ancho total
        print(f"   🔍 Chrome text: '{text}' a {size}px, ancho: {text_width}px")

        if text_width > ancho_maximo:
            # Calcular nuevo tamaño proporcional
            ratio = ancho_maximo / text_width
            nuevo_size = int(size * ratio)

            # Tamaño mínimo de 40px
            nuevo_size = max(40, nuevo_size)

            print(f"   ⚠  Texto muy ancho, reduciendo a {nuevo_size}px")
            print(f"   📏 Ratio de reducción: {ratio:.2f}")
            size = nuevo_size

            # Recargar fuente con nuevo tamaño
            font_test = self._get_font(size)
            bbox_test = draw_test.textbbox((0, 0), text, font=font_test)
            text_width = bbox_test[2] - bbox_test[0]

        # 3. Continuar con el resto del código original...
        font = self._get_font(size)
        mask = Image.new("L", (self.w, self.h), 0)
        draw_m = ImageDraw.Draw(mask)
        bbox = draw_m.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx, ty = (self.w - tw) // 2, (self.h - th) // 2
        draw_m.text((tx, ty), text, font=font, fill=255)

        gradient = Image.new("RGB", (self.w, self.h), (0, 0, 0))
        draw_g = ImageDraw.Draw(gradient)
        horizon = ty + th // 2 + random.randint(-10, 10)
        for y in range(ty, ty + th):
            if y < horizon:
                draw_g.line([(tx, y), (tx + tw, y)], fill=(0, 0, 100))
            else:
                draw_g.line([(tx, y), (tx + tw, y)], fill=(255, 215, 0))

        chrome = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        chrome.paste(gradient, (0, 0), mask)

        shadow = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        draw_s = ImageDraw.Draw(shadow)
        draw_s.text((tx + 4, ty + 4), text, font=font, fill=(0, 0, 0, 180))
        return Image.alpha_composite(shadow, chrome)

    def generar_plasma(self, title, subtitle="Loading..."):
        palette = self._random_palette()
        plasma = Image.new("RGB", (240, 135))
        pixels = plasma.load()
        offset = random.randint(0, 1000)
        for y in range(135):
            for x in range(240):
                val = (math.sin(x / 30 + offset) + math.sin(y / 20 + offset)) * 64 + 128
                pixels[x, y] = palette[int(val) % 256]
        bg = plasma.resize((self.w, self.h), Image.Resampling.BILINEAR)
        chrome = self._generate_chrome_text(title, size=70)
        bg.paste(chrome, (0, 0), chrome)
        return self._apply_crt_effect(bg)

    def generar_copper(self, title, subtitle="Init..."):
        bg = Image.new("RGB", (self.w, self.h), (10, 10, 20))
        draw = ImageDraw.Draw(bg)
        for i in range(10):
            y = random.randint(0, self.h)
            draw.line(
                [(0, y), (self.w, y)],
                fill=(random.randint(50, 255), 0, 0),
                width=random.randint(5, 20),
            )
        chrome = self._generate_chrome_text(title, size=80)
        bg.paste(chrome, (0, 0), chrome)
        return self._apply_crt_effect(bg)

    def generar_synthwave(self, title, subtitle="Booting..."):
        bg = Image.new("RGB", (self.w, self.h), (20, 0, 40))
        draw = ImageDraw.Draw(bg)
        for i in range(0, self.h, 20):
            draw.line(
                [(0, self.h / 2 + i * 2), (self.w, self.h / 2 + i * 2)],
                fill=(0, 255, 255),
            )
        for i in range(-self.w, self.w * 2, 40):
            draw.line([(i, self.h), (self.w // 2, self.h // 2)], fill=(255, 0, 255))
        chrome = self._generate_chrome_text(title, size=70)
        bg.paste(chrome, (0, 0), chrome)
        return self._apply_crt_effect(bg)


# ============================================================================
# UTILIDAD: REDIRIGIR CONSOLA
# ============================================================================
class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", string)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass


# ============================================================================
# APP PRINCIPAL - DISEÑO MEJORADO
# ============================================================================
class MetalWarCompilerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de ventana
        self.title("Compilador MetalWar - Suite de Desarrollo")
        self.geometry("1280x800")
        self.minsize(1200, 700)

        # Estilo global
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Variables Globales
        self.config_data = {}

        # Variables para Version Info
        self.v_product = ctk.StringVar(value="MetalWar")
        self.v_company = ctk.StringVar(value="MyStudio")
        self.v_desc = ctk.StringVar(value="Game Executable")
        self.v_file_ver = ctk.StringVar(value="1.0.0.0")
        self.v_prod_ver = ctk.StringVar(value="1.0.0.0")
        self.v_copyright = ctk.StringVar(value="Copyright 2024")
        self.v_filename = ctk.StringVar(value="MetalWar.exe")
        self.v_internal = ctk.StringVar(value="METALWAR")

        # Variables de configuración
        self.usar_upx = ctk.BooleanVar(value=False)
        self.uac_var = ctk.BooleanVar(value=True)

        # Configurar grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- BARRA LATERAL IZQUIERDA ---
        self.sidebar = ctk.CTkFrame(
            self, width=220, corner_radius=0, fg_color="#1a1a1a"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)

        # Logo / Título
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=140)
        title_frame.pack(fill="x", pady=(25, 15), padx=20)
        title_frame.pack_propagate(False)

        # Cargar logo si existe
        self.logo_image = None
        if Path("logo.png").exists():
            try:
                logo_pil = Image.open("logo.png")
                logo_pil.thumbnail((80, 80), Image.Resampling.LANCZOS)
                self.logo_image = ctk.CTkImage(
                    light_image=logo_pil, dark_image=logo_pil, size=(80, 80)
                )
                ctk.CTkLabel(title_frame, image=self.logo_image, text="").pack(
                    pady=(0, 15)
                )
            except Exception as e:
                print(f"⚠️ Error cargando logo: {e}")
                ctk.CTkLabel(
                    title_frame,
                    text="🛠️",
                    font=ctk.CTkFont(size=45),
                    text_color="#4dabf7",
                ).pack(pady=(0, 15))
        else:
            ctk.CTkLabel(
                title_frame, text="🛠️", font=ctk.CTkFont(size=45), text_color="#4dabf7"
            ).pack(pady=(0, 15))

        ctk.CTkLabel(
            title_frame,
            text="Compilador\nMetalWar",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff",
            justify="center",
        ).pack()

        # Separador
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#333333").pack(
            fill="x", padx=25, pady=10
        )

        # Navegación
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15, pady=10)

        self.nav_buttons = {}
        nav_items = [
            ("📊", "Panel Principal", "dashboard"),
            ("⚙️", "Configuración", "config"),
            ("📝", "Información de Versión", "version"),
            ("🎨", "Generador de Assets", "assets"),
            ("🚀", "Compilar Proyecto", "compile"),
        ]

        for icon, text, frame_name in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"  {icon}  {text}",
                anchor="w",
                font=ctk.CTkFont(size=14),
                height=45,
                fg_color="transparent",
                hover_color="#2d2d2d",
                text_color="#cccccc",
                border_width=0,
                corner_radius=8,
                command=lambda fn=frame_name: self.select_frame(fn),
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[frame_name] = btn

        # Separador inferior
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#333333").pack(
            fill="x", padx=25, pady=(20, 5)
        )

        # Estado del sistema
        status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        status_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            status_frame,
            text="Estado del Sistema",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#888888",
        ).pack(anchor="w", pady=(0, 10))

        self.system_status = ctk.CTkLabel(
            status_frame,
            text="✅ Listo",
            text_color="#4CAF50",
            font=ctk.CTkFont(size=11),
        )
        self.system_status.pack(anchor="w")

        # --- ÁREA PRINCIPAL ---
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f0f0f")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Barra superior
        self.top_bar = ctk.CTkFrame(
            self.main_container, height=60, fg_color="#1a1a1a", corner_radius=0
        )
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.top_bar.grid_columnconfigure(0, weight=1)
        self.top_bar.grid_propagate(False)

        self.current_title = ctk.CTkLabel(
            self.top_bar,
            text="Panel Principal",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff",
        )
        self.current_title.grid(row=0, column=0, sticky="w", padx=30, pady=0)

        # Área de contenido
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        # Crear frames
        self.frames = {}
        self.create_dashboard_frame()
        self.create_config_frame()
        self.create_version_frame()
        self.create_assets_frame()
        self.create_compile_frame()

        # Carga inicial - AHORA DESPUÉS de crear todos los frames
        self.load_config_file()
        self.load_version_info()
        self.check_files_status()
        self.select_frame("dashboard")
        self.update_system_status()

    def select_frame(self, name):
        """Cambia entre frames y actualiza la navegación"""
        # Ocultar todos los frames
        for frame in self.frames.values():
            frame.grid_forget()

        # Mostrar frame seleccionado
        self.frames[name].grid(row=0, column=0, sticky="nsew")

        # Actualizar título
        titles = {
            "dashboard": "Panel Principal",
            "config": "Configuración del Juego",
            "version": "Información de Versión",
            "assets": "Generador de Assets",
            "compile": "Compilar Proyecto",
        }
        self.current_title.configure(text=titles.get(name, "Panel"))

        # Actualizar botones de navegación
        for frame_name, btn in self.nav_buttons.items():
            if frame_name == name:
                btn.configure(fg_color="#2d2d2d", text_color="#4dabf7")
            else:
                btn.configure(fg_color="transparent", text_color="#cccccc")

    def update_system_status(self):
        """Actualiza el estado del sistema en la barra lateral"""
        essential_files = ["main.py", "config.py"]
        missing = [f for f in essential_files if not Path(f).exists()]

        if missing:
            self.system_status.configure(
                text=f"⚠️ Faltan {len(missing)} archivos", text_color="#FFA726"
            )
        else:
            self.system_status.configure(text="✅ Sistema listo", text_color="#4CAF50")

    # ------------------------------------------------------------------------
    # 1. PANEL PRINCIPAL - DISEÑO MEJORADO (MISMO TEXTO)
    # ------------------------------------------------------------------------
    def create_dashboard_frame(self):
        f = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.frames["dashboard"] = f

        # Encabezado
        header_frame = ctk.CTkFrame(f, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 25))

        ctk.CTkLabel(
            header_frame,
            text="📊 VISTA PREVIA",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#ffffff",
        ).pack(side="left", anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Estado de archivos esenciales y recursos detectados",
            font=ctk.CTkFont(size=14),
            text_color="#888888",
        ).pack(side="left", anchor="w", padx=(20, 0))

        # Tarjeta de archivos esenciales
        files_card = ctk.CTkFrame(
            f,
            corner_radius=12,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
        )
        files_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            files_card,
            text="📁 ARCHIVOS ESENCIALES:",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        ).pack(anchor="w", padx=25, pady=(20, 15))

        # Grid para archivos (2 columnas)
        files_grid = ctk.CTkFrame(files_card, fg_color="transparent")
        files_grid.pack(fill="x", padx=25, pady=(0, 15))

        self.lbl_files = {}
        archivos_esenciales = [
            ("main.py", "Script principal del juego"),
            ("config.py", "Configuración del juego"),
            ("version_info.txt", "Información de versión (.exe)"),
            ("logo.png", "Logo para crear iconos"),
            ("icon.ico", "Icono de la aplicación"),
            ("splash.png", "Pantalla de carga inicial"),
            ("effects.py", "Efectos visuales del juego"),
            ("installer.py", "Sistema de instalación"),
            ("audio.py", "Sistema de audio"),
            ("ui.py", "Interfaz de usuario"),
            ("utils.py", "Utilidades adicionales"),
        ]

        # Crear dos columnas
        left_col = ctk.CTkFrame(files_grid, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 20))

        right_col = ctk.CTkFrame(files_grid, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)

        columns = [left_col, right_col]

        for i, (archivo, descripcion) in enumerate(archivos_esenciales):
            col = columns[i % 2]

            file_row = ctk.CTkFrame(col, fg_color="transparent", height=38)
            file_row.pack(fill="x", pady=2)
            file_row.pack_propagate(False)

            # Nombre y descripción
            text_frame = ctk.CTkFrame(file_row, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                text_frame,
                text=archivo,
                anchor="w",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#cccccc",
            ).pack(anchor="w")

            ctk.CTkLabel(
                text_frame,
                text=descripcion,
                anchor="w",
                font=ctk.CTkFont(size=11),
                text_color="#888888",
            ).pack(anchor="w")

            # Estado
            lbl = ctk.CTkLabel(
                file_row,
                text="...",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=100,
                anchor="e",
            )
            lbl.pack(side="right", padx=(10, 0))
            self.lbl_files[archivo] = lbl

        # Botón de refrescar
        refresh_btn = ctk.CTkButton(
            files_card,
            text="🔄 REFRESCAR LISTA DE RECURSOS",
            command=self.check_files_status,
            height=40,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            border_width=1,
            border_color="#444444",
        )
        refresh_btn.pack(pady=(0, 25), padx=25, fill="x")

        # Tarjeta de recursos
        resources_card = ctk.CTkFrame(
            f,
            corner_radius=12,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
        )
        resources_card.pack(fill="both", expand=True, pady=(0, 20))

        ctk.CTkLabel(
            resources_card,
            text="📋 LISTA DE RECURSOS DETECTADOS:",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        ).pack(anchor="w", padx=25, pady=(20, 15))

        # Área de texto para recursos
        self.res_txt = ctk.CTkTextbox(
            resources_card,
            font=("Consolas", 11),
            wrap="word",
            fg_color="#0f0f0f",
            border_width=1,
            border_color="#333333",
            corner_radius=8,
        )
        self.res_txt.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        self.res_txt.configure(state="disabled")

        # Configurar tags de colores
        self.setup_console_tags()

        # Pie de página
        footer_frame = ctk.CTkFrame(f, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(0, 10))

        left_info = ctk.CTkFrame(footer_frame, fg_color="transparent")
        left_info.pack(side="left", fill="x", expand=True)

        right_info = ctk.CTkFrame(footer_frame, fg_color="transparent")
        right_info.pack(side="right")

        ctk.CTkLabel(
            left_info,
            text="💡 Los recursos se incluirán automáticamente en la compilación",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#666666",
        ).pack(side="left")

        self.res_count_label = ctk.CTkLabel(
            right_info,
            text="📏 Total: 0 archivos (actualiza para ver)",
            font=ctk.CTkFont(size=12),
            text_color="#4dabf7",
        )
        self.res_count_label.pack(side="right")

    def setup_console_tags(self):
        """Configura los tags de colores para la consola"""
        self.res_txt.configure(state="normal")
        self.res_txt.tag_config("success", foreground="#4CAF50")
        self.res_txt.tag_config("error", foreground="#F44336")
        self.res_txt.tag_config("warning", foreground="#FF9800")
        self.res_txt.tag_config("info", foreground="#2196F3")
        self.res_txt.tag_config("highlight", foreground="#4dabf7")
        self.res_txt.configure(state="disabled")

    def check_files_status(self):
        """Verifica archivos y lista recursos - FUNCIÓN ORIGINAL CON MEJOR SALIDA VISUAL"""
        # Primero, actualizar estado de archivos esenciales
        for fname, lbl in self.lbl_files.items():
            if Path(fname).exists():
                lbl.configure(text="✅ ENCONTRADO", text_color="#4CAF50")
            else:
                if fname in ["main.py", "config.py"]:
                    lbl.configure(text="❌ FALTANTE", text_color="#F44336")
                else:
                    lbl.configure(text="⚠️  FALTANTE", text_color="#FF9800")

        # Ahora listar todos los recursos
        self.res_txt.configure(state="normal")
        self.res_txt.delete("1.0", "end")

        # Encabezado
        self.res_txt.insert("1.0", "📁 ARCHIVOS DE RECURSOS DETECTADOS\n", "highlight")
        self.res_txt.insert("end", "=" * 50 + "\n\n")

        # Tipos de archivos
        tipos = {
            "Python": ["*.py"],
            "Imágenes": ["*.png", "*.jpg", "*.ico", "*.jpeg", "*.bmp"],
            "Audio": [
                "*.mp3",
                "*.ogg",
                "*.wav",
                "*.flac",
                "*.mod",
                "*.xm",
                "*.s3m",
                "*.it",
                "*.stm",
                "*.mtm",
            ],
            "Datos": ["*.dat", "*.json", "*.txt", "*.xml"],
            "Ejecutables": ["*.exe", "*.dll"],
            "Fuentes": ["*.ttf", "*.otf"],
        }

        total = 0

        for tipo, patrones in tipos.items():
            archivos = []
            for patron in patrones:
                for f in Path(".").glob(patron):
                    if f.name not in [
                        "compilador.py",
                        "compile.py",
                        "Compiler_GUI.py",
                        "Compiler_GUI_v3.py",
                    ]:
                        archivos.append(f)

            if archivos:
                self.res_txt.insert("end", f"[{tipo.upper()}]\n", "info")

                for archivo in sorted(archivos):
                    tamaño = archivo.stat().st_size
                    if tamaño < 1024:
                        tamaño_str = f"{tamaño} B"
                    elif tamaño < 1024 * 1024:
                        tamaño_str = f"{tamaño/1024:.1f} KB"
                    else:
                        tamaño_str = f"{tamaño/(1024*1024):.1f} MB"

                    if archivo.name in [
                        "main.py",
                        "config.py",
                        "ui.py",
                        "utils.py",
                        "effects.py",
                        "audio.py",
                        "installer.py",
                    ]:
                        self.res_txt.insert("end", f"  ✅ {archivo.name} ", "success")
                    elif archivo.name in [
                        "icon.ico",
                        "splash.png",
                        "version_info.txt",
                        "logo.png",
                    ]:
                        self.res_txt.insert("end", f"  🎨 {archivo.name} ", "highlight")
                    elif archivo.suffix in [".mod", ".xm", ".s3m", ".it"]:
                        self.res_txt.insert("end", f"  🎵 {archivo.name} ", "highlight")
                    elif archivo.suffix in [".exe", ".dll"]:
                        self.res_txt.insert("end", f"  ⚙  {archivo.name} ", "info")
                    else:
                        self.res_txt.insert("end", f"  • {archivo.name} ")

                    self.res_txt.insert("end", f"({tamaño_str})\n")
                    total += 1

                self.res_txt.insert("end", "\n")

        # Resumen final
        self.res_txt.insert(
            "end", f"\n📊 TOTAL: {total} archivos de recursos\n", "highlight"
        )

        # Verificar archivos críticos
        archivos_criticos = {
            "main.py": "Script principal",
            "config.py": "Configuración del juego",
            "icon.ico": "Icono de la aplicación",
            "splash.png": "Pantalla de carga",
            "version_info.txt": "Información de versión",
            "effects.py": "Efectos visuales",
            "audio.py": "Sistema de audio",
            "ui.py": "Interfaz de usuario",
        }

        self.res_txt.insert("end", "\n🔍 VERIFICACIÓN DE ARCHIVOS CRÍTICOS:\n", "info")
        for archivo, desc in archivos_criticos.items():
            if Path(archivo).exists():
                self.res_txt.insert("end", f"  ✅ {desc}: {archivo}\n", "success")
            else:
                self.res_txt.insert(
                    "end", f"  ❌ {desc}: {archivo} NO ENCONTRADO\n", "error"
                )

        self.res_txt.configure(state="disabled")

        # Actualizar contador
        self.res_count_label.configure(text=f"📏 Total: {total} archivos")

        # Actualizar estado del sistema
        self.update_system_status()

        print("✅ Dashboard actualizado - Recursos listados")
        print(f"📊 Total de recursos: {total} archivos")

    # ------------------------------------------------------------------------
    # 2. CONFIG EDITOR - DISEÑO MEJORADO (MISMO TEXTO)
    # ------------------------------------------------------------------------
    def create_config_frame(self):
        f = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.frames["config"] = f

        # Cabecera
        header_card = ctk.CTkFrame(
            f,
            corner_radius=12,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
        )
        header_card.pack(fill="x", pady=(0, 20))

        # Título y botones
        title_section = ctk.CTkFrame(header_card, fg_color="transparent")
        title_section.pack(fill="x", padx=25, pady=20)

        ctk.CTkLabel(
            title_section,
            text="Editor config.py",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff",
        ).pack(side="left", anchor="w")

        # Botones
        btn_frame = ctk.CTkFrame(title_section, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="🔧 REPARAR CONFIG",
            command=self.reparar_config_gui,
            width=140,
            height=35,
            fg_color="#FF9800",
            hover_color="#F57C00",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="💾 GUARDAR",
            command=self.save_config_file,
            width=120,
            height=35,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left")

        # Área de edición con scroll
        self.config_scroll = ctk.CTkScrollableFrame(
            f,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
            corner_radius=12,
        )
        self.config_scroll.pack(fill="both", expand=True, pady=(0, 20))
        self.config_entries = {}

        # SIEMPRE llamar a populate_config_ui aquí - ya que el frame está creado
        self.populate_config_ui()

    def load_config_file(self):
        """Carga config.py - Solo carga datos en memoria, no afecta archivo"""
        if not Path("config.py").exists():
            print("⚠ config.py no encontrado")
            self.config_data = {}
            return

        try:
            with open("config.py", "r", encoding="utf-8") as f:
                contenido = f.read()

            # Buscar GAME_CONFIG manteniendo formato original
            import re

            match = re.search(
                r"GAME_CONFIG\s*=\s*({.*?})\s*(?:\n|$)", contenido, re.DOTALL
            )

            if match:
                config_str = match.group(1)
                try:
                    # Parsear el diccionario
                    self.config_data = ast.literal_eval(config_str)
                    print(f"✅ config.py cargado - {len(self.config_data)} claves")

                    # Debug: mostrar algunas claves importantes
                    claves_importantes = [
                        "GAME_NAME_DISPLAY",
                        "WINDOW_SIZE",
                        "FPS",
                        "SCROLLER_MESSAGE",
                    ]
                    for clave in claves_importantes:
                        if clave in self.config_data:
                            print(
                                f"   📋 {clave}: {self.config_data[clave][:50] if isinstance(self.config_data[clave], str) else self.config_data[clave]}"
                            )

                except Exception as e:
                    print(f"❌ Error parseando config.py: {e}")
                    self.config_data = {}
            else:
                print("❌ No se encontró GAME_CONFIG en el archivo")
                self.config_data = {}

        except Exception as e:
            print(f"❌ Error leyendo config.py: {e}")
            self.config_data = {}

    def reparar_config_si_falla(self):
        """Intenta reparar config.py si falla la carga - SOLO datos, NO UI"""
        print("⚠ Intentando reparar config.py...")
        self.config_data = {
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
                "SPAIN_TEXT": {
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
                "SPAIN_ANIMATION": {
                    "WAVE_SPEED": 0.05,
                    "WAVE_AMPLITUDE": 0.3,
                    "ROTATION_MAX": 0.3,
                    "SHINE_SPEED": 0.02,
                    "PULSE_SPEED": 0.03,
                },
            },
            "AUDIO": {"BPM": 128, "MUSIC_OFFSET": 0.12},
            "BPM_EFFECT": {"IN_NORMAL_MODE": False, "IN_RAVE_MODE": True},
        }

        # Guardar el archivo pero NO llamar a populate_config_ui
        self.save_config_file()

        print("✅ Configuración reparada (datos listos)")

    def reparar_config_gui(self):
        """Repara config.py usando el método directo"""
        try:
            respuesta = messagebox.askyesno(
                "Reparar config.py",
                "⚠  Esto creará un nuevo config.py con valores por defecto.\n\n"
                "¿Estás seguro de que quieres continuar?\n\n"
                "Se hará un backup del archivo actual si existe.",
            )

            if not respuesta:
                print("Operación cancelada")
                return False

            # Usar el método directo que crea el archivo EXACTO
            if self.reparar_config_directo():
                # Actualizar la UI si estamos en la sección de configuración
                if hasattr(self, "config_scroll") and self.config_scroll.winfo_exists():
                    self.populate_config_ui()

                messagebox.showinfo(
                    "Configuración Reparada",
                    "✅ config.py reparado correctamente\n\n"
                    "Se ha creado un archivo config.py nuevo con el formato original.\n"
                    "El archivo original se guardó como config.py.backup",
                )
                return True
            else:
                messagebox.showerror(
                    "Error",
                    "❌ No se pudo reparar config.py\n"
                    "Revisa los mensajes en la consola.",
                )
                return False

        except Exception as e:
            print(f"❌ Error en interfaz de reparación: {e}")
            messagebox.showerror("Error", f"❌ Error reparando config.py:\n\n{str(e)}")
            return False

    def populate_config_ui(self):
        """Puebla la UI con TODOS los campos de configuración"""
        # NUEVO: Cargar config si está vacío
        if not self.config_data:
            self.load_config_file()
            if not self.config_data:
                self.reparar_config_si_falla()
        """Puebla la UI con TODOS los campos de configuración - CAMBIADO: CTkEntry en lugar de CTkTextbox"""
        for w in self.config_scroll.winfo_children():
            w.destroy()
        self.config_entries = {}

        campos_config = [
            ("INFORMACIÓN BÁSICA", "section"),
            ("GAME_FOLDER_NAME", "basic", "Nombre de la carpeta donde se instalará"),
            ("GAME_NAME_DISPLAY", "basic", "Título que se muestra en pantalla"),
            ("WINDOW_CAPTION", "basic", "Título de la ventana"),
            ("SCROLLER_MESSAGE", "basic", "Mensaje del scroller animado"),
            ("SUBTITLE_DISPLAY", "basic", "Subtítulo opcional"),
            ("SPANISH_TEXT", "basic", "Texto personalizable"),
            ("CONFIGURACIÓN DE POST-INSTALACIÓN", "section"),
            (
                "POST_INSTALL|ENABLED",
                "post_install",
                "Parche post-instalación (Nesrak1 CrcTool y serialización, u otro.)",
                "boolean",
            ),
            (
                "POST_INSTALL|PATCHER_EXE",
                "post_install",
                "Nombre del ejecutable parcheador",
            ),
            (
                "POST_INSTALL|TARGET_FILE",
                "post_install",
                "Archivo objetivo para parchear",
            ),
            ("POST_INSTALL|ARGUMENT", "post_install", "Argumento para el parcheador"),
            ("CONFIGURACIÓN DE AUDIO Y SINCRONIZACIÓN BPM", "section"),
            ("AUDIO|BPM", "audio", "Pulsos por minuto (128)"),
            ("AUDIO|MUSIC_OFFSET", "audio", "Offset música (0.12)"),
            (
                "CONTROL DE EFECTOS BPM - Siempre se aplican a los espectometros tanto en SI como en NO",
                "section",
            ),
            (
                "BPM_EFFECT|IN_NORMAL_MODE",
                "bpm",
                "Efectos BPM en modo normal",
                "boolean",
            ),
            (
                "BPM_EFFECT|IN_RAVE_MODE",
                "bpm",
                "Efectos BPM en modo Headbang/rave",
                "boolean",
            ),
        ]

        def obtener_valor(config_dict, clave_ruta, tipo_campo=None):
            partes = clave_ruta.split("|")
            valor_actual = config_dict
            for parte in partes:
                if isinstance(valor_actual, dict) and parte in valor_actual:
                    valor_actual = valor_actual[parte]
                else:
                    if tipo_campo == "boolean":
                        if "ENABLED" in clave_ruta:
                            return False
                        elif "IN_NORMAL_MODE" in clave_ruta:
                            return False
                        elif "IN_RAVE_MODE" in clave_ruta:
                            return True
                        else:
                            return False
                    elif (
                        "SCALE" in clave_ruta
                        or "SPEED" in clave_ruta
                        or "AMPLITUDE" in clave_ruta
                    ):
                        return "1.5" if "SPANISH_TEXT_SCALE" in clave_ruta else "0.05"
                    elif (
                        "COLOR" in clave_ruta
                        or "RED" in clave_ruta
                        or "BLUE" in clave_ruta
                        or "GREEN" in clave_ruta
                        or "YELLOW" in clave_ruta
                    ):
                        return (
                            "(255, 255, 255)"
                            if "WHITE" in clave_ruta
                            else "(255, 0, 0)"
                        )
                    elif "SIZE" in clave_ruta:
                        return "(800, 600)"
                    elif "BPM" in clave_ruta:
                        return "128"
                    elif "OFFSET" in clave_ruta:
                        return "0.12"
                    elif "TIMEOUT" in clave_ruta:
                        return "20.0"
                    elif "FPS" in clave_ruta:
                        return "60"
                    else:
                        return ""
            if tipo_campo == "boolean":
                if isinstance(valor_actual, bool):
                    return valor_actual
                elif isinstance(valor_actual, str):
                    return valor_actual.lower() in [
                        "true",
                        "yes",
                        "sí",
                        "si",
                        "1",
                        "on",
                    ]
                else:
                    return bool(valor_actual)
            else:
                # PARA TODOS LOS CAMPOS: Limpiar saltos de línea
                if isinstance(valor_actual, str):
                    # Reemplazar saltos de línea por espacios para todos los campos
                    return valor_actual.replace("\n", " ").replace("\r", " ")
                else:
                    return (
                        str(valor_actual)
                        if not isinstance(valor_actual, (dict, list))
                        else repr(valor_actual)
                    )

        # Crear UI con diseño mejorado - TODOS LOS CAMPOS COMO CTkEntry (una línea)
        for item in campos_config:
            if len(item) == 2:
                nombre_seccion, tipo = item
                if tipo == "section":
                    section_frame = ctk.CTkFrame(
                        self.config_scroll, fg_color="transparent"
                    )
                    section_frame.pack(fill="x", pady=(20, 15))

                    ctk.CTkLabel(
                        section_frame,
                        text=nombre_seccion,
                        font=ctk.CTkFont(size=16, weight="bold"),
                        text_color="#4dabf7",
                    ).pack(anchor="w", padx=10)

                    separator = ctk.CTkFrame(
                        section_frame, height=1, fg_color="#333333"
                    )
                    separator.pack(fill="x", pady=5)

            else:
                if len(item) == 4:
                    clave_ruta, categoria, descripcion, tipo_campo = item
                else:
                    clave_ruta, categoria, descripcion = item
                    tipo_campo = None

                row_frame = ctk.CTkFrame(self.config_scroll, fg_color="transparent")
                row_frame.pack(fill="x", pady=12, padx=10)

                # Etiqueta de descripción (lado izquierdo)
                label_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                label_frame.pack(side="left", padx=(0, 20))

                ctk.CTkLabel(
                    label_frame,
                    text=descripcion,
                    anchor="w",
                    font=ctk.CTkFont(size=13),
                    text_color="#cccccc",
                    wraplength=300,  # Ancho fijo para la descripción
                ).pack(anchor="w")

                valor_actual = obtener_valor(self.config_data, clave_ruta, tipo_campo)

                if tipo_campo == "boolean":
                    valor_actual_bool = bool(valor_actual)
                    opciones = ["No", "Sí"]
                    valor_inicial = "Sí" if valor_actual_bool else "No"

                    segmented_var = ctk.StringVar(value=valor_inicial)

                    segmented = ctk.CTkSegmentedButton(
                        row_frame,
                        values=opciones,
                        variable=segmented_var,
                        width=120,
                        height=35,
                        fg_color="#2d2d2d",
                        selected_color="#4dabf7",
                        selected_hover_color="#3d8bf5",
                        font=ctk.CTkFont(size=12),
                    )
                    segmented.pack(side="right", padx=(0, 10))

                    self.config_entries[clave_ruta] = segmented

                else:
                    # TODOS LOS CAMPOS DE TEXTO COMO CTkEntry (una línea)
                    entrada = ctk.CTkEntry(
                        row_frame,
                        height=38,  # Altura para una sola línea
                        fg_color="#2d2d2d",
                        border_width=1,
                        border_color="#444444",
                        text_color="#ffffff",
                        font=ctk.CTkFont(size=12),
                    )
                    entrada.insert(0, str(valor_actual))

                    # Campos MUY largos para entrada de texto
                    entrada.configure(width=500)  # Todos los campos igual de largos

                    entrada.pack(
                        side="right", fill="x", expand=True
                    )  # Ocupa el espacio restante
                    self.config_entries[clave_ruta] = entrada

        # Añadir espacio al final
        ctk.CTkFrame(self.config_scroll, height=30, fg_color="transparent").pack()

    def save_config_file(self):
        """Guarda config.py usando la misma lógica que compile.py"""
        try:
            # 1. Verificar que tenemos datos de la UI
            if not hasattr(self, "config_entries") or not self.config_entries:
                print("⚠ No hay campos de configuración para guardar")
                messagebox.showwarning("Advertencia", "No hay cambios para guardar")
                return False

            # 2. Actualizar self.config_data con los valores de la UI
            for clave_ruta, widget in self.config_entries.items():
                if isinstance(widget, ctk.CTkSegmentedButton):
                    valor_seleccionado = widget.get()
                    valor_procesado = valor_seleccionado == "Sí"
                elif isinstance(widget, ctk.CTkEntry):
                    raw_valor = widget.get().strip()

                    # ===== REGLAS DE VALIDACIÓN =====
                    # Campos que PUEDEN estar vacíos (strings opcionales)
                    campos_vacio_permitido = ["SPANISH_TEXT", "SUBTITLE_DISPLAY"]

                    # ===== VALIDACIÓN =====
                    # 1. SPANISH_TEXT y SUBTITLE_DISPLAY pueden estar vacíos
                    if not raw_valor and clave_ruta in campos_vacio_permitido:
                        print(f"    ✅ {clave_ruta} = '' (vacío permitido)")
                        valor_procesado = ""

                    # 2. Otros campos vacíos - omitir (mantener valor anterior)
                    elif not raw_valor:
                        print(f"    ⚠  {clave_ruta} está vacío - omitiendo cambio")
                        continue

                    # 3. Campo CON valor - procesar normalmente
                    else:
                        # DEBUG para campos importantes
                        if clave_ruta in ["SPANISH_TEXT", "SUBTITLE_DISPLAY"]:
                            print(f"    ⭐ {clave_ruta}: '{raw_valor}'")

                        # CONVERSIÓN DE TIPOS
                        try:
                            if raw_valor.lower() == "true":
                                valor_procesado = True
                            elif raw_valor.lower() == "false":
                                valor_procesado = False
                            elif raw_valor.startswith("(") and raw_valor.endswith(")"):
                                valor_procesado = ast.literal_eval(raw_valor)
                            elif raw_valor.isdigit():
                                valor_procesado = int(raw_valor)
                            elif (
                                raw_valor.replace(".", "", 1).isdigit()
                                and raw_valor.count(".") == 1
                            ):
                                valor_procesado = float(raw_valor)
                            else:
                                valor_procesado = raw_valor
                        except Exception as e:
                            print(f"    ⚠  Error convirtiendo {clave_ruta}: {e}")
                            valor_procesado = raw_valor  # Fallback a string
                else:
                    continue

                # Actualizar self.config_data
                partes = clave_ruta.split("|")
                nivel_actual = self.config_data

                for i, parte in enumerate(partes[:-1]):
                    if parte not in nivel_actual:
                        nivel_actual[parte] = {}
                    nivel_actual = nivel_actual[parte]

                nivel_actual[partes[-1]] = valor_procesado

            # 3. Guardar usando la misma estructura que compile.py
            print("💾 Guardando config.py...")

            # Crear backup
            if Path("config.py").exists():
                shutil.copy2("config.py", "config.py.backup")
                print("✅ Backup creado: config.py.backup")

            # Construir contenido con el MISMO formato que compile.py
            contenido = """# config.py
# Configuración principal del juego MetalWar
# Contiene todos los parámetros ajustables del sistema

GAME_CONFIG = {
"""

            # Función para formatear valores (igual que compile.py)
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
                    # Escapar comillas como en compile.py
                    valor_escaped = valor.replace('"', '\\"')
                    # Mantener saltos de línea si existen en el texto original
                    return f'"{valor_escaped}"'

                else:
                    return repr(valor)

            # Añadir todas las secciones (formato igual que compile.py)
            secciones = [
                (
                    "INFORMACIÓN BÁSICA",
                    [
                        "GAME_FOLDER_NAME",
                        "GAME_NAME_DISPLAY",
                        "WINDOW_CAPTION",
                        "SCROLLER_MESSAGE",
                        "SUBTITLE_DISPLAY",
                        "SPANISH_TEXT",
                    ],
                ),
                (
                    "CONFIGURACIÓN DE VENTANA Y RENDIMIENTO",
                    ["WINDOW_SIZE", "FPS", "IDLE_TIMEOUT"],
                ),
                (
                    "CONFIGURACIÓN DE POST-INSTALACIÓN",
                    ["POST_INSTALL"],
                ),
                (
                    "PALETA DE COLORES DEL JUEGO",
                    ["COLORS"],
                ),
                (
                    "CONFIGURACIÓN DE AUDIO Y SINCRONIZACIÓN BPM",
                    ["AUDIO"],
                ),
                (
                    "CONTROL DE EFECTOS BPM",
                    ["BPM_EFFECT"],
                ),
            ]

            primera_seccion = True
            for titulo_seccion, claves in secciones:
                if not primera_seccion:
                    contenido += "\n"
                contenido += f"\n    # {titulo_seccion}\n"

                for clave in claves:
                    if clave in self.config_data:
                        contenido += f'    "{clave}": {formatear_valor(self.config_data[clave])},\n'

                primera_seccion = False

            contenido += "}\n"

            # Guardar archivo
            with open("config.py", "w", encoding="utf-8") as f:
                f.write(contenido)

            print("✅ config.py guardado correctamente")
            print(f"📊 Campos guardados: {len(self.config_entries)}")

            messagebox.showinfo("Éxito", "✅ config.py guardado correctamente")
            return True

        except Exception as e:
            print(f"❌ Error guardando config.py: {e}")
            import traceback

            traceback.print_exc()

            # Restaurar backup si existe
            if Path("config.py.backup").exists():
                try:
                    shutil.copy2("config.py.backup", "config.py")
                    print("✅ Restaurado desde backup")
                except:
                    pass

            messagebox.showerror("Error", f"❌ Error guardando config.py:\n\n{str(e)}")
            return False

    def reparar_config_directo(self):
        """Repara config.py DIRECTAMENTE con el formato EXACTO del archivo original"""
        try:
            print("🔧 Reparando config.py con formato original...")

            # Contenido EXACTO como en el config.py original que me mostraste
            contenido = """# config.py
# Configuración principal del juego MetalWar
# Contiene todos los parámetros ajustables del sistema

GAME_CONFIG = {

    # INFORMACIÓN BÁSICA
    "GAME_FOLDER_NAME": "CARPETA DEL JUEGO",
    "GAME_NAME_DISPLAY": "TITULO DEL JUEGO",
    "WINDOW_CAPTION": "MetalWar - Instalador",
    "SCROLLER_MESSAGE": ">>> METALWAR LOADING... SYSTEM INITIALIZED >>>",
    "SUBTITLE_DISPLAY": "",
    "SPANISH_TEXT": "In Awesome Spanish",


    # CONFIGURACIÓN DE VENTANA Y RENDIMIENTO
    "WINDOW_SIZE": (800, 600),
    "FPS": 60,
    "IDLE_TIMEOUT": 20.0,


    # CONFIGURACIÓN DE POST-INSTALACIÓN
    "POST_INSTALL": {
    "ENABLED": False,
    "PATCHER_EXE": "example.exe",
    "TARGET_FILE": "catalog.json",
    "ARGUMENT": "patchcrc",
},


    # PALETA DE COLORES DEL JUEGO
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


    # CONFIGURACIÓN DE AUDIO Y SINCRONIZACIÓN BPM
    "AUDIO": {
    "BPM": 128,
    "MUSIC_OFFSET": 0.12,
},


    # CONTROL DE EFECTOS BPM
    "BPM_EFFECT": {
    "IN_NORMAL_MODE": False,
    "IN_RAVE_MODE": True,
},
}
"""

            # 1. Hacer backup si existe
            if Path("config.py").exists():
                shutil.copy2("config.py", "config.py.backup")
                print("✅ Backup creado: config.py.backup")

            # 2. Guardar el contenido EXACTO
            with open("config.py", "w", encoding="utf-8") as f:
                f.write(contenido)

            # 3. Recargar la configuración en memoria
            self.load_config_file()

            print("✅ config.py reparado con formato EXACTO del original")
            return True

        except Exception as e:
            print(f"❌ Error reparando config.py: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _actualizar_config_recursivo(self, original, nuevos):
        """Actualiza recursivamente un diccionario con nuevos valores"""
        for clave, valor in nuevos.items():
            if (
                isinstance(valor, dict)
                and clave in original
                and isinstance(original[clave], dict)
            ):
                self._actualizar_config_recursivo(original[clave], valor)
            elif clave in original:
                original[clave] = valor

    # ------------------------------------------------------------------------
    # 3. VERSION INFO EDITOR - DISEÑO MEJORADO (MISMO TEXTO)
    # ------------------------------------------------------------------------
    def create_version_frame(self):
        f = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.frames["version"] = f

        # Cabecera
        header_card = ctk.CTkFrame(
            f,
            corner_radius=12,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
        )
        header_card.pack(fill="x", pady=(0, 20))

        title_section = ctk.CTkFrame(header_card, fg_color="transparent")
        title_section.pack(fill="x", padx=25, pady=20)

        ctk.CTkLabel(
            title_section,
            text="📝 Editor version_info.txt",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff",
        ).pack(side="left", anchor="w")

        ctk.CTkButton(
            title_section,
            text="💾 GUARDAR VERSIÓN",
            command=self.save_version_info,
            width=140,
            height=35,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="right")

        # Información de ayuda
        help_frame = ctk.CTkFrame(f, fg_color="transparent")
        help_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            help_frame,
            text="Información de versión para el ejecutable (.exe)",
            text_color="#888888",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w")

        ctk.CTkLabel(
            help_frame,
            text="Formato de versión: número.mayor.menor.revisión (ej: 1.0.0.0)",
            text_color="#4dabf7",
            font=ctk.CTkFont(size=12, slant="italic"),
        ).pack(anchor="w", pady=(5, 0))

        # Contenedor principal con scroll
        scroll_container = ctk.CTkScrollableFrame(
            f,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
            corner_radius=12,
        )
        scroll_container.pack(fill="both", expand=True, pady=(0, 20))

        # Campos de edición
        campos = [
            ("ProductName", self.v_product, "Nombre del producto", "MetalWar"),
            ("CompanyName", self.v_company, "Nombre de la compañía", "MyStudio"),
            (
                "FileDescription",
                self.v_desc,
                "Descripción del archivo",
                "Game Executable",
            ),
            (
                "FileVersion",
                self.v_file_ver,
                "Versión del archivo (ej: 1.0.0.0)",
                "1.0.0.0",
            ),
            (
                "ProductVersion",
                self.v_prod_ver,
                "Versión del producto (ej: 1.0.0.0)",
                "1.0.0.0",
            ),
            (
                "LegalCopyright",
                self.v_copyright,
                "Texto de copyright",
                "Copyright 2024",
            ),
            (
                "OriginalFilename",
                self.v_filename,
                "Nombre del archivo .exe",
                "MetalWar.exe",
            ),
            ("InternalName", self.v_internal, "Nombre interno", "METALWAR"),
        ]

        self.version_entries = {}

        for campo_nombre, variable, descripcion, ejemplo in campos:
            field_card = ctk.CTkFrame(scroll_container, fg_color="transparent")
            field_card.pack(fill="x", pady=12, padx=25)

            label = ctk.CTkLabel(
                field_card,
                text=descripcion,
                anchor="w",
                font=ctk.CTkFont(size=14),
                text_color="#cccccc",
            )
            label.pack(side="left", padx=(0, 20))

            entry = ctk.CTkEntry(
                field_card,
                textvariable=variable,
                placeholder_text=ejemplo,
                height=36,
                fg_color="#2d2d2d",
                border_width=1,
                border_color="#444444",
                text_color="#ffffff",
            )

            if "Version" in campo_nombre:
                entry.configure(width=180)
                example_label = ctk.CTkLabel(
                    field_card,
                    text=f"ej: {ejemplo}",
                    text_color="#666666",
                    font=ctk.CTkFont(size=11),
                )
                example_label.pack(side="right", padx=(10, 0))
            else:
                entry.configure(width=300)

            entry.pack(side="right")
            self.version_entries[campo_nombre] = entry

        # Panel de validación
        validation_card = ctk.CTkFrame(
            f,
            corner_radius=12,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
        )
        validation_card.pack(fill="x", pady=(0, 20))

        validation_content = ctk.CTkFrame(validation_card, fg_color="transparent")
        validation_content.pack(fill="x", padx=25, pady=20)

        validate_btn = ctk.CTkButton(
            validation_content,
            text="✅ Validar formatos de versión",
            command=self.validar_formatos_version_gui,
            width=200,
            height=35,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            border_width=1,
            border_color="#4dabf7",
        )
        validate_btn.pack(side="left", padx=(0, 20))

        self.version_status_label = ctk.CTkLabel(
            validation_content,
            text="Esperando validación...",
            text_color="#888888",
            font=ctk.CTkFont(size=13),
        )
        self.version_status_label.pack(side="left", fill="x", expand=True)

        preview_btn = ctk.CTkButton(
            validation_content,
            text="👁️ Vista previa",
            command=self.mostrar_vista_previa_version,
            width=120,
            height=35,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            border_width=1,
            border_color="#4dabf7",
        )
        preview_btn.pack(side="right")

    def load_version_info(self):
        """Carga version_info.txt - MÉTODO ORIGINAL"""
        if not Path("version_info.txt").exists():
            print("⚠ version_info.txt no encontrado - Se usarán valores por defecto")
            return

        try:
            with open("version_info.txt", "r", encoding="utf-8") as f:
                contenido = f.read()

            valores = {
                "ProductName": "MetalWar",
                "CompanyName": "MyStudio",
                "FileDescription": "Game Executable",
                "FileVersion": "1.0.0.0",
                "ProductVersion": "1.0.0.0",
                "LegalCopyright": "Copyright 2024",
                "OriginalFilename": "MetalWar.exe",
                "InternalName": "METALWAR",
            }

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

            self.v_product.set(valores["ProductName"])
            self.v_company.set(valores["CompanyName"])
            self.v_desc.set(valores["FileDescription"])
            self.v_file_ver.set(valores["FileVersion"])
            self.v_prod_ver.set(valores["ProductVersion"])
            self.v_copyright.set(valores["LegalCopyright"])
            self.v_filename.set(valores["OriginalFilename"])
            self.v_internal.set(valores["InternalName"])

            print("✅ version_info.txt cargado correctamente")

        except Exception as e:
            print(f"❌ Error leyendo version_info.txt: {e}")

    def validar_formatos_version_gui(self):
        """Valida los formatos de versión - MÉTODO ORIGINAL CON MEJOR VISUAL"""

        def validar_version(version_str):
            if not version_str:
                return False, "Campo vacío"
            partes = version_str.split(".")
            if len(partes) != 4:
                return False, "Debe tener 4 partes (x.x.x.x)"
            for parte in partes:
                if not parte.isdigit():
                    return False, "Todas las partes deben ser números"
            return True, "✓ Formato correcto"

        file_version = self.v_file_ver.get()
        product_version = self.v_prod_ver.get()

        valido_fv, mensaje_fv = validar_version(file_version)
        valido_pv, mensaje_pv = validar_version(product_version)

        if "FileVersion" in self.version_entries:
            color_fv = "#4CAF50" if valido_fv else "#F44336"
            self.version_entries["FileVersion"].configure(border_color=color_fv)

        if "ProductVersion" in self.version_entries:
            color_pv = "#4CAF50" if valido_pv else "#F44336"
            self.version_entries["ProductVersion"].configure(border_color=color_pv)

        if valido_fv and valido_pv:
            self.version_status_label.configure(
                text="✅ Formatos de versión válidos", text_color="#4CAF50"
            )
            return True
        else:
            mensaje_error = ""
            if not valido_fv:
                mensaje_error += f"FileVersion: {mensaje_fv}\n"
            if not valido_pv:
                mensaje_error += f"ProductVersion: {mensaje_pv}"

            self.version_status_label.configure(
                text=f"❌ Errores:\n{mensaje_error}", text_color="#F44336"
            )
            return False

    def mostrar_vista_previa_version(self):
        """Muestra vista previa - MÉTODO ORIGINAL"""
        try:
            if not self.validar_formatos_version_gui():
                print("❌ No se puede generar vista previa: formatos inválidos")
                return

            fv = self.v_file_ver.get().replace(".", ", ")
            pv = self.v_prod_ver.get().replace(".", ", ")

            version_content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({fv}),
    prodvers=({pv}),
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
        [StringStruct(u'CompanyName', u'{self.v_company.get()}'),
        StringStruct(u'FileDescription', u'{self.v_desc.get()}'),
        StringStruct(u'FileVersion', u'{self.v_file_ver.get()}'),
        StringStruct(u'InternalName', u'{self.v_internal.get()}'),
        StringStruct(u'LegalCopyright', u'{self.v_copyright.get()}'),
        StringStruct(u'OriginalFilename', u'{self.v_filename.get()}'),
        StringStruct(u'ProductName', u'{self.v_product.get()}'),
        StringStruct(u'ProductVersion', u'{self.v_prod_ver.get()}')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""

            preview_window = ctk.CTkToplevel(self)
            preview_window.title("Vista previa - version_info.txt")
            preview_window.geometry("700x500")

            info_label = ctk.CTkLabel(
                preview_window,
                text="Este es el contenido que se guardará:",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#ffffff",
            )
            info_label.pack(pady=(20, 10))

            preview_text = ctk.CTkTextbox(
                preview_window,
                font=("Consolas", 10),
                wrap="none",
                fg_color="#1a1a1a",
                border_width=1,
                border_color="#333333",
            )
            preview_text.pack(fill="both", expand=True, padx=20, pady=10)

            preview_text.insert("1.0", version_content)
            preview_text.configure(state="disabled")

            close_btn = ctk.CTkButton(
                preview_window,
                text="Cerrar",
                command=preview_window.destroy,
                width=100,
                height=35,
            )
            close_btn.pack(pady=20)

        except Exception as e:
            print(f"❌ Error mostrando vista previa: {e}")

    def save_version_info(self):
        """Guarda version_info.txt - MÉTODO ORIGINAL"""
        try:

            def validar_version(version_str):
                partes = version_str.split(".")
                if len(partes) != 4:
                    return False, "Debe tener 4 partes (x.x.x.x)"
                for parte in partes:
                    if not parte.isdigit():
                        return False, "Todas las partes deben ser números"
                return True, "Formato correcto"

            file_version = self.v_file_ver.get()
            product_version = self.v_prod_ver.get()

            valido_fv, mensaje_fv = validar_version(file_version)
            if not valido_fv:
                print(f"❌ Error en FileVersion: {mensaje_fv}")
                print("   Ejemplo correcto: 1.0.0.0")
                return False

            valido_pv, mensaje_pv = validar_version(product_version)
            if not valido_pv:
                print(f"❌ Error en ProductVersion: {mensaje_pv}")
                print("   Ejemplo correcto: 1.0.0.0")
                return False

            fv = file_version.replace(".", ", ")
            pv = product_version.replace(".", ", ")

            version_content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({fv}),
    prodvers=({pv}),
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
        [StringStruct(u'CompanyName', u'{self.v_company.get()}'),
        StringStruct(u'FileDescription', u'{self.v_desc.get()}'),
        StringStruct(u'FileVersion', u'{self.v_file_ver.get()}'),
        StringStruct(u'InternalName', u'{self.v_internal.get()}'),
        StringStruct(u'LegalCopyright', u'{self.v_copyright.get()}'),
        StringStruct(u'OriginalFilename', u'{self.v_filename.get()}'),
        StringStruct(u'ProductName', u'{self.v_product.get()}'),
        StringStruct(u'ProductVersion', u'{self.v_prod_ver.get()}')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

            print("📄 VISTA PREVIA DEL ARCHIVO:")
            preview_lines = version_content.split("\n")
            for i, line in enumerate(preview_lines[:10]):
                print(f"   {line}")
            if len(preview_lines) > 10:
                print(f"   ... ({len(preview_lines) - 10} líneas más)")

            with open("version_info.txt", "w", encoding="utf-8") as f:
                f.write(version_content)

            print("✅ version_info.txt guardado en formato CORRECTO para PyInstaller")
            print("   • Formato VSVersionInfo correcto")
            print(f"   • ProductName: {self.v_product.get()}")
            print(f"   • Versión: {self.v_file_ver.get()}")
            print(f"   • Copyright: {self.v_copyright.get()}")

            self.check_files_status()
            return True

        except Exception as e:
            print(f"❌ Error guardando version_info.txt: {e}")
            import traceback

            traceback.print_exc()
            return False

    # ============================================================================
    # 4. ASSETS FRAME - DISEÑO MEJORADO (MISMO TEXTO)
    # ============================================================================
    def create_assets_frame(self):
        f = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.frames["assets"] = f

        # Cabecera
        header_card = ctk.CTkFrame(
            f,
            corner_radius=12,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
        )
        header_card.pack(fill="x", pady=(0, 20))

        title_section = ctk.CTkFrame(header_card, fg_color="transparent")
        title_section.pack(fill="x", padx=25, pady=20)

        ctk.CTkLabel(
            title_section,
            text="🎨 Generador de Assets (Splash + Iconos)",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff",
        ).pack(side="left", anchor="w")

        # Panel principal
        main_container = ctk.CTkFrame(f, fg_color="transparent")
        main_container.pack(fill="both", expand=True, pady=(0, 20))

        # Panel izquierdo: Generadores
        left_panel = ctk.CTkFrame(
            main_container,
            width=400,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
            corner_radius=12,
        )
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        left_panel.grid_propagate(False)

        # Panel derecho: Preview
        right_panel = ctk.CTkFrame(
            main_container,
            width=300,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
            corner_radius=12,
        )
        right_panel.pack(side="right", fill="both")
        right_panel.grid_propagate(False)

        # ===== PANEL IZQUIERDO: GENERADORES =====
        left_content = ctk.CTkFrame(left_panel, fg_color="transparent")
        left_content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            left_content,
            text="🛠️ GENERADORES DE SPLASH",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        ).pack(anchor="w", pady=(0, 15))

        # Selector de producto
        product_frame = ctk.CTkFrame(left_content, fg_color="transparent")
        product_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            product_frame,
            text="Nombre del producto:",
            font=ctk.CTkFont(size=13),
            text_color="#cccccc",
        ).pack(anchor="w", pady=(0, 8))

        self.assets_product_var = ctk.StringVar(value="MetalWar")
        self.assets_product_entry = ctk.CTkEntry(
            product_frame,
            textvariable=self.assets_product_var,
            height=38,
            fg_color="#2d2d2d",
            border_width=1,
            border_color="#444444",
        )
        self.assets_product_entry.pack(fill="x", pady=(0, 15))

        # Información sobre hover+click
        info_label = ctk.CTkLabel(
            left_content,
            text="🖱️ HOVER: Vista previa | CLICK: Generar splash.png",
            text_color="#4dabf7",
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        info_label.pack(anchor="w", pady=(0, 15))

        # Lista de generadores
        generadores = [
            (
                "🌀 Lite - Minimalista profesional",
                self.generar_splash_lite_gui,
                "#2E8B57",
            ),
            ("🤖 Industrial - Cyberpunk", self.Industrial_muthafuckaed_gui, "#4B0082"),
            ("🎸 Brutal - Heavy metal", self.generar_splash_brutal_gui, "#8B0000"),
            (
                "🎲 Random Madness - Aleatorio",
                self.generar_splash_random_madness_gui,
                "#DAA520",
            ),
            (
                "👾 Pixel Terror - 8-bit",
                self.generar_splash_pixel_terror_gui,
                "#696969",
            ),
            ("⚡ Plasma Core PRO", self.generar_plasma_core_pro_gui, "#8A2BE2"),
            ("🎛️ Copper Bars PRO", self.generar_copper_bars_pro_gui, "#DC143C"),
            ("🌌 Synthwave Grid PRO", self.generar_synthwave_grid_pro_gui, "#00BFFF"),
            (
                "🌐 Experimental Web - HTML/Canvas",
                self.generar_experimental_web_gui,
                "#6A5ACD",
            ),
        ]

        scrollable_generators = ctk.CTkScrollableFrame(
            left_content, fg_color="transparent", height=300
        )
        scrollable_generators.pack(fill="both", expand=True)

        for texto, comando, color in generadores:
            btn = ctk.CTkButton(
                scrollable_generators,
                text=texto,
                command=lambda cmd=comando: cmd(preview_only=False),
                fg_color=color,
                hover_color=self._ajustar_color(color, -30),
                height=42,
                font=ctk.CTkFont(size=13),
                corner_radius=8,
            )

            btn.bind("<Enter>", lambda e, cmd=comando: cmd(preview_only=True))
            btn.pack(fill="x", pady=4)

        # Separador
        ctk.CTkFrame(left_content, height=1, fg_color="#333333").pack(fill="x", pady=20)

        # Generador de iconos
        ctk.CTkLabel(
            left_content,
            text="📁 GENERADOR DE ICONOS (.ico)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff",
        ).pack(anchor="w", pady=(0, 15))

        # ===== NUEVO: BOTÓN DE ICONOS AL LADO DEL TÍTULO =====
        title_buttons = ctk.CTkFrame(header_card, fg_color="transparent")
        title_buttons.pack(side="right", padx=(0, 25))

        ctk.CTkButton(
            title_buttons,
            text="🖼️ CREAR ICON.ICO",
            command=self.generar_icono_desde_logo,
            width=160,
            height=35,
            fg_color="#FF9800",
            hover_color="#F57C00",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="right", padx=(10, 0), pady=(5, 50))

        btn_icon = ctk.CTkButton(
            left_content,
            text="🖼️ Generar icon.ico desde logo.png",
            command=self.generar_icono_desde_logo,
            height=42,
            fg_color="#FF9800",
            hover_color="#F57C00",
            corner_radius=8,
        )
        btn_icon.pack(fill="x", pady=(0, 15))

        self.icon_status_label = ctk.CTkLabel(
            left_content,
            text="Requiere logo.png para generar iconos",
            text_color="#888888",
            font=ctk.CTkFont(size=12),
        )
        self.icon_status_label.pack(anchor="w")

        self.verificar_logo_existente()

        # ===== PANEL DERECHO: PREVIEW =====
        right_content = ctk.CTkFrame(right_panel, fg_color="transparent")
        right_content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            right_content,
            text="👁️ VISTA PREVIA",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        ).pack(anchor="w", pady=(0, 20))

        # Frame para imagen de preview
        self.preview_frame = ctk.CTkFrame(
            right_content,
            height=200,
            fg_color="#2d2d2d",
            border_width=1,
            border_color="#444444",
            corner_radius=8,
        )
        self.preview_frame.pack(fill="x", pady=(0, 20))
        self.preview_frame.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Pasa el ratón sobre un generador",
            font=ctk.CTkFont(size=13),
            text_color="#888888",
        )
        self.preview_label.pack(expand=True, padx=20, pady=20)

        self.preview_info = ctk.CTkLabel(
            right_content,
            text="Vista previa aparecerá aquí",
            text_color="#666666",
            font=ctk.CTkFont(size=12),
        )
        self.preview_info.pack(anchor="w", pady=(0, 20))

        # Estado de archivos
        status_frame = ctk.CTkFrame(right_content, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            status_frame,
            text="📊 ESTADO DE ARCHIVOS:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff",
        ).pack(anchor="w", pady=(0, 15))

        self.assets_status_labels = {}
        archivos_assets = ["splash.png", "icon.ico", "logo.png"]

        for archivo in archivos_assets:
            row = ctk.CTkFrame(status_frame, fg_color="transparent")
            row.pack(fill="x", pady=6)

            ctk.CTkLabel(
                row,
                text=archivo,
                font=ctk.CTkFont(size=13),
                text_color="#cccccc",
                width=120,
                anchor="w",
            ).pack(side="left")

            status = ctk.CTkLabel(
                row,
                text="...",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100,
                anchor="e",
            )
            status.pack(side="right")
            self.assets_status_labels[archivo] = status

        # Botón para verificar
        ctk.CTkButton(
            right_content,
            text="🔄 Actualizar estado",
            command=self.actualizar_estado_assets,
            height=35,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            border_width=1,
            border_color="#444444",
        ).pack(fill="x", pady=(10, 0))

        self.actualizar_estado_assets()

    # ============================================================================
    # MOTOR GRÁFICO PRO V3 (TEXTO AJUSTADO + CAOS PROCEDURAL)
    # ============================================================================

    def _crear_gradiente_vertical(self, width, height, color_top, color_bottom):
        base = Image.new("RGB", (width, height), color_top)
        top = Image.new("RGB", (width, height), color_top)
        bottom = Image.new("RGB", (width, height), color_bottom)
        mask = Image.new("L", (width, height))
        mask_data = []
        for y in range(height):
            mask_data.extend([int(255 * (y / height))] * width)
        mask.putdata(mask_data)
        base.paste(bottom, (0, 0), mask)
        return base

    def _aplicar_vignette(self, img, intensidad=100):
        width, height = img.size
        mask = Image.new("L", (width, height), 255)
        m_draw = ImageDraw.Draw(mask)
        m_draw.ellipse((40, 40, width - 40, height - 40), fill=0)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=80))
        black_layer = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        black_layer.putalpha(mask)
        return Image.alpha_composite(img.convert("RGBA"), black_layer).convert("RGB")

    def _generar_ruido(self, width, height, opacity=30):
        noise = Image.effect_noise((width, height), 10).convert("L")
        colorize = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        colorize.putalpha(noise)
        final_noise = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        final_noise.paste(colorize, (0, 0), colorize)
        alpha = final_noise.split()[3]
        alpha = alpha.point(lambda p: p * (opacity / 255))
        final_noise.putalpha(alpha)
        return final_noise

    def dibujar_texto_gigante(self, draw, texto, y_centro_objetivo, color):
        """
        Dibuja texto asegurando 100% que no se corta.
        """
        image_width = 600

        # 👇👇👇 AQUÍ ESTÁ EL CAMBIO 👇👇👇
        margin_safety = 100  # Antes 50. Con 80 forzamos a que el texto sea más pequeño.
        # 👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆

        max_width = image_width - (margin_safety * 2)

        # Empezamos grande
        font_size = 130
        min_font_size = 20
        font = None

        # BUCLE DE AJUSTE
        while font_size >= min_font_size:
            try:
                font = ImageFont.truetype("arialbd.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                    break

            # Medir
            bbox = draw.textbbox((0, 0), texto, font=font)
            text_width = bbox[2] - bbox[0]

            # Si cabe de sobra, salimos
            if text_width <= max_width:
                break

            # Si no cabe, reducimos rápido
            font_size -= 5

        # Calcular posición
        bbox = draw.textbbox((0, 0), texto, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (image_width - text_width) // 2
        y = y_centro_objetivo - (text_height // 2) - 10

        # Sombra y Texto
        offset = max(2, font_size // 20)
        draw.text((x + offset, y + offset), texto, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), texto, font=font, fill=color)

        return font_size

    def _generar_splash_maestro(self, estilo, preview_only=False):
        try:
            width, height = 600, 350
            style_type = estilo.get("effect", "solid")

            # --- FASE 1: GENERACIÓN PROCEDURAL (CAOS REAL) ---

            if style_type == "plasma":
                # Plasma con semilla aleatoria para que cambie siempre
                low_w, low_h = 100, 60
                plasma = Image.new("RGB", (low_w, low_h))
                pixels = plasma.load()

                # Semillas aleatorias
                seed_x = random.randint(0, 100)
                seed_y = random.randint(0, 100)
                seed_z = random.randint(0, 100)

                for y in range(low_h):
                    for x in range(low_w):
                        # Fórmulas matemáticas caóticas
                        v = (
                            math.sin(x / 10 + seed_x)
                            + math.sin(y / 10 + seed_y)
                            + math.sin((x + y) / 100 + seed_z)
                        )
                        v = (v + 3) * 32
                        r = int(math.sin(v * math.pi / 128) * 127 + 128)
                        g = int(
                            math.sin(v * math.pi / 128 + 2) * 127 + 128
                        )  # Añadimos verde para variar
                        b = int(math.sin(v * math.pi / 128 + 4) * 127 + 128)

                        # Variación de color según el estilo deseado (Morado/Azul vs Multicolor)
                        pixels[x, y] = (r, 0, b) if random.random() > 0.1 else (r, g, b)

                img = plasma.resize((width, height), Image.Resampling.BICUBIC)

            elif style_type == "grid":  # Synthwave
                # Fondo variante
                top_c = (random.randint(0, 20), 0, random.randint(20, 50))
                bot_c = (random.randint(30, 60), 0, random.randint(50, 100))
                img = self._crear_gradiente_vertical(width, height, top_c, bot_c)
                draw = ImageDraw.Draw(img)

                # Sol en posición ligeramente aleatoria
                sun_size = random.randint(160, 200)
                sun_y = height // 2 - random.randint(30, 60)
                draw.ellipse(
                    (
                        width // 2 - sun_size // 2,
                        sun_y - sun_size // 2,
                        width // 2 + sun_size // 2,
                        sun_y + sun_size // 2,
                    ),
                    fill=(255, random.randint(50, 150), 0),
                )

                # Cortes del sol
                for i in range(sun_y, sun_y + sun_size // 2, 8):
                    draw.line(
                        [
                            (width // 2 - sun_size // 2, i),
                            (width // 2 + sun_size // 2, i),
                        ],
                        fill=bot_c,
                        width=3,
                    )

                # Grid suelo
                ground_y = height // 2 + 20
                draw.rectangle([0, ground_y, width, height], fill=(10, 0, 20))

                # Líneas de perspectiva aleatorias
                offset_grid = random.randint(-50, 50)
                for i in range(-600, 1200, 60):
                    draw.line(
                        [(i + offset_grid, height), (width // 2, ground_y)],
                        fill=(0, 255, 255),
                        width=1,
                    )
                for i in range(ground_y, height, 20):
                    draw.line([(0, i), (width, i)], fill=(0, 255, 255), width=1)

            elif style_type == "noise":  # Industrial
                # Fondo metálico sucio
                base_val = random.randint(20, 50)
                img = self._crear_gradiente_vertical(
                    width,
                    height,
                    (base_val + 20, base_val + 20, base_val + 20),
                    (10, 10, 10),
                )
                draw = ImageDraw.Draw(img)

                # Elementos industriales aleatorios
                for _ in range(5):
                    x1 = random.randint(0, width)
                    y1 = random.randint(0, height)
                    draw.rectangle(
                        [
                            x1,
                            y1,
                            x1 + random.randint(20, 100),
                            y1 + random.randint(5, 20),
                        ],
                        fill=(60, 60, 60),
                    )

                # Franjas peligro
                for i in range(-200, 200, 40):
                    draw.line([(0, i), (200, i + 200)], fill=(200, 180, 0), width=20)
                    draw.line(
                        [(width - 200, i), (width, i + 200)],
                        fill=(200, 180, 0),
                        width=20,
                    )

                # Suciedad extra
                overlay = Image.new("RGBA", (width, height), (0, 0, 0, 180))
                img.paste(overlay, (0, 0), overlay)

            elif estilo.get("text_color") == "#B87333":  # Copper
                img = self._crear_gradiente_vertical(
                    width, height, (60, 30, 10), (20, 10, 0)
                )
                draw = ImageDraw.Draw(img)
                # Rayas de cobre aleatorias
                for _ in range(20):
                    y = random.randint(0, height)
                    w_line = random.randint(1, 4)
                    draw.line(
                        [(0, y), (width, y)], fill=(255, 150, 100, 50), width=w_line
                    )

            elif (
                estilo.get("bg_color") == "#000000"
                and estilo.get("text_color") == "#FF0000"
            ):  # Brutal
                img = Image.new("RGB", (width, height), (10, 0, 0))
                draw = ImageDraw.Draw(img)
                # Sangre / Fragmentos aleatorios
                for _ in range(random.randint(10, 20)):
                    coords = [
                        (random.randint(0, width), random.randint(0, height))
                        for _ in range(3)
                    ]
                    color_r = random.randint(50, 150)
                    draw.polygon(coords, fill=(color_r, 0, 0))

            elif estilo.get("bg_color") == "#F8F9FA":  # Web / Lite
                img = self._crear_gradiente_vertical(
                    width, height, (255, 255, 255), (220, 230, 250)
                )
                d = ImageDraw.Draw(img, "RGBA")
                # Círculos abstractos aleatorios
                for _ in range(3):
                    x = random.randint(0, width)
                    y = random.randint(0, height)
                    r = random.randint(50, 150)
                    d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 220, 255, 80))

            else:  # Random
                r1, g1, b1 = (
                    random.randint(0, 50),
                    random.randint(0, 50),
                    random.randint(0, 50),
                )
                r2, g2, b2 = (
                    random.randint(0, 20),
                    random.randint(0, 20),
                    random.randint(0, 20),
                )
                img = self._crear_gradiente_vertical(
                    width, height, (r1, g1, b1), (r2, g2, b2)
                )

            # --- FASE 2: TEXTURIZADO Y VIGNETTE ---
            if estilo.get("bg_color") != "#F8F9FA":
                noise_layer = self._generar_ruido(
                    width, height, opacity=random.randint(15, 30)
                )
                img = Image.alpha_composite(img.convert("RGBA"), noise_layer).convert(
                    "RGB"
                )
                img = self._aplicar_vignette(img, intensidad=120)

            # --- FASE 3: UI (TEXTO Y BARRAS) ---
            draw = ImageDraw.Draw(img)

            # 1. TEXTO DEL PRODUCTO (Ajustado)
            product_name = self.assets_product_var.get().strip() or "PRODUCTO"
            product_name = product_name.upper()
            text_color = estilo.get("text_color", "#FFFFFF")

            # Centro vertical superior (aprox 120px desde arriba)
            self.dibujar_texto_gigante(draw, product_name, 120, text_color)

            # 2. BARRA DE PROGRESO
            bar_w = width * 0.7
            bar_h = 18
            bar_x = (width - bar_w) // 2
            bar_y = 240

            bar_fill = estilo.get("bar_fill", "#FFFFFF")
            bar_border = estilo.get("bar_border", "#FFFFFF")

            draw.rectangle(
                [bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
                fill=(0, 0, 0, 128),
                outline=bar_border,
            )

            inner = 3
            style = estilo.get("bar_style", "solid")

            # Relleno de barra (con variación aleatoria leve en estilo striped)
            if style == "striped":
                offset_stripe = random.randint(0, 10)
                for i in range(int(bar_x) + inner, int(bar_x + bar_w * 0.7), 10):
                    draw.line(
                        [
                            (i + offset_stripe, bar_y + bar_h - inner),
                            (i + 6 + offset_stripe, bar_y + inner),
                        ],
                        fill=bar_fill,
                        width=4,
                    )
            elif style == "blocks":
                for i in range(int(bar_x) + inner, int(bar_x + bar_w * 0.7), 20):
                    draw.rectangle(
                        [i, bar_y + inner, i + 15, bar_y + bar_h - inner], fill=bar_fill
                    )
            else:
                draw.rectangle(
                    [
                        bar_x + inner,
                        bar_y + inner,
                        bar_x + bar_w * 0.7,
                        bar_y + bar_h - inner,
                    ],
                    fill=bar_fill,
                )

            # 3. TEXTO DE ESTADO
            wait_text = (
                "INITIALIZING..."
                if style_type in ["noise", "grid"]
                else "PLEASE WAIT..."
            )
            try:
                font_s = ImageFont.truetype("arial.ttf", 12)
            except:
                font_s = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), wait_text, font=font_s)
            tw = bbox[2] - bbox[0]
            draw.rectangle(
                [
                    (width - tw) // 2 - 10,
                    bar_y + 30,
                    (width + tw) // 2 + 10,
                    bar_y + 46,
                ],
                fill=(0, 0, 0, 100),
            )
            draw.text(
                ((width - tw) // 2, bar_y + 32), wait_text, font=font_s, fill=text_color
            )

            # --- FASE 4: SCANLINES ---
            if style_type in ["grid", "noise", "plasma"]:
                overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                d = ImageDraw.Draw(overlay)
                for y in range(0, height, 2):
                    d.line([(0, y), (width, y)], fill=(0, 0, 0, 40))
                img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

            if not preview_only:
                img.save("splash.png")
                print(f"✅ Splash generado: {product_name}")
                self.actualizar_estado_assets()

            self._actualizar_preview_splash(img)
            return img

        except Exception as e:
            print(f"❌ Error generando splash: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _actualizar_preview_splash(self, img_pil):
        try:
            preview_w, preview_h = 260, 150
            img_copy = img_pil.copy()
            img_copy.thumbnail((preview_w, preview_h), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(
                light_image=img_copy, dark_image=img_copy, size=img_copy.size
            )
            self.preview_label.configure(image=ctk_img, text="")
            self.preview_info.configure(
                text=f"Splash generado: {img_pil.size[0]}x{img_pil.size[1]}"
            )
        except Exception as e:
            print(f"⚠ Error preview: {e}")
            self.preview_label.configure(text="Error preview")

    def _ajustar_color(self, color_hex, ajuste):
        try:
            r = int(color_hex[1:3], 16)
            g = int(color_hex[3:5], 16)
            b = int(color_hex[5:7], 16)
            r = max(0, min(255, r + ajuste))
            g = max(0, min(255, g + ajuste))
            b = max(0, min(255, b + ajuste))
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color_hex

    def verificar_logo_existente(self):
        """Verifica si logo.png existe - MÉTODO ORIGINAL"""
        if Path("logo.png").exists():
            self.icon_status_label.configure(
                text="✅ logo.png encontrado - Listo para generar iconos",
                text_color="#4CAF50",
            )
        else:
            self.icon_status_label.configure(
                text="❌ logo.png no encontrado - No se pueden generar iconos",
                text_color="#F44336",
            )

    def actualizar_estado_assets(self):
        """Actualiza el estado de los archivos de assets - MÉTODO ORIGINAL"""
        for archivo, label in self.assets_status_labels.items():
            if Path(archivo).exists():
                label.configure(text="✅ PRESENTE", text_color="#4CAF50")
            else:
                label.configure(
                    text="❌ FALTANTE",
                    text_color="#F44336" if archivo == "logo.png" else "#FF9800",
                )

    def generar_icono_desde_logo(self):
        """Genera icon.ico desde logo.png - MÉTODO ORIGINAL"""
        try:
            if not Path("logo.png").exists():
                messagebox.showerror(
                    "Error",
                    "❌ No se encontró logo.png\n\n"
                    "Necesitas un archivo logo.png para generar los iconos.",
                )
                return False

            print("🖼️ Generando icon.ico desde logo.png...")

            logo = Image.open("logo.png")

            icon_sizes = [
                (16, 16),
                (32, 32),
                (48, 48),
                (64, 64),
                (128, 128),
                (256, 256),
            ]

            icon_images = []
            for size in icon_sizes:
                img_resized = logo.copy()
                img_resized.thumbnail(size, Image.Resampling.LANCZOS)

                square_img = Image.new("RGBA", size, (0, 0, 0, 0))

                x_offset = (size[0] - img_resized.width) // 2
                y_offset = (size[1] - img_resized.height) // 2
                square_img.paste(
                    img_resized,
                    (x_offset, y_offset),
                    img_resized if img_resized.mode == "RGBA" else None,
                )

                icon_images.append(square_img)

            icon_images[0].save(
                "icon.ico",
                format="ICO",
                sizes=[(size[0], size[1]) for size in icon_sizes],
                append_images=icon_images[1:],
            )

            print(f"✅ icon.ico generado con {len(icon_sizes)} tamaños diferentes")

            self.actualizar_estado_assets()
            self.verificar_logo_existente()

            messagebox.showinfo(
                "Éxito",
                "✅ icon.ico generado correctamente\n\n"
                f"Se crearon iconos en {len(icon_sizes)} tamaños diferentes:\n"
                "16x16, 32x32, 48x48, 64x64, 128x128, 256x256",
            )

            return True

        except Exception as e:
            print(f"❌ Error generando icono: {e}")
            import traceback

            traceback.print_exc()

            messagebox.showerror("Error", f"❌ Error generando icon.ico:\n\n{str(e)}")
            return False

    # Métodos de los botones de generación de splash (MISMOS QUE EL ORIGINAL)
    def generar_splash_lite_gui(self, preview_only=False):
        img = self._generar_splash_maestro(
            {
                "bg_color": "#FFFFFF",
                "text_color": "#333333",
                "bar_fill": "#2E8B57",
                "bar_border": "#CCCCCC",
                "bar_style": "solid",
            },
            preview_only=preview_only,
        )
        if not preview_only:
            print("✅ Splash Lite generado y guardado")

    def Industrial_muthafuckaed_gui(self, preview_only=False):
        img = self._generar_splash_maestro(
            {
                "bg_color": "#111111",
                "text_color": "#FFD700",
                "bar_fill": "#FFA500",
                "bar_border": "#555555",
                "effect": "noise",
                "accent_color": "#333333",
                "bar_style": "striped",
            },
            preview_only=preview_only,
        )
        if not preview_only:
            print("✅ Splash Industrial generado y guardado")

    def generar_splash_brutal_gui(self, preview_only=False):
        img = self._generar_splash_maestro(
            {
                "bg_color": "#000000",
                "text_color": "#FF0000",
                "bar_fill": "#8B0000",
                "bar_border": "#FF0000",
                "shadow": True,
                "bar_style": "solid",
            },
            preview_only=preview_only,
        )
        if not preview_only:
            print("✅ Splash Brutal generado y guardado")

    def generar_splash_random_madness_gui(self, preview_only=False):
        def r_col():
            return "#{:06x}".format(random.randint(0, 0xFFFFFF))

        img = self._generar_splash_maestro(
            {
                "bg_color": r_col(),
                "text_color": "#FFFFFF",
                "bar_fill": r_col(),
                "bar_border": "#FFFFFF",
                "shadow": True,
                "bar_style": "solid",
            },
            preview_only=preview_only,
        )
        if not preview_only:
            print("✅ Splash Random generado y guardado")

    def generar_splash_pixel_terror_gui(self, preview_only=False):
        img = self._generar_splash_maestro(
            {
                "bg_color": "#000000",
                "text_color": "#00FF00",
                "bar_fill": "#00FF00",
                "bar_border": "#00FF00",
                "effect": "noise",
                "accent_color": "#003300",
                "bar_style": "blocks",
            },
            preview_only=preview_only,
        )
        if not preview_only:
            print("✅ Splash Pixel generado y guardado")

    def generar_plasma_core_pro_gui(self, preview_only=False):
        img = self._generar_splash_maestro(
            {
                "bg_color": "#1A0033",
                "text_color": "#00FFFF",
                "bar_fill": "#FF00FF",
                "bar_border": "#FFFFFF",
                "effect": "plasma",
                "shadow": True,
                "bar_style": "solid",
            },
            preview_only=preview_only,
        )
        if not preview_only:
            print("✅ Plasma Core PRO generado y guardado")

    def generar_copper_bars_pro_gui(self, preview_only=False):
        img = self._generar_splash_maestro(
            {
                "bg_color": "#2F1B10",
                "text_color": "#B87333",
                "bar_fill": "#CD7F32",
                "bar_border": "#B87333",
                "shadow": True,
                "bar_style": "striped",
            },
            preview_only=preview_only,
        )
        if not preview_only:
            print("✅ Copper Bars PRO generado y guardado")

    def generar_synthwave_grid_pro_gui(self, preview_only=False):
        img = self._generar_splash_maestro(
            {
                "bg_color": "#050014",
                "text_color": "#FF00CC",
                "bar_fill": "#00F0FF",
                "bar_border": "#FF00CC",
                "effect": "grid",
                "grid_color": "#9400D3",
                "shadow": True,
                "bar_style": "solid",
            },
            preview_only=preview_only,
        )
        if not preview_only:
            print("✅ Synthwave Grid PRO generado y guardado")

    def generar_experimental_web_gui(self, preview_only=False):
        img = self._generar_splash_maestro(
            {
                "bg_color": "#F8F9FA",
                "text_color": "#6610f2",
                "bar_fill": "#0d6efd",
                "bar_border": "#dee2e6",
                "bar_style": "solid",
            },
            preview_only=preview_only,
        )
        if not preview_only:
            print("✅ Experimental Web generado y guardado")

    # ------------------------------------------------------------------------
    # 5. COMPILAR PROYECTO (.spec) - DISEÑO MEJORADO (MISMO TEXTO)
    # ------------------------------------------------------------------------
    def create_compile_frame(self):
        f = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.frames["compile"] = f

        # Cabecera
        header_card = ctk.CTkFrame(
            f,
            corner_radius=12,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
        )
        header_card.pack(fill="x", pady=(0, 20))

        title_section = ctk.CTkFrame(header_card, fg_color="transparent")
        title_section.pack(fill="x", padx=25, pady=20)

        ctk.CTkLabel(
            title_section,
            text="🚀 COMPILAR PROYECTO (.spec)",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff",
        ).pack(side="left", anchor="w")

        ctk.CTkButton(
            title_section,
            text="❓ Ayuda",
            command=self.mostrar_ayuda_compilacion,
            width=80,
            height=35,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            border_width=1,
            border_color="#444444",
        ).pack(side="right", padx=(0, 10))

        # Información de ayuda
        help_frame = ctk.CTkFrame(f, fg_color="transparent")
        help_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            help_frame,
            text="Esta opción creará un archivo .spec y compilará el proyecto completo",
            text_color="#888888",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w")

        ctk.CTkLabel(
            help_frame,
            text="Replica exactamente la opción 5 de Compile.py",
            text_color="#4dabf7",
            font=ctk.CTkFont(size=12, slant="italic"),
        ).pack(anchor="w", pady=(5, 0))

        # Contenedor principal
        main_container = ctk.CTkFrame(f, fg_color="transparent")
        main_container.pack(fill="both", expand=True, pady=(0, 20))

        # Panel izquierdo: Opciones
        left_panel = ctk.CTkFrame(
            main_container,
            width=350,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
            corner_radius=12,
        )
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        left_panel.grid_propagate(False)

        # Panel derecho: Consola de salida
        right_panel = ctk.CTkFrame(
            main_container,
            fg_color="#1a1a1a",
            border_width=1,
            border_color="#333333",
            corner_radius=12,
        )
        right_panel.pack(side="right", fill="both", expand=True)

        # ===== PANEL IZQUIERDO: OPCIONES =====
        left_content = ctk.CTkFrame(left_panel, fg_color="transparent")
        left_content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            left_content,
            text="⚙️ OPCIONES DE COMPILACIÓN",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff",
        ).pack(anchor="w", pady=(0, 20))

        # Checkbox UPX
        upx_frame = ctk.CTkFrame(left_content, fg_color="transparent")
        upx_frame.pack(fill="x", pady=(0, 15))

        self.upx_var = ctk.BooleanVar(value=False)
        cb_upx = ctk.CTkCheckBox(
            upx_frame,
            text="Usar UPX",
            variable=self.upx_var,
            command=self.actualizar_estado_upx,
            font=ctk.CTkFont(size=13),
            text_color="#cccccc",
        )
        cb_upx.pack(side="left")

        self.upx_status_label = ctk.CTkLabel(
            upx_frame,
            text="(DESACTIVADO)",
            text_color="#F44336",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.upx_status_label.pack(side="right")

        # Checkbox UAC
        uac_frame = ctk.CTkFrame(left_content, fg_color="transparent")
        uac_frame.pack(fill="x", pady=(0, 20))

        self.uac_var = ctk.BooleanVar(value=True)
        cb_uac = ctk.CTkCheckBox(
            uac_frame,
            text="Privilegios Administrador (UAC)",
            variable=self.uac_var,
            command=self.actualizar_estado_uac,
            font=ctk.CTkFont(size=13),
            text_color="#cccccc",
        )
        cb_uac.pack(side="left")

        self.uac_status_label = ctk.CTkLabel(
            uac_frame,
            text="(ACTIVADO)",
            text_color="#4CAF50",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.uac_status_label.pack(side="right")

        # Información sobre opciones
        opciones_info = ctk.CTkLabel(
            left_content,
            text="• UPX: Ejecutable más pequeño (puede causar falsos positivos)\n"
            "• UAC: Pedirá permisos de administrador al ejecutar\n"
            "  (necesario para instalación/archivos del sistema)",
            text_color="#888888",
            font=ctk.CTkFont(size=12),
            justify="left",
        )
        opciones_info.pack(anchor="w", pady=(0, 20))

        # Separador
        ctk.CTkFrame(left_content, height=1, fg_color="#333333").pack(fill="x", pady=10)

        # Verificación de archivos
        ctk.CTkLabel(
            left_content,
            text="📁 VERIFICACIÓN DE ARCHIVOS",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff",
        ).pack(anchor="w", pady=(0, 15))

        archivos_frame = ctk.CTkFrame(left_content, fg_color="transparent")
        archivos_frame.pack(fill="x", pady=(0, 15))

        self.archivos_status = {}
        archivos_esenciales = ["main.py", "config.py"]

        for archivo in archivos_esenciales:
            row = ctk.CTkFrame(archivos_frame, fg_color="transparent")
            row.pack(fill="x", pady=6)

            ctk.CTkLabel(
                row,
                text=archivo,
                font=ctk.CTkFont(size=13),
                text_color="#cccccc",
                width=120,
                anchor="w",
            ).pack(side="left")

            status_label = ctk.CTkLabel(
                row,
                text="...",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100,
                anchor="e",
            )
            status_label.pack(side="right")
            self.archivos_status[archivo] = status_label

        ctk.CTkButton(
            left_content,
            text="🔍 Verificar archivos ahora",
            command=self.verificar_archivos_compilacion,
            height=35,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            border_width=1,
            border_color="#444444",
        ).pack(fill="x", pady=(0, 20))

        # ===== BOTÓN PRINCIPAL DE COMPILACIÓN =====
        self.btn_compile = ctk.CTkButton(
            left_content,
            text="🚀 COMPILAR PROYECTO",
            height=50,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.iniciar_compilacion_completa,
            corner_radius=8,
        )
        self.btn_compile.pack(fill="x", pady=(0, 15))

        # Botón secundario: Solo crear .spec
        ctk.CTkButton(
            left_content,
            text="📄 Solo crear .spec",
            height=40,
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=self.crear_solo_spec,
            corner_radius=8,
        )
        self.btn_solo_spec = ctk.CTkButton(
            left_content,
            text="📄 Solo crear .spec",
            height=40,
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=self.crear_solo_spec,
            corner_radius=8,
        )
        self.btn_solo_spec.pack(fill="x")

        # ===== PANEL DERECHO: CONSOLA =====
        right_content = ctk.CTkFrame(right_panel, fg_color="transparent")
        right_content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            right_content,
            text="📝 SALIDA DE COMPILACIÓN",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff",
        ).pack(anchor="w", pady=(0, 15))

        # Consola de salida
        self.compile_console = ctk.CTkTextbox(
            right_content,
            font=("Consolas", 11),
            wrap="word",
            fg_color="#0f0f0f",
            border_width=1,
            border_color="#333333",
            corner_radius=8,
        )
        self.compile_console.pack(fill="both", expand=True, pady=(0, 15))
        self.compile_console.configure(state="disabled")

        # Barra de estado
        self.compile_status_bar = ctk.CTkFrame(right_content, fg_color="transparent")
        self.compile_status_bar.pack(fill="x")

        self.status_label = ctk.CTkLabel(
            self.compile_status_bar,
            text="Listo para compilar",
            text_color="#888888",
            font=ctk.CTkFont(size=13),
        )
        self.status_label.pack(side="left")

        self.progress_bar = ctk.CTkProgressBar(
            self.compile_status_bar, width=150, height=20, corner_radius=10
        )
        self.progress_bar.pack(side="right", padx=(10, 0))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()

        # Configurar tags de colores para la consola
        self.compile_console.configure(state="normal")
        self.compile_console.tag_config("error", foreground="#F44336")
        self.compile_console.tag_config("success", foreground="#4CAF50")
        self.compile_console.tag_config("warning", foreground="#FF9800")
        self.compile_console.tag_config("info", foreground="#2196F3")
        self.compile_console.configure(state="disabled")

    def actualizar_estado_upx(self):
        """Actualiza la etiqueta de estado UPX - MÉTODO ORIGINAL"""
        if self.upx_var.get():
            self.upx_status_label.configure(text="(ACTIVADO)", text_color="#4CAF50")
        else:
            self.upx_status_label.configure(text="(DESACTIVADO)", text_color="#F44336")

    def actualizar_estado_uac(self):
        """Actualiza la etiqueta de estado UAC - MÉTODO ORIGINAL"""
        if self.uac_var.get():
            self.uac_status_label.configure(text="(ACTIVADO)", text_color="#4CAF50")
        else:
            self.uac_status_label.configure(text="(DESACTIVADO)", text_color="#F44336")

    def verificar_archivos_compilacion(self):
        """Verifica los archivos esenciales para compilación - MÉTODO ORIGINAL"""
        for archivo, label in self.archivos_status.items():
            if Path(archivo).exists():
                label.configure(text="✅ PRESENTE", text_color="#4CAF50")
            else:
                label.configure(
                    text="❌ FALTANTE",
                    text_color="#F44336",
                )

    def mostrar_ayuda_compilacion(self):
        """Muestra ayuda sobre la compilación - MÉTODO ORIGINAL"""
        messagebox.showinfo(
            "En el año del Señor 2026 By MetalWAR - Bajo Licencia MIT",
            "Esta opción:\n\n"
            "1. Verifica archivos esenciales\n"
            "2. Lee la configuración actual\n"
            "3. Crea un archivo .spec con TODOS los recursos\n"
            "4. Compila usando PyInstaller\n\n"
            "El resultado será un ejecutable .exe en la carpeta 'dist/'",
        )

    def escribir_en_consola(self, texto, color="black"):
        """Escribe texto en la consola de compilación - MÉTODO ORIGINAL"""
        self.compile_console.configure(state="normal")

        if color == "error":
            self.compile_console.insert("end", texto, "error")
        elif color == "success":
            self.compile_console.insert("end", texto, "success")
        elif color == "warning":
            self.compile_console.insert("end", texto, "warning")
        elif color == "info":
            self.compile_console.insert("end", texto, "info")
        else:
            self.compile_console.insert("end", texto)

        self.compile_console.see("end")
        self.compile_console.configure(state="disabled")
        self.update()

    def configurar_tags_consola(self):
        """Configura los tags de colores para la consola - MÉTODO ORIGINAL"""
        self.compile_console.configure(state="normal")
        self.compile_console.tag_config("error", foreground="#F44336")
        self.compile_console.tag_config("success", foreground="#4CAF50")
        self.compile_console.tag_config("warning", foreground="#FF9800")
        self.compile_console.tag_config("info", foreground="#2196F3")
        self.compile_console.configure(state="disabled")

    def _crear_packed_dat(self):
        """
        Valida, comprime y genera el archivo packed.dat desde TRANSLATION_FILES_TO_PACK.
        Retorna True si todo es correcto, False en caso de error o carpeta vacía.
        """
        import zipfile
        import os
        from pathlib import Path
        import traceback
        from tkinter import messagebox

        self.escribir_en_consola("📁 Validando contenido de TRANSLATION_FILES_TO_PACK...\n", "info")
        folder_path = Path("TRANSLATION_FILES_TO_PACK")

        # Asegurar que la carpeta existe
        if not folder_path.exists():
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                # Crear .gitkeep
                with open(folder_path / ".gitkeep", "w", encoding="utf-8") as f:
                    pass
                self.escribir_en_consola("📁 Carpeta TRANSLATION_FILES_TO_PACK creada automáticamente.\n", "warning")
            except Exception as e:
                err_msg = f"No se pudo crear la carpeta TRANSLATION_FILES_TO_PACK: {e}"
                self.escribir_en_consola(f"❌ {err_msg}\n", "error")
                self.after(0, lambda: messagebox.showerror("Error de carpeta", err_msg))
                return False

        # Reglas de exclusión
        def es_excluido(p: Path):
            # No incluir .gitkeep
            if p.name == ".gitkeep":
                return True
            # No incluir el propio packed.dat si por error estuviese dentro
            if p.name == "packed.dat":
                return True
            # No incluir caches de python (e.g. __pycache__, .pyc, .pyo, .pyd)
            if "__pycache__" in p.parts:
                return True
            if p.suffix in [".pyc", ".pyo", ".pyd"]:
                return True
            # No incluir archivos temporales (e.g. .tmp, .temp, .bak, .swp, o que empiezan con ~$)
            if p.suffix in [".tmp", ".temp", ".bak", ".swp"]:
                return True
            if p.name.startswith("~$"):
                return True
            return False

        # Encontrar todos los archivos empaquetables
        empaquetables = []
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = Path(root) / file
                    if not es_excluido(file_path):
                        empaquetables.append(file_path)
        except Exception as e:
            err_msg = f"Error al explorar la carpeta de traducción: {e}"
            self.escribir_en_consola(f"❌ {err_msg}\n", "error")
            self.after(0, lambda: messagebox.showerror("Error de exploración", err_msg))
            return False

        # Validación de carpeta vacía
        if not empaquetables:
            msg = "La carpeta TRANSLATION_FILES_TO_PACK está vacía o solo contiene elementos excluidos.\n" \
                  "No se puede generar packed.dat y se cancela la compilación."
            self.escribir_en_consola(f"⚠️ {msg}\n", "warning")
            # Mostrar aviso claro en la GUI
            self.after(0, lambda: messagebox.showwarning("Carpeta vacía", msg))
            return False

        self.escribir_en_consola(f"📦 Encontrados {len(empaquetables)} archivos empaquetables.\n", "info")

        # Generación segura usando un archivo temporal
        temp_packed = Path("packed.dat.tmp")
        try:
            # Comprimir recursivamente conservando rutas relativas respecto a TRANSLATION_FILES_TO_PACK
            with zipfile.ZipFile(temp_packed, "w", zipfile.ZIP_DEFLATED) as zip_f:
                for file_path in empaquetables:
                    # Ruta relativa respecto a TRANSLATION_FILES_TO_PACK
                    rel_path = file_path.relative_to(folder_path)
                    self.escribir_en_consola(f"   ➕ Añadiendo: {rel_path}\n")

                    # Forzar lectura para verificar que es legible. Si falla, lanzará excepción.
                    with open(file_path, "rb") as f_test:
                        # Leer un fragmento para estar seguros de que es accesible
                        f_test.read(1024)

                    zip_f.write(file_path, rel_path)

            # Verificar validez del archivo zip generado
            with zipfile.ZipFile(temp_packed, "r") as zip_f:
                bad_file = zip_f.testzip()
                if bad_file is not None:
                    raise Exception(f"El archivo ZIP temporal generado está corrupto (primer error en: {bad_file})")

            # Reemplazo seguro
            dest_packed = Path("packed.dat")
            if temp_packed.exists():
                if dest_packed.exists():
                    os.remove(dest_packed)
                os.rename(temp_packed, dest_packed)

            self.escribir_en_consola("✅ packed.dat generado y reemplazado con éxito.\n", "success")
            return True

        except Exception as e:
            # Limpiar archivo temporal si quedó a medias
            if temp_packed.exists():
                try:
                    os.remove(temp_packed)
                except:
                    pass

            err_msg = f"Error durante el empaquetado de archivos: {e}"
            self.escribir_en_consola(f"❌ {err_msg}\n", "error")
            self.escribir_en_consola(traceback.format_exc(), "error")
            self.after(0, lambda: messagebox.showerror("Error de empaquetado", err_msg))
            return False

    def iniciar_compilacion_completa(self):
        """Inicia el proceso completo de compilación - MÉTODO ORIGINAL"""
        self.compile_console.configure(state="normal")
        self.compile_console.delete("1.0", "end")
        self.compile_console.configure(state="disabled")

        self.configurar_tags_consola()

        self.btn_compile.configure(state="disabled")
        self.btn_solo_spec.configure(state="disabled")
        self.status_label.configure(text="Compilando...", text_color="#2196F3")
        self.progress_bar.pack(side="right", padx=(10, 0))
        self.progress_bar.set(0)

        threading.Thread(target=self.proceso_compilacion_completa).start()

    def proceso_compilacion_completa(self):
        """Proceso principal de compilación - MÉTODO ORIGINAL"""
        try:
            import time

            self.escribir_en_consola("=" * 60 + "\n", "info")
            self.escribir_en_consola("🚀 COMPILACIÓN INICIADA\n", "info")
            self.escribir_en_consola("=" * 60 + "\n\n", "info")

            # PASO 1: Verificar archivos esenciales
            self.escribir_en_consola(
                "1. 🔍 VERIFICANDO ARCHIVOS ESENCIALES...\n", "info"
            )
            esenciales = ["main.py", "config.py"]
            faltan = []

            for archivo in esenciales:
                if Path(archivo).exists():
                    self.escribir_en_consola(f"   ✅ {archivo}\n", "success")
                else:
                    self.escribir_en_consola(f"   ❌ {archivo}\n", "error")
                    faltan.append(archivo)

            if faltan:
                self.escribir_en_consola(f"\n❌ FALTAN: {', '.join(faltan)}\n", "error")
                self.escribir_en_consola("   No se puede continuar.\n", "error")
                return

            self.escribir_en_consola(
                "   ✅ Todos los archivos esenciales encontrados\n\n", "success"
            )
            self.progress_bar.set(0.1)

            # PASO 2: Leer configuración
            self.escribir_en_consola("2. 📖 LEYENDO CONFIGURACIÓN...\n", "info")
            config = self.leer_config_para_compilacion()

            if not config:
                self.escribir_en_consola("   ⚠ No se pudo leer config.py\n", "warning")
                self.escribir_en_consola("   ¿Usar valores por defecto? (Sí)\n", "info")
                config = {"GAME_NAME_DISPLAY": "MetalWar"}

            self.escribir_en_consola("   ✅ Configuración cargada\n\n", "success")
            self.progress_bar.set(0.15)

            # PASO 2.5: Crear packed.dat
            self.escribir_en_consola("2.5. 📦 CREANDO PACKED.DAT...\n", "info")
            if not self._crear_packed_dat():
                self.escribir_en_consola("\n❌ Cancelando compilación por error en packed.dat\n", "error")
                self.progress_bar.set(0)
                self.status_label.configure(
                    text="❌ Error en packed.dat", text_color="#F44336"
                )
                return

            self.progress_bar.set(0.2)

            # PASO 3: Crear spec
            self.escribir_en_consola("3. 📄 CREANDO ARCHIVO .SPEC...\n", "info")
            spec_file = self.crear_spec_gui(config, self.upx_var.get())

            if not spec_file:
                self.escribir_en_consola(
                    "   ❌ No se pudo crear el archivo .spec\n", "error"
                )
                return

            self.escribir_en_consola(
                f"   ✅ {spec_file} creado correctamente\n\n", "success"
            )
            self.progress_bar.set(0.4)

            # PASO 4: Confirmar compilación
            self.escribir_en_consola("4. 🤔 ¿COMPILAR AHORA?\n", "info")
            self.escribir_en_consola("   (Se procederá con la compilación)\n\n", "info")
            self.progress_bar.set(0.5)

            # PASO 5: Compilar
            self.escribir_en_consola(
                "5. 🔨 INICIANDO COMPILACIÓN CON PYINSTALLER...\n", "info"
            )
            self.escribir_en_consola(
                "   ⚠ Esto puede tomar varios minutos...\n\n", "warning"
            )

            resultado = self.compilar_con_spec_gui(spec_file)

            if resultado:
                self.escribir_en_consola("\n" + "=" * 60 + "\n", "success")
                self.escribir_en_consola("🎮 ¡COMPILACIÓN EXITOSA!\n", "success")
                self.escribir_en_consola("=" * 60 + "\n\n", "success")
                self.progress_bar.set(1.0)
                self.status_label.configure(
                    text="✅ Compilación exitosa", text_color="#4CAF50"
                )

                self.after(100, self.preguntar_abrir_carpeta)
            else:
                self.progress_bar.set(0)
                self.status_label.configure(
                    text="❌ Compilación fallida", text_color="#F44336"
                )

        except Exception as e:
            self.escribir_en_consola(f"\n❌ ERROR INESPERADO: {str(e)}\n", "error")
            import traceback

            self.escribir_en_consola(traceback.format_exc(), "error")
            self.progress_bar.set(0)
            self.status_label.configure(text="❌ Error", text_color="#F44336")

        finally:
            self.btn_compile.configure(state="normal")
            self.btn_solo_spec.configure(state="normal")

    def leer_config_para_compilacion(self):
        """Lee config.py para compilación - MÉTODO ORIGINAL"""
        try:
            if not Path("config.py").exists():
                return None

            with open("config.py", "r", encoding="utf-8") as f:
                content = f.read()

            match = re.search(
                r"GAME_CONFIG\s*=\s*({.*?})\s*(?:\n|$)", content, re.DOTALL
            )
            if match:
                config_str = match.group(1)
                config = ast.literal_eval(config_str)
                return config

            return None

        except Exception as e:
            self.escribir_en_consola(f"   ❌ Error leyendo config: {e}\n", "error")
            return None

    def crear_spec_gui(self, config, usar_upx):
        """Crea archivo .spec - MÉTODO ORIGINAL"""
        try:
            usar_uac = hasattr(self, "uac_var") and self.uac_var.get()

            if config and "GAME_NAME_DISPLAY" in config:
                nombre_juego = config["GAME_NAME_DISPLAY"].replace(" ", "_")
            else:
                nombre_juego = "MetalWar"

            nombre_exe = f"{nombre_juego}.exe"
            spec_file = f"{nombre_juego}.spec"

            self.escribir_en_consola("   🔍 Buscando recursos...\n", "info")

            datos = []

            archivos_py = [
                "config.py",
                "main.py",
                "effects.py",
                "audio.py",
                "ui.py",
                "utils.py",
                "installer.py",
            ]
            for archivo in archivos_py:
                if Path(archivo).exists():
                    datos.append((archivo, "."))
                    self.escribir_en_consola(f"      📄 {archivo}\n", "info")

            import glob

            patrones_audio = [
                "*.mp3",
                "*.ogg",
                "*.wav",
                "*.flac",
                "*.mod",
                "*.xm",
                "*.s3m",
                "*.it",
                "*.stm",
                "*.mtm",
            ]

            patrones = [
                "*.png",
                "*.jpg",
                "*.ico",
                "*.jpeg",
                "*.bmp",
                *patrones_audio,
                "*.ttf",
                "*.otf",
                "*.json",
                "*.txt",
                "*.dat",
                "*.xml",
                "*.exe",
                "*.dll",
            ]

            for patron in patrones:
                for archivo in glob.glob(patron):
                    if archivo in [
                        "compile.py",
                        "compilador.py",
                        "Compiler_GUI.py",
                        "Compiler_GUI_v3.py",
                    ]:
                        continue
                    if Path(archivo).is_file():
                        if (archivo, ".") not in datos:
                            datos.append((archivo, "."))

                            if archivo.lower().endswith(".it"):
                                self.escribir_en_consola(
                                    f"      🎵 {archivo} (.it incluido)\n", "info"
                                )

            self.escribir_en_consola(
                f"      ✅ {len(datos)} recursos encontrados\n", "success"
            )

            archivos_it = [f for f in datos if f[0].lower().endswith(".it")]
            if archivos_it:
                self.escribir_en_consola(
                    f"      🎵 {len(archivos_it)} archivo(s) .it incluido(s)\n",
                    "success",
                )

            uac_comment = (
                "CON PRIVILEGIOS ADMINISTRATIVOS"
                if usar_uac
                else "SIN privilegios administrativos"
            )
            spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
# MetalWar - Archivo de especificación
# {uac_comment}

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas={datos},
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Splash screen
"""

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

            # Usar repr() para escapar automáticamente
            spec_content += f"""exe = EXE(
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
    name={repr(nombre_exe)},
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx={'True' if usar_upx else 'False'},
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
"""

            if usar_uac:
                spec_content += (
                    "    uac_admin=True,  # PRIVILEGIOS ADMINISTRATIVOS ACTIVADOS\n"
                )

            if Path("icon.ico").exists():
                spec_content += f"    icon={repr('icon.ico')},\n"

            if Path("splash.png").exists():
                spec_content += f"    splash={repr('splash.png')},\n"

            if Path("version_info.txt").exists():
                spec_content += f"    version={repr('version_info.txt')},\n"

            spec_content += ")\n"

            with open(spec_file, "w", encoding="utf-8") as f:
                f.write(spec_content)

            self.escribir_en_consola(f"   📄 {spec_file} creado\n", "success")

            self.escribir_en_consola(f"   ⚙  Ejecutable: {nombre_exe}\n", "info")
            self.escribir_en_consola(f"   📦 Recursos: {len(datos)} archivos\n", "info")
            self.escribir_en_consola(
                f"   🔧 UPX: {'ACTIVADO' if usar_upx else 'DESACTIVADO'}\n", "info"
            )
            self.escribir_en_consola(
                f"   ⚡ UAC: {'ADMINISTRADOR (pedirá permisos elevados)' if usar_uac else 'USUARIO NORMAL (sin UAC)'}\n",
                "info",
            )

            if archivos_it:
                self.escribir_en_consola(
                    f"   🎵 Archivos .it incluidos: {len(archivos_it)}\n", "info"
                )
                for archivo_it in archivos_it[:3]:
                    self.escribir_en_consola(f"      • {archivo_it[0]}\n", "info")
                if len(archivos_it) > 3:
                    self.escribir_en_consola(
                        f"      • ... y {len(archivos_it)-3} más\n", "info"
                    )

            return spec_file

        except Exception as e:
            self.escribir_en_consola(f"   ❌ Error creando spec: {e}\n", "error")
            import traceback

            traceback.print_exc()
            return None

    def compilar_con_spec_gui(self, spec_file):
        """Compila con .spec - MÉTODO ORIGINAL"""
        try:
            if not Path(spec_file).exists():
                self.escribir_en_consola(
                    f"   ❌ Archivo {spec_file} no encontrado\n", "error"
                )
                return False

            if not Path("main.py").exists():
                self.escribir_en_consola("   ❌ main.py NO ENCONTRADO\n", "error")
                return False

            comando = [
                "pyinstaller",
                "--clean",
                "--noconfirm",
                spec_file,
            ]

            self.escribir_en_consola(f"   🔨 Comando: {' '.join(comando)}\n", "info")

            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                shell=True,
                timeout=900,
            )

            if resultado.stdout:
                for linea in resultado.stdout.split("\n"):
                    if "error" in linea.lower() or "failed" in linea.lower():
                        self.escribir_en_consola(f"      ✗ {linea}\n", "error")
                    elif "warning" in linea.lower():
                        self.escribir_en_consola(f"      ⚠ {linea}\n", "warning")
                    elif "info" in linea.lower() or "checking" in linea.lower():
                        self.escribir_en_consola(f"      ℹ {linea}\n", "info")
                    elif linea.strip():
                        self.escribir_en_consola(f"      {linea}\n", "info")

            if resultado.returncode == 0:
                self.escribir_en_consola("\n   ✅ ¡COMPILACIÓN EXITOSA!\n", "success")

                spec_path = Path(spec_file)
                nombre_base = spec_path.stem
                exe_path = Path("dist") / f"{nombre_base}.exe"

                if exe_path.exists():
                    tamaño = exe_path.stat().st_size / (1024 * 1024)
                    self.escribir_en_consola(f"   📍 Ubicación: {exe_path}\n", "info")
                    self.escribir_en_consola(f"   📏 Tamaño: {tamaño:.2f} MB\n", "info")
                    return True
                else:
                    self.escribir_en_consola(
                        "   ⚠ No se encontró .exe en 'dist/'\n", "warning"
                    )
                    return False
            else:
                self.escribir_en_consola("\n   ❌ COMPILACIÓN FALLIDA\n", "error")
                if resultado.stderr:
                    self.escribir_en_consola(
                        f"   📛 Errores:\n{resultado.stderr}\n", "error"
                    )
                return False

        except subprocess.TimeoutExpired:
            self.escribir_en_consola(
                "   ⏰ TIMEOUT - La compilación tardó más de 15 minutos\n", "error"
            )
            return False
        except Exception as e:
            self.escribir_en_consola(f"   ❌ Error inesperado: {e}\n", "error")
            return False

    def crear_solo_spec(self):
        """Crea solo el archivo .spec sin compilar - MÉTODO ORIGINAL"""
        try:
            self.escribir_en_consola("📄 CREANDO SOLO ARCHIVO .SPEC...\n", "info")

            if not Path("main.py").exists():
                self.escribir_en_consola("   ❌ main.py no encontrado\n", "error")
                return

            config = self.leer_config_para_compilacion()
            if not config:
                config = {"GAME_NAME_DISPLAY": "MetalWar"}

            spec_file = self.crear_spec_gui(config, self.upx_var.get())

            if spec_file:
                self.escribir_en_consola(
                    f"\n✅ Archivo .spec creado: {spec_file}\n", "success"
                )
                self.escribir_en_consola(
                    "   Puedes editarlo manualmente antes de compilar\n", "info"
                )

        except Exception as e:
            self.escribir_en_consola(f"❌ Error: {e}\n", "error")

    def preguntar_abrir_carpeta(self):
        """Pregunta si abrir la carpeta del ejecutable - MÉTODO ORIGINAL"""
        respuesta = messagebox.askyesno(
            "Compilación Exitosa",
            "✅ ¡Compilación completada!\n\n"
            "¿Quieres abrir la carpeta del ejecutable?",
        )

        if respuesta:
            try:
                if Path("dist").exists():
                    if os.name == "nt":
                        os.startfile("dist")
                    elif os.name == "posix":
                        subprocess.run(["xdg-open", "dist"])
                else:
                    messagebox.showwarning(
                        "Carpeta no encontrada", "No se encontró la carpeta 'dist'"
                    )
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}")


# ============================================================================
# INICIO DE LA APLICACIÓN
# ============================================================================

if __name__ == "__main__":
    app = MetalWarCompilerApp()
    app.mainloop()
