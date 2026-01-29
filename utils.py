# utils.py
# Utilidades generales y funciones de apoyo
# Manejo de recursos, matemáticas básicas y efectos visuales

import os
import sys
import pygame
import random
from dataclasses import dataclass

# ============================================================================
# IMPORTS OPCIONALES
# ============================================================================

# Numpy para cálculos vectorizados (opcional, mejora rendimiento)
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Pyttsx3 para síntesis de voz (opcional)
try:
    import pyttsx3

    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# ============================================================================
# ESTRUCTURAS DE DATOS
# ============================================================================


@dataclass
class Point3D:
    """Representa un punto en espacio 3D con coordenadas x, y, z"""

    x: float
    y: float
    z: float


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================


def clamp_val(val):
    """
    Limita un valor entre 0 y 255
    Útil para componentes de color RGB
    """
    return int(max(0, min(255, val)))


def SIN(angle):
    """
    Calcula el seno de un ángulo
    Args:
        angle: Ángulo en grados
    Returns:
        Seno del ángulo
    """
    import math

    return math.sin(math.radians(angle))


def COS(angle):
    """
    Calcula el coseno de un ángulo
    Args:
        angle: Ángulo en grados
    Returns:
        Coseno del ángulo
    """
    import math

    return math.cos(math.radians(angle))


PI = 3.141592653589793


def safe_color(color_tuple):
    """
    Asegura que todos los componentes de un color estén en rango 0-255
    Args:
        color_tuple: Tupla (R, G, B) o (R, G, B, A)
    Returns:
        Tupla con valores clampados
    """
    return tuple(clamp_val(c) for c in color_tuple)


def resource_path(relative_path):
    """
    Obtiene la ruta absoluta a un recurso, compatible con PyInstaller
    PyInstaller crea un temp folder y almacena la ruta en _MEIPASS
    """
    try:
        # PyInstaller crea un folder temporal en _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Si no estamos en un ejecutable, usa el path actual
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def clean_temp_files():
    """
    Limpia archivos de audio temporales generados por síntesis de voz
    Se ejecuta al cerrar la aplicación
    """
    temp_files = [
        "temp_intro.wav",
        "temp_armed.wav",
        "temp_blast.wav",
        "temp_locked.wav",
        "temp_firing.wav",
    ]

    for filename in temp_files:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                # Silenciar errores de eliminación
                pass


def draw_circle_alpha(surface, color, center, radius):
    """
    Dibuja un círculo con transparencia (alpha)
    Args:
        surface: Superficie de Pygame donde dibujar
        color: Tupla (R, G, B, A) con transparencia
        center: Tupla (x, y) del centro del círculo
        radius: Radio del círculo
    """
    if radius < 1:
        return

    try:
        # Extraer componentes de color con transparencia
        r, g, b = clamp_val(color[0]), clamp_val(color[1]), clamp_val(color[2])
        a = clamp_val(color[3] if len(color) > 3 else 255)

        # Crear superficie temporal con alpha channel
        surf = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (r, g, b, a), (radius, radius), radius)

        # Dibujar con blending alpha
        surface.blit(
            surf,
            (center[0] - radius, center[1] - radius),
            special_flags=pygame.BLEND_ALPHA_SDL2,
        )
    except Exception:
        # Fallback silencioso en caso de error
        pass


def apply_glitch(surface, intensity, width, height):
    """
    Aplica efecto glitch cromático y desplazamiento aleatorio
    Args:
        surface: Superficie a modificar
        intensity: Intensidad del efecto (0.0 a 1.0)
        width, height: Dimensiones de la superficie
    Returns:
        Superficie con efecto glitch aplicado
    """
    if intensity <= 0.05:
        return surface

    # Desplazamiento cromático (efecto de canales separados)
    offset = int(intensity * 15)
    copy_surf = surface.copy()

    # Crear versiones de canales desplazados
    red_channel = copy_surf.copy()
    red_channel.fill((0, 255, 255), special_flags=pygame.BLEND_RGB_SUB)

    blue_channel = copy_surf.copy()
    blue_channel.fill((255, 255, 0), special_flags=pygame.BLEND_RGB_SUB)

    # Aplicar desplazamiento cromático
    surface.blit(red_channel, (-offset, 0), special_flags=pygame.BLEND_RGB_ADD)
    surface.blit(blue_channel, (offset, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Efecto de desplazamiento aleatorio de líneas (scanline glitch)
    if random.random() < 0.4:
        strip_height = random.randint(5, 20)
        strip_y = random.randint(0, height - strip_height)
        shift_amount = random.randint(-30, 30)

        # Copiar y desplazar una franja horizontal
        strip = surface.subsurface(0, strip_y, width, strip_height).copy()
        surface.blit(strip, (shift_amount, strip_y))

    return surface
