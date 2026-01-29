# effects.py
# Efectos visuales avanzados para MetalWar
# Incluye geometría 3D, partículas, analizador de espectro y secuencias especiales

import pygame
import random
import math
import time
import os
import colorsys
from config import GAME_CONFIG
from utils import (
    Point3D,
    clamp_val,
    safe_color,
    draw_circle_alpha,
    resource_path,
    NUMPY_AVAILABLE,
)

# Import condicional de numpy (mejora rendimiento si disponible)
if NUMPY_AVAILABLE:
    import numpy as np

# ============================================================================
# OPTIMIZACIONES: Cache de funciones matemáticas para bucles intensivos
# ============================================================================
SIN = math.sin
COS = math.cos
PI = math.pi
SQRT = math.sqrt

# ============================================================================
# CLASE STARFIELD: Fondo estelar con efecto de movimiento 3D
# ============================================================================


class Starfield:
    """
    Campo de estrellas 3D ULTRA AGRESIVO & BPM REACTIVE
    Características:
    - Warp explosivo sincronizado con Beats.
    - Rotación de cámara tipo 'Scratch' o 'Barrel Roll'.
    - Paletas de colores dinámicas por compás.
    - Estelas de luz (Light Trails).
    """

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.num_stars = 250  # Densidad media-alta

        # Paletas de colores para alternar (Cyberpunk, Matrix, Inferno, Ice)
        self.palettes = [
            [(0, 255, 255), (255, 0, 255), (255, 255, 255)],  # Cyberpunk
            [(0, 255, 0), (50, 255, 50), (200, 255, 200)],  # Matrix
            [(255, 50, 0), (255, 150, 0), (255, 255, 0)],  # Inferno
            [(100, 100, 255), (200, 200, 255), (255, 255, 255)],  # Ice
        ]
        self.current_palette_idx = 0

        self.stars = []
        self._init_stars()

        # Variables de física y cámara
        self.camera_z = 0.0
        self.angle = 0.0
        self.angle_vel = 0.002  # Velocidad rotación base

        # Variables BPM reactivas
        self.warp_factor = 1.0  # Multiplicador de velocidad (golpe de beat)
        self.fov_pulse = 0.0  # Pulsación del campo de visión (zoom in/out)

    def _init_stars(self):
        """Inicializa estrellas con propiedades extendidas"""
        self.stars = []
        palette = self.palettes[self.current_palette_idx]

        for _ in range(self.num_stars):
            self.stars.append(
                {
                    "x": random.uniform(-self.w, self.w),
                    "y": random.uniform(-self.h, self.h),
                    "z": random.uniform(10, self.w * 2),
                    "base_color": random.choice(palette),  # Color asignado
                    "prev_sx": None,
                    "prev_sy": None,
                }
            )

    def draw(self, surface, intensity, bpm_data=None):
        """
        Dibuja el Starfield reactivo.
        """
        cx, cy = self.w // 2, self.h // 2

        # ====================================================================
        # 1. PROCESAMIENTO BPM (REACCIÓN MUSICAL)
        # ====================================================================
        is_strong_beat = False
        beat_pulse = 0.0

        if bpm_data:
            beat_pulse = bpm_data.get("beat_pulse", 0.0)  # 1.0 en el golpe, decae a 0.0
            is_strong_beat = bpm_data.get("strong_beat", False)

            # Cambio de paleta cada 16 o 32 beats (cambio de sección musical)
            if is_strong_beat and random.random() < 0.05:
                self.current_palette_idx = (self.current_palette_idx + 1) % len(
                    self.palettes
                )
                palette = self.palettes[self.current_palette_idx]
                for s in self.stars:
                    if random.random() < 0.1:
                        s["base_color"] = random.choice(palette)

        # ====================================================================
        # 2. FÍSICA AGRESIVA
        # ====================================================================

        # Warp Factor: El beat empuja la velocidad.
        target_warp = 1.0 + (beat_pulse * 12.0) + (intensity * 4.0)
        self.warp_factor = self.warp_factor * 0.9 + target_warp * 0.1

        # Velocidad final
        speed = 8.0 * self.warp_factor

        # Rotación de Cámara:
        rotation_kick = beat_pulse * 0.05 * (1 if random.random() > 0.5 else -1)
        self.angle += self.angle_vel + rotation_kick

        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        # FOV (Zoom) dinámico
        fov = 350 + (beat_pulse * 150) + (intensity * 50)

        # ====================================================================
        # 3. RENDERIZADO Y LÓGICA DE ESTRELLAS
        # ====================================================================

        for star in self.stars:
            # MOVER Z
            star["z"] -= speed

            # Respawn
            if star["z"] <= 1:
                star["z"] = self.w * 2
                star["x"] = random.uniform(-self.w, self.w)
                star["y"] = random.uniform(-self.h, self.h)
                star["prev_sx"] = None
                star["prev_sy"] = None
                palette = self.palettes[self.current_palette_idx]
                star["base_color"] = random.choice(palette)
                continue

            # ROTACIÓN 2D
            rx = star["x"] * cos_a - star["y"] * sin_a
            ry = star["x"] * sin_a + star["y"] * cos_a

            # PROYECCIÓN
            factor = fov / max(0.1, star["z"])
            sx = int(rx * factor + cx)
            sy = int(ry * factor + cy)

            # DIBUJO
            if 0 <= sx < self.w and 0 <= sy < self.h:
                # Brillo por profundidad
                depth_b = 1.0 - (star["z"] / (self.w * 2))
                brightness = min(1.0, max(0.0, depth_b))

                # Potenciar brillo con el beat
                brightness += beat_pulse * 0.5
                if brightness > 1.0:
                    brightness = 1.0

                col = star["base_color"]
                final_color = (
                    int(col[0] * brightness),
                    int(col[1] * brightness),
                    int(col[2] * brightness),
                )

                # WARP LINES (Estelas agresivas)
                draw_line = False

                if star["prev_sx"] is not None:
                    dist_sq = (sx - star["prev_sx"]) ** 2 + (sy - star["prev_sy"]) ** 2

                    if dist_sq > 25 or self.warp_factor > 2.0:
                        draw_line = True
                        width = 1
                        if star["z"] < 300:
                            width = 2
                        if is_strong_beat and star["z"] < 500:
                            width = 3

                        pygame.draw.line(
                            surface,
                            final_color,
                            (star["prev_sx"], star["prev_sy"]),
                            (sx, sy),
                            width,
                        )

                if not draw_line:
                    surface.set_at((sx, sy), final_color)

            # Guardar histórico
            star["prev_sx"] = sx
            star["prev_sy"] = sy

    def toggle_palette(self):
        """Fuerza cambio manual de paleta"""
        self.current_palette_idx = (self.current_palette_idx + 1) % len(self.palettes)


# ============================================================================
# CLASE GEOMETRICTRANSFORMER3D
# ============================================================================


class GeometricTransformer3D:
    """
    Sistema de transformación 3D con múltiples formas geométricas
    """

    def __init__(self, width, height):
        self.w, self.h = width, height

        # Formas geométricas disponibles
        self.shapes = ["SPHERE", "TORUS", "KNOT", "CYLINDER"]
        self.curr = 0
        self.tp = 0.0
        self.lt = time.time()
        self.it = False
        self.rot = Point3D(0, 0, 0)
        self.dragging = False
        self.last_mouse = (0, 0)

        # Efectos especiales
        self.electric_pulses = []
        self.particle_trails = []
        self.plasma_time = 0.0

        # Resolución de malla
        self.rows = 20
        self.cols = 30

        # Optimización: Superficie persistente para efectos fantasma
        self.ghost_surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # Generar geometría inicial
        self.gen()

    def gen(self):
        """Genera la geometría base para todas las formas"""
        self.sd = {}
        self.ed = []

        cols = self.cols
        rows = self.rows

        # GENERAR ARISTAS
        for i in range(rows):
            row_offset = i * cols
            next_row_offset = (i + 1) * cols

            for j in range(cols):
                current_vertex = row_offset + j
                self.ed.append((current_vertex, row_offset + (j + 1) % cols))

                if i < rows - 1:
                    self.ed.append((current_vertex, next_row_offset + j))

        # GENERAR VÉRTICES PARA CADA FORMA
        for shape_name in self.shapes:
            vertices = []

            for i in range(rows):
                u = i / (rows - 1) if rows > 1 else 0

                for j in range(cols):
                    v_param = j / cols
                    theta = v_param * 2 * PI
                    phi = u * PI

                    x, y, z = 0, 0, 0

                    if shape_name == "SPHERE":
                        radius = 1.0
                        sin_phi = SIN(phi)
                        x = radius * sin_phi * COS(theta)
                        y = radius * COS(phi)
                        z = radius * sin_phi * SIN(theta)

                    elif shape_name == "TORUS":
                        R, r_torus = 1.0, 0.4
                        a = u * 2 * PI
                        common = R + r_torus * COS(a)
                        x = common * COS(theta)
                        y = common * SIN(theta)
                        z = r_torus * SIN(a)

                    elif shape_name == "CYLINDER":
                        x = COS(theta)
                        z = SIN(theta)
                        y = (u - 0.5) * 2.5

                    elif shape_name == "KNOT":
                        p, q = 2, 3
                        r = 0.5 + 0.2 * COS(phi)
                        common = (2 + COS(p * theta)) * 0.5
                        x = r * COS(q * theta) * common
                        y = r * SIN(q * theta) * common
                        z = r * SIN(p * theta)

                    vertices.append(Point3D(x, y, z))

            self.sd[shape_name] = vertices

    def handle_input(self, event):
        """Maneja eventos de entrada para rotación manual"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if event.pos[1] < self.h - 100:
                self.dragging = True
                self.last_mouse = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            dx = event.pos[0] - self.last_mouse[0]
            dy = event.pos[1] - self.last_mouse[1]

            self.rot.y += dx * 0.01
            self.rot.x += dy * 0.01
            self.last_mouse = event.pos

    def get_plasma_color(self, x, y, z, time_val, intensity):
        """Calcula color de efecto plasma basado en posición y tiempo"""
        v = (
            SIN(x * 1.5 + time_val * 0.8)
            + SIN(y * 2.3 + time_val * 1.2)
            + SIN(z * 3.1 + time_val * 0.5)
            + SIN((x + y + z) * 0.7 + time_val * 2.0)
        ) * 0.25

        plasma_val = (v + 1) * 0.5
        plasma_val = min(1.0, plasma_val + intensity * 0.3)

        if plasma_val < 0.5:
            if plasma_val < 0.25:
                r, g, b = (
                    int(1020 * plasma_val),
                    int(200 * plasma_val),
                    int(255 * (0.5 + plasma_val)),
                )
            else:
                f = (plasma_val - 0.25) * 4
                r, g, b = (
                    int(255 * (1 - f * 0.5)),
                    int(255 * f),
                    int(150 * (1 - plasma_val)),
                )
        else:
            if plasma_val < 0.75:
                r, g, b = (
                    int(200 + 55 * SIN(time_val * 3)),
                    int(100 + 155 * plasma_val),
                    int(255 * (plasma_val - 0.5) * 2),
                )
            else:
                f = (plasma_val - 0.75) * 4
                r, g, b = 255, int(255 * (1 - f)), int(255 * f)

        boost = intensity * 0.8 * 255
        if boost > 1:
            r = min(255, int(r + boost * 0.23))
            g = min(255, int(g + boost * 0.15))
            b = min(255, int(b + boost * 0.31))

        return (r, g, b)

    def get_heatmap_color(self, val):
        """Color basado en mapa de calor (valor 0.0-1.0)"""
        val = max(0.0, min(1.0, val))
        hue = 0.7 - (val * 0.7)
        saturation = 1.0
        value = 1.0

        if val > 0.9:
            saturation = max(0.0, 1.0 - ((val - 0.9) * 10.0))
            hue = 0.0

        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return (int(r * 255), int(g * 255), int(b * 255))

    def draw(self, surface, intensity, main_time, current_fmt=None, bpm_state=None):
        """Dibuja la geometría 3D con efectos"""
        self.plasma_time += 0.03

        # EXTRACCIÓN DE PARÁMETROS BPM
        bpm_enabled = bpm_state.get("enabled", True) if bpm_state else True
        bpm_strong = bpm_state.get("strong_beat", False) if bpm_state else False

        adjusted_intensity = (
            min(1.0, intensity + 0.3) if (bpm_enabled and bpm_strong) else intensity
        )
        if bpm_enabled and bpm_state:
            adjusted_intensity += bpm_state.get("beat_pulse", 0.0) * 0.2

        # LÓGICA DE TRANSICIÓN
        current_time = time.time()
        dt = current_time - self.lt

        if not self.it:
            if dt > 5.0:
                self.it = True
                self.lt = current_time
        else:
            self.tp = min(1.0, dt / 2.0)
            if self.tp >= 1:
                self.tp = 0
                self.it = False
                self.curr = (self.curr + 1) % len(self.shapes)
                self.lt = current_time

        # ROTACIÓN AUTOMÁTICA
        if not self.dragging:
            speed = 0.01 + (adjusted_intensity * 0.05)
            if bpm_enabled and bpm_strong:
                speed += 0.02

            self.rot.x += speed * 0.5
            self.rot.y += speed
            self.rot.z += speed * 0.2

        # PREPARACIÓN DE GEOMETRÍA
        vertices_current = self.sd[self.shapes[self.curr]]
        vertices_next = self.sd[self.shapes[(self.curr + 1) % len(self.shapes)]]

        et = self.tp * self.tp * (3 - 2 * self.tp)
        pulse = 1.0 + (adjusted_intensity * 0.3)
        if bpm_enabled and bpm_strong:
            pulse += 0.2

        # PARÁMETROS DE PROYECCIÓN 3D
        fov = 500
        center_x, center_y = self.w // 2, self.h // 2

        cos_rx, sin_rx = COS(self.rot.x), SIN(self.rot.x)
        cos_ry, sin_ry = COS(self.rot.y), SIN(self.rot.y)
        cos_rz, sin_rz = COS(self.rot.z), SIN(self.rot.z)

        projected_points = [None] * len(vertices_current)
        vertex_3d = [None] * len(vertices_current)
        depths = [0.0] * len(vertices_current)

        jitter_active = adjusted_intensity > 0.8 or (bpm_enabled and bpm_strong)
        jitter_range = 0.08 if (bpm_enabled and bpm_strong) else 0.05

        # TRANSFORMACIÓN DE VÉRTICES
        for i in range(len(vertices_current)):
            p1 = vertices_current[i]
            p2 = vertices_next[i]

            x = p1.x + (p2.x - p1.x) * et
            y = p1.y + (p2.y - p1.y) * et
            z = p1.z + (p2.z - p1.z) * et

            if jitter_active:
                pulse_factor = pulse + random.uniform(-jitter_range, jitter_range)
            else:
                pulse_factor = pulse

            x *= pulse_factor
            y *= pulse_factor
            z *= pulse_factor

            # ROTACIÓN 3D
            rx = x * cos_ry - z * sin_ry
            rz = x * sin_ry + z * cos_ry
            ry = y

            new_ry = ry * cos_rx - rz * sin_rx
            rz = ry * sin_rx + rz * cos_rx
            ry = new_ry

            new_rx = rx * cos_rz - ry * sin_rz
            ry = rx * sin_rz + ry * cos_rz
            rx = new_rx

            vertex_3d[i] = (rx, ry, rz)
            depths[i] = rz

            divisor = 4.0 + rz
            if divisor == 0:
                divisor = 0.001

            factor = fov / divisor
            projected_points[i] = (
                int(rx * factor + center_x),
                int(ry * factor + center_y),
            )

        # CONFIGURACIÓN DE RENDERIZADO
        min_z, max_z = min(depths), max(depths)
        z_range = max_z - min_z if max_z != min_z else 1.0

        use_plasma = (
            current_fmt in ["mod", "s3m", "xm", "it"] or adjusted_intensity > 0.7
        )

        bpm_heat_boost = (
            0.3
            if (bpm_enabled and bpm_strong)
            else (0.15 if (bpm_enabled and bpm_state.get("medium_beat")) else 0.0)
        )

        # GENERACIÓN DE PARTÍCULAS
        if adjusted_intensity > 0.5:
            spawn_chance = 0.2 if (bpm_enabled and bpm_strong) else 0.05

            if random.random() < spawn_chance:
                idx = random.randint(0, len(projected_points) - 1)
                pos = projected_points[idx]

                if 0 <= pos[0] < self.w and 0 <= pos[1] < self.h:
                    v3d = vertex_3d[idx]

                    if use_plasma:
                        color = self.get_plasma_color(
                            v3d[0],
                            v3d[1],
                            v3d[2],
                            self.plasma_time,
                            adjusted_intensity + bpm_heat_boost,
                        )
                    else:
                        color = self.get_heatmap_color(
                            adjusted_intensity + bpm_heat_boost
                        )

                    self.particle_trails.append(
                        {"pos": pos, "life": 1.0, "color": color}
                    )

        # DIBUJADO DE PARTÍCULAS
        self.particle_trails = [p for p in self.particle_trails if p["life"] > 0]

        for particle in self.particle_trails:
            particle["life"] -= 0.05
            alpha = int(255 * particle["life"])

            if alpha > 10:
                radius = int(3 * particle["life"])
                draw_circle_alpha(
                    surface, (*particle["color"], alpha), particle["pos"], radius
                )

        # DIBUJADO DEL WIREFRAME
        draw_line = pygame.draw.line
        width_limit, height_limit = self.w + 100, self.h + 100

        for start_idx, end_idx in self.ed:
            point1 = projected_points[start_idx]
            point2 = projected_points[end_idx]

            if not (-100 < point1[0] < width_limit and -100 < point1[1] < height_limit):
                continue

            avg_z = (depths[start_idx] + depths[end_idx]) * 0.5
            norm_z = 1.0 - ((avg_z - min_z) / z_range)

            heat_val = min(
                1.0, (norm_z * 0.4) + (adjusted_intensity * 0.8) + bpm_heat_boost
            )

            if use_plasma:
                v3_start, v3_end = vertex_3d[start_idx], vertex_3d[end_idx]
                mid_x = (v3_start[0] + v3_end[0]) * 0.5
                mid_y = (v3_start[1] + v3_end[1]) * 0.5
                mid_z = (v3_start[2] + v3_end[2]) * 0.5
                color = self.get_plasma_color(
                    mid_x,
                    mid_y,
                    mid_z,
                    self.plasma_time,
                    adjusted_intensity + bpm_heat_boost,
                )
            else:
                color = self.get_heatmap_color(heat_val)

            thickness = 1
            if heat_val > 0.6:
                thickness = 2
            if heat_val > 0.8:
                thickness = 3
            if adjusted_intensity > 0.9:
                thickness = 4

            draw_line(surface, color, point1, point2, thickness)

            if heat_val > 0.85 or (bpm_enabled and bpm_strong):
                draw_line(surface, (255, 255, 255), point1, point2, 1)

        # EFECTO ESPECIAL: GHOSTING
        special_effect = adjusted_intensity > 0.9 or (bpm_enabled and bpm_strong)

        if special_effect:
            self.ghost_surf.fill((0, 0, 0, 0))
            offset = adjusted_intensity * 8 + (4 if bpm_strong else 0)
            ghost_color = (100, 255, 100, 120) if bpm_strong else (255, 100, 100, 80)

            for i in range(0, len(self.ed), 3):
                start_idx, end_idx = self.ed[i]
                p1 = projected_points[start_idx]
                p2 = projected_points[end_idx]

                offset_x = random.uniform(-offset, offset)
                offset_y = random.uniform(-offset, offset)

                ghost_p1 = (p1[0] + offset_x, p1[1] + offset_y)
                ghost_p2 = (p2[0] + offset_x, p2[1] + offset_y)

                pygame.draw.line(self.ghost_surf, ghost_color, ghost_p1, ghost_p2, 1)

            surface.blit(self.ghost_surf, (0, 0))


# ============================================================================
# CLASE SPECTRUMANALYZER: Analizador de espectro visual sincronizado con audio
# ============================================================================


class SpectrumAnalyzer:
    """
    Simulador de analizador de espectro visual ULTRA REACTIVO
    Genera barras, partículas y efectos basados en intensidad de audio
    Diferentes efectos para cada formato de música
    CON SINCRONIZACIÓN BPM COMPLETA PARA TODOS LOS FORMATOS
    """

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.bars = 64  # Número de barras del espectro
        self.bar_width = max(1, width // self.bars)

        # Calcular margen horizontal para centrado
        self.horizontal_margin = (self.w - (self.bars * self.bar_width)) // 2

        # Buffers de datos para el espectro
        if NUMPY_AVAILABLE:
            self.values = np.zeros(self.bars)
            self.peaks = np.zeros(self.bars)
            self.peak_hold = np.zeros(self.bars)
            self.x_axis = np.linspace(0, 10, self.bars)
        else:
            self.values = [0.0] * self.bars
            self.peaks = [0.0] * self.bars
            self.peak_hold = [0.0] * self.bars
            self.x_axis = []

        self.offset = 0.0

        # Sistemas de partículas MEJORADOS
        self.sparks = []  # Chispas para efecto MP3
        self.particles_ogg = []  # Partículas para efecto OGG
        self.particles_3d = []  # Partículas 3D para efecto IT
        self.particles_xm = []  # Partículas para efecto XM (NUEVO)

        # Variables de tiempo y BPM
        self.last_update = time.time()
        self.rotation_angle = 0.0
        self.bpm_pulse = 0.0  # Pulso de beat (0.0-1.0)
        self.bpm_phase = 0.0  # Fase dentro del beat (0.0-1.0)
        self.current_bpm = 120.0  # BPM por defecto
        self.beat_counter = 0  # Contador de beats
        self.measure_counter = 0  # Contador de compases (cada 4 beats)

        # EFECTO MAGMA (para MP3)
        self.magma_height = 400
        self.magma_texture = self._generate_magma_texture(width, self.magma_height)

        # Textura duplicada para scrolling infinito
        self.magma_long = pygame.Surface((width, self.magma_height * 2))
        self.magma_long.blit(self.magma_texture, (0, 0))
        self.magma_long.blit(self.magma_texture, (0, self.magma_height))

        self.magma_y_scroll = 0

        # Superficies de trabajo reutilizables
        self.work_surf = pygame.Surface((self.w, 350), pygame.SRCALPHA)
        self.mask_surf = pygame.Surface((self.w, 350), pygame.SRCALPHA)

        # Sprite de burbuja para efecto MP3
        self.bubble_size = 64
        self.bubble_surf = pygame.Surface(
            (self.bubble_size, self.bubble_size), pygame.SRCALPHA
        )
        self._generate_bubble_sprite()

        # Variables de efectos BPM
        self.last_beat_time = time.time()
        self.beat_history = []  # Historial de beats para cálculo de BPM
        self.auto_bpm_detected = 120.0

    def _get_safe_color(self, index, value, bpm_pulse=0.0):
        """Versión segura de _get_frequency_color que nunca falla y devuelve tuple(int,int,int,int)"""
        try:
            col = self._get_frequency_color(index, value, bpm_pulse)

            # Si devuelve None o algo inválido, fallback
            if col is None or not (isinstance(col, (tuple, list))):
                return (255, 255, 255, 200)

            # Asegurar longitud mínima
            if len(col) < 3:
                return (255, 255, 255, 200)

            # Forzar conversión a int nativo de Python y clamping estricto 0-255
            # Esto elimina numpy.int64 o floats que rompen pygame.draw
            r = int(col[0])
            g = int(col[1])
            b = int(col[2])
            a = int(col[3]) if len(col) > 3 else 255

            return (
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b)),
                max(0, min(255, a)),
            )
        except:
            return (255, 255, 255, 200)

    def _generate_magma_texture(self, width, height):
        """Genera textura de efecto magma (gradiente de calor)"""
        surface = pygame.Surface((width, height))

        for y in range(0, height, 2):
            for x in range(0, width, 4):
                v1 = SIN(x * 0.02)
                v2 = SIN(y * 0.03)
                v3 = SIN((x + y) * 0.015)
                value = (v1 + v2 + v3 + 3) / 6

                if value < 0.2:
                    color = (int(120 + value * 100), 0, 0)
                elif value < 0.5:
                    color = (255, int(100 * (value - 0.2) * 3.3), 0)
                elif value < 0.8:
                    color = (
                        255,
                        int(100 + 155 * (value - 0.5) * 3.3),
                        0,
                    )
                else:
                    color = (
                        255,
                        255,
                        int(255 * (value - 0.8) * 5.0),
                    )

                pygame.draw.rect(surface, color, (x, y, 4, 2))

        return pygame.transform.smoothscale(surface, (width, height))

    def _generate_bubble_sprite(self):
        """Genera sprite de burbuja con gradiente radial"""
        center = self.bubble_size // 2

        for radius in range(center, 0, -2):
            alpha = int(255 * (1 - (radius / center)))
            color = (255, 220 - int(radius * 2), 100, clamp_val(alpha * 0.6))
            pygame.draw.circle(self.bubble_surf, color, (center, center), radius)

    def _get_frequency_color(self, index, value, bpm_pulse=0.0):
        """
        Obtiene color basado en frecuencia (posición) e intensidad
        """
        try:
            # Validar entradas para evitar errores
            index = max(0, min(self.bars - 1, int(index)))
            value = max(0.0, min(1.0, float(value)))
            bpm_pulse = max(0.0, min(1.0, float(bpm_pulse)))

            position = index / self.bars

            # Añadir pulso BPM al valor de color
            pulse_boost = bpm_pulse * 0.3

            # Gradiente de frecuencia: bajas=rojo, medias=verde, altas=azul
            if position < 0.3:  # Bajas frecuencias
                r = 255 + int(pulse_boost * 100)
                g = int(80 + position * 200 + pulse_boost * 80)
                b = int(50 * position + pulse_boost * 50)
            elif position < 0.7:  # Frecuencias medias
                r = int(255 * (0.7 - position) * 2.5 + pulse_boost * 50)
                g = 255 + int(pulse_boost * 100)
                b = int(100 * (position - 0.3) * 2.5 + pulse_boost * 50)
            else:  # Altas frecuencias
                r = int(100 * (1.0 - position) * 3.3 + pulse_boost * 30)
                g = int(200 * (1.0 - position) * 3.3 + pulse_boost * 50)
                b = 255 + int(pulse_boost * 100)

            # Alpha basado en intensidad y pulso BPM
            alpha = 180 + value * 75 + bpm_pulse * 50

            return (r, g, b, alpha)

        except Exception as e:
            return (255, 255, 255, 200)

    def _apply_bpm_sync(self, bpm_data=None, kick=0.0):
        """
        Aplica sincronización BPM a los parámetros de animación
        """
        current_time = time.time()

        if bpm_data:
            # Usar datos BPM proporcionados
            self.bpm_pulse = bpm_data.get("beat_pulse", 0.0)
            self.current_bpm = bpm_data.get("bpm", self.auto_bpm_detected)
            self.bpm_phase = bpm_data.get("beat_phase", 0.0)
            is_strong_beat = bpm_data.get("strong_beat", False)

            if is_strong_beat:
                self.beat_counter += 1
                if self.beat_counter % 4 == 0:
                    self.measure_counter += 1

        else:
            # Detección automática de BPM basada en kicks
            if kick > 0.7:
                now = time.time()
                self.beat_history.append(now)

                # Mantener solo los últimos 10 beats
                if len(self.beat_history) > 10:
                    self.beat_history.pop(0)

                # Calcular BPM si tenemos suficientes beats
                if len(self.beat_history) >= 4:
                    intervals = []
                    for i in range(1, len(self.beat_history)):
                        intervals.append(
                            self.beat_history[i] - self.beat_history[i - 1]
                        )

                    avg_interval = sum(intervals) / len(intervals)
                    if avg_interval > 0:
                        self.auto_bpm_detected = 60.0 / avg_interval

                self.current_bpm = self.auto_bpm_detected

            # Simular pulso BPM
            beat_duration = 60.0 / self.current_bpm
            time_since_last_beat = current_time - self.last_beat_time

            if time_since_last_beat > beat_duration:
                self.last_beat_time = current_time
                self.bpm_pulse = 1.0
                self.beat_counter += 1
            else:
                # Decaimiento exponencial del pulso
                decay_time = beat_duration * 0.3  # 30% del beat
                self.bpm_pulse = max(0.0, self.bpm_pulse - (1.0 / decay_time) * 0.016)

            # Calcular fase dentro del beat
            self.bpm_phase = (time_since_last_beat % beat_duration) / beat_duration

        # Actualizar rotación basada en BPM
        beats_per_rotation = 8  # Rotación completa cada 8 beats
        rotation_speed = (2 * PI) / (beats_per_rotation * (60.0 / self.current_bpm))
        self.rotation_angle += rotation_speed

        return {
            "bpm_pulse": self.bpm_pulse,
            "bpm": self.current_bpm,
            "phase": self.bpm_phase,
            "beat_counter": self.beat_counter,
            "measure_counter": self.measure_counter,
        }

    def draw(self, surface, intensity, kick, fmt, bpm_data=None):
        """
        Dibuja el analizador de espectro con efectos según formato
        TODOS LOS EFECTOS CON SINCRONIZACIÓN BPM MEJORADA
        """
        # Limpiar superficie de trabajo
        work_surface = self.work_surf
        work_surface.fill((0, 0, 0, 0))

        # ====================================================================
        # ACTUALIZACIÓN DE PARÁMETROS CON SINCRONIZACIÓN BPM
        # ====================================================================
        self.offset += 0.1
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time

        # Aplicar sincronización BPM
        bpm_info = self._apply_bpm_sync(bpm_data, kick)
        bpm_pulse = bpm_info["bpm_pulse"]
        bpm_phase = bpm_info["phase"]
        is_beat = bpm_pulse > 0.8
        is_measure_start = bpm_info["beat_counter"] % 4 == 0 and is_beat

        # Determinar física según formato
        is_tracker_physics = fmt in ["mod", "s3m", "xm", "it"]

        # ====================================================================
        # CÁLCULO DE DATOS DEL ESPECTRO (MEJORADO CON BPM)
        # ====================================================================
        if NUMPY_AVAILABLE:
            # 1. GENERAR OBJETIVOS (TARGETS) - A dónde quieren ir las barras
            target_values = np.zeros(self.bars)

            if is_tracker_physics:
                # Física Tracker: Saltos aleatorios
                n = int(intensity * self.bars * 0.7)
                if n > 0:
                    indices = np.random.choice(self.bars, n, replace=False)
                    base_value = 0.4 + kick * 0.6 + bpm_pulse * 0.3
                    target_values[indices] = np.random.rand(n) * base_value

                    if is_beat:
                        extra_indices = np.random.choice(
                            self.bars, int(n * 0.3), replace=False
                        )
                        target_values[extra_indices] = np.random.rand(
                            len(extra_indices)
                        ) * (0.5 + bpm_pulse * 0.5)
            else:
                # Física Audio: Ondas senoidales
                bpm_factor = self.current_bpm / 120.0
                wave_sine = (
                    np.sin(self.x_axis + self.offset * bpm_factor) * 0.5
                    + 0.5
                    + np.sin(self.x_axis * 0.5 - self.offset * 2 * bpm_factor) * 0.3
                )
                beat_peak = bpm_pulse * 0.9 * np.exp(-self.x_axis * 0.4)
                target_values = (
                    wave_sine * (0.3 + intensity * 0.6)
                    + kick * 0.9 * np.exp(-self.x_axis * 0.4)
                    + beat_peak
                )
                target_values += (
                    np.random.rand(self.bars)
                    * 0.12
                    * intensity
                    * (1 - np.exp(-self.x_axis * 0.15))
                )

            # 2. APLICAR GRAVEDAD A LAS BARRAS (values)
            # Si el target es mayor, sube de golpe. Si es menor, cae suave.
            BAR_GRAVITY = 0.040
            self.values = np.where(
                target_values > self.values, target_values, self.values - BAR_GRAVITY
            )
            self.values = np.clip(self.values, 0, 1)

            # 3. APLICAR GRAVEDAD A LOS PICOS (peaks) - ESTO ES LA CLAVE DE LA SUAVIDAD
            PEAK_GRAVITY = 0.015  # Caída lenta y elegante

            # Si la barra empuja al pico, el pico sube
            self.peaks = np.where(self.values > self.peaks, self.values, self.peaks)

            # Si no, el pico cae por gravedad constante
            self.peaks -= PEAK_GRAVITY

            # Limpiar negativos
            self.peaks = np.maximum(self.peaks, 0)

            # Referencias locales para el dibujado
            values = self.values
            peaks = self.peaks

        else:
            # Versión sin numpy con efectos BPM
            values = []
            peaks = []

            for i in range(self.bars):
                # Simular onda de audio con sincronización BPM
                bpm_factor = self.current_bpm / 120.0
                val = SIN(self.offset * 0.5 * bpm_factor + i * 0.05) * 0.5 + 0.5
                val += random.uniform(0, 0.15) * intensity

                # Añadir pulso BPM
                if bpm_phase < 0.2:  # En el golpe
                    val += bpm_pulse * 0.4 * np.exp(-i * 0.05)

                # Efecto tracker: silenciar aleatoriamente, menos en beats
                if is_tracker_physics and random.random() > (0.85 - bpm_pulse * 0.2):
                    val = 0

                values.append(min(1.0, val))

                # Actualizar picos
                if val > self.peaks[i]:
                    self.peaks[i] = val
                else:
                    decay_rate = 0.002 * (1.0 - bpm_pulse * 0.5)
                    self.peaks[i] = max(0, self.peaks[i] - decay_rate * delta_time * 60)

                peaks.append(self.peaks[i])

            self.peak_hold = values

        # ====================================================================
        # LIMPIEZA DE PARTÍCULAS
        # ====================================================================
        if fmt != "ogg":
            self.particles_ogg = [p for p in self.particles_ogg if p["life"] > 0]
        if fmt != "mp3":
            self.sparks = [spark for spark in self.sparks if spark["life"] > 0]
        if fmt != "it":
            self.particles_3d = [p for p in self.particles_3d if p["life"] > 0]
        if fmt != "xm":
            self.particles_xm = [p for p in self.particles_xm if p["life"] > 0]

        # ====================================================================
        # EFECTO 1: MAGMA (MP3) - LIMPIO Y LIQUIDO
        # ====================================================================
        if fmt == "mp3":
            points = []
            ghost_points = []
            prev_height = 0

            # Generar puntos (SIN RUIDO ALEATORIO SUCIO)
            for i in range(len(values)):
                raw_height = values[i]

                # Altura aumentada en beats (Reactividad)
                bpm_height_boost = 1.0 + bpm_pulse * 0.5
                base_height = int(raw_height * 200 * (1 + kick) * bpm_height_boost)

                # Suavizado entre puntos vecinos (filtro paso bajo espacial)
                height = (base_height + prev_height) / 2
                prev_height = height

                x_pos = self.horizontal_margin + i * self.bar_width

                # CORRECCIÓN 1: Quitamos 'noise_y'. Ahora la linea es pura.
                # Si quieres variación, usa una onda seno suave, no random.randint
                points.append((x_pos, 350 - height))

                # Línea fantasma (sombra flotante)
                ghost_points.append((x_pos + 5, 350 - height - 5))

            # CORRECCIÓN 2: Cierre del polígono exacto para evitar diagonales en los márgenes
            if points:
                first_x = points[0][0]
                last_x = points[-1][0]
                # Cerramos bajando recto desde el último punto y volviendo recto al primero
                poly_points = points + [(last_x, 350), (first_x, 350)]
            else:
                poly_points = []

            # Dibujar línea fantasma
            if len(ghost_points) > 1:
                ghost_alpha = 100 + int(bpm_pulse * 155)
                # Usamos blend para que se vea más integrada
                pygame.draw.lines(
                    work_surface, (150, 80, 0, ghost_alpha), False, ghost_points, 2
                )

            # Crear máscara para efecto de magma
            self.mask_surf.fill((0, 0, 0, 0))
            if len(poly_points) > 2:
                pygame.draw.polygon(self.mask_surf, (255, 255, 255), poly_points)

            # Scrolling de textura
            scroll_speed = 1 + int(kick * 5) + int(bpm_pulse * 3)
            self.magma_y_scroll = (self.magma_y_scroll + scroll_speed) % 400

            src_rect = pygame.Rect(0, 400 - self.magma_y_scroll, self.w, 350)
            magma_slice = self.magma_long.subsurface(src_rect)

            self.mask_surf.blit(
                magma_slice, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
            )
            work_surface.blit(self.mask_surf, (0, 0))

            # CORRECCIÓN 3: HE ELIMINADO EL BLOQUE DE "RECTÁNGULOS GLITCH"
            # Ese era el causante principal de los "artefactos extraños".
            # Si quieres mantenerlo pero más suave, descomenta esto y baja la probabilidad:
            """
            if bpm_pulse > 0.9 and random.random() < 0.2: # Solo muy raramente en beats fuertes
                 # ... código de glitch ...
            """

            # Línea principal (Borde superior del magma)
            if len(points) > 1:
                line_color = (255, 220, 150)  # Color lava caliente
                if is_beat:
                    line_color = (255, 255, 255)  # Blanco en el golpe

                # Grosor variable: más grueso en el beat
                line_width = 2 if not is_beat else 3
                pygame.draw.lines(work_surface, line_color, False, points, line_width)

            # Generar partículas/burbujas (Esto sí mola, lo dejamos)
            spark_chance = 0.05 + (intensity * 0.1) + (bpm_pulse * 0.15)
            if random.random() < spark_chance:
                num_sparks = 1 + int(bpm_pulse * 3)
                for _ in range(num_sparks):
                    # Nacer desde la altura del magma, no desde abajo del todo siempre
                    spawn_x_idx = random.randint(0, len(values) - 1)
                    spawn_x = self.horizontal_margin + spawn_x_idx * self.bar_width
                    # Altura aproximada en ese punto
                    spawn_y = 350 - (values[spawn_x_idx] * 200 * (1 + kick))

                    self.sparks.append(
                        {
                            "x": spawn_x + random.randint(-10, 10),
                            "y": min(
                                340, spawn_y + random.randint(0, 50)
                            ),  # Un poco por debajo de la superficie
                            "vx": random.uniform(-0.5 - bpm_pulse, 0.5 + bpm_pulse),
                            "vy": random.uniform(-1.0, -3.0 - bpm_pulse * 2),
                            "size": random.uniform(0.5, 1.0) * (1 + bpm_pulse),
                            "life": 1.0 + bpm_pulse * 0.5,
                        }
                    )

            # Actualizar y dibujar partículas (Burbujas de calor)
            for spark in self.sparks:
                spark["x"] += spark["vx"]
                spark["y"] += spark["vy"]
                spark["life"] -= 0.015

                if spark["life"] > 0:
                    pulse_factor = 0.8 + 0.2 * SIN(current_time * 10)
                    size = int(
                        self.bubble_size
                        * spark["size"]
                        * pulse_factor
                        * (spark["life"] ** 0.5)
                    )

                    if size > 0:
                        bubble = pygame.transform.scale(self.bubble_surf, (size, size))
                        alpha = int(255 * spark["life"])
                        bubble.set_alpha(alpha)
                        work_surface.blit(
                            bubble,
                            (int(spark["x"]) - size // 2, int(spark["y"]) - size // 2),
                            special_flags=pygame.BLEND_RGBA_ADD,
                        )

        # ====================================================================
        # EFECTO 2: TRACKER (MOD, S3M) - CON BPM (CORREGIDO)
        # ====================================================================
        # ====================================================================
        # BLOQUE 2: DIBUJADO TRACKER (SUSTITUIR TODO EL BLOQUE 'elif fmt in ["mod", "s3m"]:')
        # ====================================================================
        elif fmt in ["mod", "s3m"]:
            if NUMPY_AVAILABLE:
                heights = (values * 140).astype(int)
                peak_heights = (peaks * 140).astype(int)
            else:
                heights = [int(v * 140) for v in values]
                peak_heights = [int(p * 140) for p in peaks]

            for i in range(self.bars):
                # --- BARRA PRINCIPAL ---
                base_height = min(heights[i], 250)
                # La barra SÍ puede latir con el BPM (queda bien)
                height = int(base_height * (1.0 + bpm_pulse * 0.3))
                x_pos = self.horizontal_margin + i * self.bar_width

                if height > 0:
                    color = self._get_safe_color(i, values[i], bpm_pulse)

                    # Barra base
                    pygame.draw.rect(
                        work_surface,
                        color,
                        (x_pos + 1, 250 - height, self.bar_width - 2, height),
                    )

                    # Highlight (Brillo superior barra)
                    highlight_boost = 40 + int(bpm_pulse * 60)
                    highlight_color = (
                        min(255, color[0] + highlight_boost),
                        min(255, color[1] + highlight_boost),
                        min(255, color[2] + highlight_boost),
                        color[3],
                    )
                    highlight_height = 3 + int(bpm_pulse * 2)
                    pygame.draw.rect(
                        work_surface,
                        highlight_color,
                        (x_pos + 1, 250 - height, self.bar_width - 2, highlight_height),
                    )

                    # Efecto Scanline
                    if bpm_phase < 0.3:
                        scan_y = 250 - height + int(bpm_phase * 333 * height / 100)
                        pygame.draw.rect(
                            work_surface,
                            (255, 255, 255, 150),
                            (x_pos + 1, scan_y, self.bar_width - 2, 2),
                        )

                # --- PICO (RAYA BLANCA) ---
                if peak_heights[i] > 0:
                    # 1. POSICIÓN: Sólida como una roca (sin efectos de BPM)
                    peak_pixel_y = min(peak_heights[i], 250)

                    # 2. COLOR: Aquí es donde aplicamos el ritmo (Alpha)
                    # La raya no se mueve, pero brilla con el beat
                    peak_alpha = 180 + int(bpm_pulse * 75)

                    # Dibujamos justo encima
                    draw_y = 250 - peak_pixel_y - 2

                    pygame.draw.rect(
                        work_surface,
                        (255, 255, 255, peak_alpha),
                        (x_pos + 2, draw_y, self.bar_width - 4, 2),
                    )

            # Efecto especial en inicio de compás (Flash de fondo)
            if is_measure_start:
                flash_surf = pygame.Surface((self.bar_width * 4, 50), pygame.SRCALPHA)
                flash_surf.fill((255, 255, 255, 80))
                work_surface.blit(
                    flash_surf,
                    (self.horizontal_margin + self.bar_width * 15, 200),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )

            # Efecto especial en inicio de compás (Flash de fondo)
            if is_measure_start:
                flash_surf = pygame.Surface((self.bar_width * 4, 50), pygame.SRCALPHA)
                flash_surf.fill((255, 255, 255, 80))
                work_surface.blit(
                    flash_surf,
                    (self.horizontal_margin + self.bar_width * 15, 200),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )

            # Efecto especial en inicio de compás (Se mantiene igual)
            if is_measure_start:
                flash_surf = pygame.Surface((self.bar_width * 4, 50), pygame.SRCALPHA)
                flash_surf.fill((255, 255, 255, 80))
                work_surface.blit(
                    flash_surf,
                    (self.horizontal_margin + self.bar_width * 15, 200),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )

        # ====================================================================
        # EFECTO 3: OGG (formato OGG Vorbis - estilo simétrico) CON BPM
        # ====================================================================
        elif fmt == "ogg":
            center_x = self.w // 2
            limit = self.bars // 2
            width_step = (self.w // 2) / limit
            bar_width = max(1, int(self.bar_width * 0.4))

            for i in range(limit):
                # Altura con efecto BPM
                val_base = values[i] * (1.3 + kick * 1.5)
                bpm_boost = bpm_pulse * 0.3  # Boost en el beat
                val = val_base * (1.0 + bpm_boost)
                height = min(int(val * 180), 180)
                x_offset = i * width_step

                # Color basado en frecuencia con BPM - USANDO safe_color
                energy_color = self._get_safe_color(i, val, bpm_pulse)

                # Dibujar barra con gradiente vertical
                step = 4
                for y_offset in range(0, height, step):
                    y_pos = 250 - y_offset
                    if y_pos < 0:
                        break

                    progress = y_offset / max(1, height)
                    factor = 0.3 + 0.7 * progress

                    # Efecto de pulsación en beat
                    if is_beat:
                        pulse_factor = 1.0 + bpm_pulse * 0.2
                        factor *= pulse_factor

                    # Calcular color seguro
                    r = int(energy_color[0] * factor)
                    g = int(energy_color[1] * factor)
                    b = int(energy_color[2] * factor)

                    # Asegurar límites
                    r = max(0, min(255, r))
                    g = max(0, min(255, g))
                    b = max(0, min(255, b))

                    color = (
                        r,
                        g,
                        b,
                        200 + int(bpm_pulse * 55),  # Alpha pulsante
                    )

                    # Separación sutil en beat
                    bar_spacing = 0
                    if is_beat:
                        bar_spacing = random.uniform(-1, 1) * bpm_pulse * 2

                    pygame.draw.rect(
                        work_surface,
                        color,
                        (
                            center_x - x_offset - bar_width // 2 + bar_spacing,
                            y_pos,
                            bar_width,
                            step,
                        ),
                    )
                    pygame.draw.rect(
                        work_surface,
                        color,
                        (
                            center_x + x_offset - bar_width // 2 - bar_spacing,
                            y_pos,
                            bar_width,
                            step,
                        ),
                    )

                # Generar partículas en picos altos (más en beats)
                particle_chance = val * 0.8 + bpm_pulse * 0.2
                if val > 0.3 and random.random() < particle_chance:
                    spark_y = 250 - height
                    if spark_y >= 0:
                        speed = random.uniform(1.5, 5.0) * (0.5 + val + bpm_pulse * 0.5)
                        particle_color = (
                            random.randint(150, 255),
                            random.randint(50, 200),
                            int(bpm_pulse * 100),  # Azul en beat
                        )

                        self.particles_ogg.append(
                            {
                                "x": center_x - x_offset,
                                "y": spark_y,
                                "vx": COS(2.5) * speed,
                                "vy": SIN(2.5) * speed,
                                "life": 1.5 + bpm_pulse * 0.5,  # Más vida en beat
                                "max_life": 1.5 + bpm_pulse * 0.5,
                                "color": particle_color,
                                "size": random.uniform(2, 6),
                            }
                        )

                        self.particles_ogg.append(
                            {
                                "x": center_x + x_offset,
                                "y": spark_y,
                                "vx": COS(0.6) * speed,
                                "vy": SIN(0.6) * speed,
                                "life": 1.5 + bpm_pulse * 0.5,
                                "max_life": 1.5 + bpm_pulse * 0.5,
                                "color": particle_color,
                                "size": random.uniform(2, 6),
                            }
                        )

            # Actualizar y dibujar partículas OGG
            self.particles_ogg = [p for p in self.particles_ogg if p["life"] > 0]

            for particle in self.particles_ogg:
                particle["x"] += particle["vx"]
                particle["y"] += particle["vy"]
                particle["life"] -= 0.02

                if 0 <= particle["y"] <= 350:
                    alpha = int(255 * (particle["life"] / particle["max_life"]))

                    # Partículas más brillantes en beat
                    if is_beat:
                        alpha = min(255, alpha + 50)

                    # Asegurar que el color de la partícula sea válido
                    p_color = particle["color"]
                    safe_p_color = (
                        max(0, min(255, p_color[0])),
                        max(0, min(255, p_color[1])),
                        max(0, min(255, p_color[2])),
                        max(0, min(255, alpha)),
                    )

                    radius = int(
                        particle["size"] * (particle["life"] / particle["max_life"])
                    )
                    pygame.draw.circle(
                        work_surface,
                        safe_p_color,
                        (int(particle["x"]), int(particle["y"])),
                        radius,
                    )

        # ====================================================================
        # EFECTO 4: XM - CON BPM (MEJORADO)
        # ====================================================================
        elif fmt == "xm":
            if NUMPY_AVAILABLE:
                heights = (values * 140).astype(int)
                peak_heights = (peaks * 140).astype(int)
            else:
                heights = [int(v * 140) for v in values]
                peak_heights = [int(p * 140) for p in peaks]

            for i in range(self.bars):
                base_height = min(heights[i], 250)
                # Altura con variación rítmica
                rhythm_variation = SIN(bpm_phase * 2 * PI + i * 0.2) * 0.1
                height = int(base_height * (1.0 + bpm_pulse * 0.4 + rhythm_variation))
                x_pos = self.horizontal_margin + i * self.bar_width

                if height > 0:
                    base_color = self._get_safe_color(i, values[i], bpm_pulse)

                    # Color que cambia con el compás
                    if self.measure_counter % 2 == 0:
                        # Compás par: tonos fríos
                        color = (
                            clamp_val(int(base_color[0] // 2)),
                            clamp_val(int(base_color[1])),
                            clamp_val(
                                int(min(255, base_color[2] + 50 + int(bpm_pulse * 50)))
                            ),
                            clamp_val(int(base_color[3])),
                        )
                    else:
                        # Compás impar: tonos cálidos
                        color = (
                            clamp_val(
                                int(min(255, base_color[0] + 30 + int(bpm_pulse * 30)))
                            ),
                            clamp_val(int(base_color[1] // 2)),
                            clamp_val(int(base_color[2])),
                            clamp_val(int(base_color[3])),
                        )

                    pygame.draw.rect(
                        work_surface,
                        color,
                        (x_pos + 1, 250 - height, self.bar_width - 2, height),
                    )

                    # Highlight que parpadea en el beat
                    highlight_alpha = 180 if not is_beat else 255
                    pygame.draw.rect(
                        work_surface,
                        (255, 255, 255, highlight_alpha),
                        (
                            x_pos + 1,
                            250 - height,
                            self.bar_width - 2,
                            max(1, int(3 * (0.5 + bpm_pulse * 0.5))),
                        ),
                    )

                    # Línea de pico con efecto de caída en beat
                    if peak_heights[i] > 0:
                        peak_height = min(peak_heights[i], 250)
                        peak_drop = int(bpm_pulse * 20)  # "Cae" en el beat
                        pygame.draw.rect(
                            work_surface,
                            (
                                200 - int(bpm_pulse * 50),
                                200 - int(bpm_pulse * 50),
                                255,
                                220,
                            ),
                            (
                                x_pos + 2,
                                250 - min(peak_height, 250) - peak_drop,
                                self.bar_width - 4,
                                1,
                            ),
                        )

                    # Reflejo/eco que se mueve con el BPM
                    reflection_height = int(height * 0.4)
                    reflection_offset = int(bpm_phase * 10)
                    pygame.draw.rect(
                        work_surface,
                        (*color[:3], 30),
                        (
                            x_pos + 1,
                            252 + reflection_offset,
                            self.bar_width - 2,
                            reflection_height,
                        ),
                    )

            # Partículas XM especiales
            if random.random() < 0.03 + (bpm_pulse * 0.1):
                for _ in range(int(1 + bpm_pulse * 3)):
                    self.particles_xm.append(
                        {
                            "x": random.randint(0, self.w),
                            "y": random.randint(100, 250),
                            "vx": random.uniform(-1, 1) * (1 + bpm_pulse),
                            "vy": random.uniform(-2, -0.5) * (1 + bpm_pulse),
                            "life": random.uniform(1, 2),
                            "color": (
                                random.randint(100, 200),
                                random.randint(100, 255),
                                random.randint(200, 255),
                            ),
                            "size": random.uniform(1, 3) * (1 + bpm_pulse),
                        }
                    )

            # Actualizar partículas XM
            for particle in self.particles_xm:
                particle["x"] += particle["vx"]
                particle["y"] += particle["vy"]
                particle["life"] -= 0.03

                if (
                    0 <= particle["x"] < self.w
                    and 0 <= particle["y"] < 350
                    and particle["life"] > 0
                ):
                    alpha = int(255 * particle["life"])
                    size = int(particle["size"] * particle["life"])
                    draw_circle_alpha(
                        work_surface,
                        (*particle["color"], alpha),
                        (int(particle["x"]), int(particle["y"])),
                        size,
                    )

        # ====================================================================
        # EFECTO 5: IT - NEON 3D (DESPLAZADO ABAJO PARA EVITAR UI)
        # ====================================================================
        elif fmt == "it":
            # POSICIÓN: BAJAMOS A LA ZONA INFERIOR
            center_x = self.w // 2

            # Antes era self.h * 0.45 (arriba). Ahora lo bajamos al 75%
            # Esto lo pone en el cuarto inferior de la pantalla.
            center_y = int(self.h * 0.75)

            # CONFIGURACIÓN
            FOV = 400.0
            CAMERA_Z = 500.0
            RADIUS = 300.0  # Tamaño generoso

            rotation = current_time * 0.4 + (kick * 0.1)

            draw_list = []

            for i in range(self.bars):
                val = values[i]
                if val < 0.01:
                    continue

                angle_step = (2 * PI) / self.bars
                bar_angle = i * angle_step + rotation

                x_world = RADIUS * math.cos(bar_angle)
                z_world = RADIUS * math.sin(bar_angle)
                z_depth = z_world + CAMERA_Z

                if z_depth < 50:
                    continue

                scale = FOV / z_depth
                screen_x = center_x + (x_world * scale)

                rot_visual_width = abs(math.cos(bar_angle + PI / 2))
                bar_w = max(3, int(32 * scale * rot_visual_width))

                height_pixels = val * 280.0 * scale * (1.0 + kick * 0.5)

                raw_color = self._get_safe_color(i, val, bpm_pulse)
                depth_alpha = max(0.3, min(1.0, 1.0 - (z_depth / 2000.0)))

                draw_list.append(
                    {
                        "z": z_depth,
                        "x": screen_x,
                        "y": center_y,
                        "w": bar_w,
                        "h": height_pixels,
                        "color": raw_color,
                        "alpha": depth_alpha,
                    }
                )

            draw_list.sort(key=lambda p: p["z"], reverse=True)

            # Capa de brillo aditivo
            glow_surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            glow_surface.fill((0, 0, 0, 0))

            for item in draw_list:
                rx = item["x"] - item["w"] / 2
                ry_horizon = item["y"]
                rw = item["w"]
                rh = item["h"]
                r, g, b = item["color"][:3]
                alpha_factor = item["alpha"]

                if rw > 1 and rh > 1:
                    # 1. REFLEJO (ESPEJO - HACIA ARRIBA)
                    # OJO: Si hay algo negro arriba, el reflejo se verá tapado.
                    # Pero la barra principal (hacia abajo) se verá perfecta.
                    mirror_alpha = int(80 * alpha_factor)
                    if mirror_alpha > 0:
                        pygame.draw.rect(
                            work_surface,
                            (r, g, b, mirror_alpha),
                            (rx, ry_horizon - rh, rw, rh),
                        )

                    # 2. BARRA PRINCIPAL (HACIA ABAJO)
                    body_alpha = int(255 * alpha_factor)
                    pygame.draw.rect(
                        work_surface, (r, g, b, body_alpha), (rx, ry_horizon, rw, rh)
                    )

                    # 3. LUCES GLOW (ADITIVO)
                    halo_alpha = int(80 * alpha_factor)
                    # Glow abajo
                    pygame.draw.rect(
                        glow_surface,
                        (r, g, b, halo_alpha),
                        (rx - 5, ry_horizon, rw + 10, rh),
                    )

                    # Núcleo brillante
                    core_w = max(1, rw // 2)
                    core_x = rx + (rw - core_w) // 2
                    core_alpha = int(150 * alpha_factor)
                    core_color = (
                        min(255, r + 100),
                        min(255, g + 100),
                        min(255, b + 100),
                        core_alpha,
                    )

                    pygame.draw.rect(
                        glow_surface, core_color, (core_x, ry_horizon, core_w, rh)
                    )

            # Fusión
            work_surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # --- FUSIÓN FINAL ---
            # Sumamos la luz de glow_surface a la pantalla principal
            surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)

            # --- Partículas 3D (CORREGIDO) ---
            # Flotando alrededor con movimiento y VIDA
            if bpm_pulse > 0.5 and random.random() < 0.2:
                self.particles_3d.append(
                    {
                        "x": center_x + random.uniform(-300, 300),
                        "y": center_y + random.uniform(-100, 100),
                        "z": random.uniform(200, 600),
                        "vx": random.uniform(-1, 1),  # Velocidad X
                        "vy": random.uniform(-1, 1),  # Velocidad Y
                        "vz": random.uniform(-5, -15),  # Velocidad Z (hacia la cámara)
                        "life": 1.0,  # <--- ESTO EVITA EL CRASH
                        "color": self._get_safe_color(random.randint(0, 63), 1.0, 1.0),
                    }
                )

            # --- Actualizar y dibujar las partículas 3D ---
            # (IMPORTANTE: Esto mueve las partículas y reduce su vida)
            for p in self.particles_3d:
                p["x"] += p.get("vx", 0)
                p["y"] += p.get("vy", 0)
                p["z"] += p.get("vz", -5)
                p["life"] -= 0.02  # Reducir vida para que desaparezcan

                if p["life"] > 0 and p["z"] > 10:
                    scale_p = FOV / p["z"]
                    sx = int(center_x + (p["x"] - center_x) * scale_p)
                    sy = int(center_y + (p["y"] - center_y) * scale_p)

                    if 0 <= sx < self.w and 0 <= sy < self.h:
                        alpha = int(255 * p["life"])
                        r, g, b = p["color"][:3]
                        # Dibujamos un círculo brillante
                        pygame.draw.circle(
                            surface,
                            (r, g, b, alpha),
                            (sx, sy),
                            max(1, int(2 * scale_p)),
                        )

            # Limpieza de partículas muertas
            self.particles_3d = [p for p in self.particles_3d if p.get("life", 0) > 0]

        # --- BLOQUE FINAL FUERA DE LOS IF/ELIF ---
        # Si NO es modo IT, necesitamos pegar la work_surface (la tira de 350px)
        # a la pantalla principal.
        if fmt != "it":
            # Pegamos la tira en la parte inferior de la pantalla
            surface.blit(self.work_surf, (0, self.h - 350))


# ============================================================================
# CLASE CRTBoot: Secuencia de arranque estilo CRT/monitor viejo
# ============================================================================


class CRTBoot:
    """
    Simula secuencia de arranque estilo CRT.
    OPTIMIZADA: Surface Caching + Flag de finalización de texto.
    CON PRECARGA: Sistema mejorado para precargar recursos durante la pausa.
    """

    def __init__(self, width, height, font_path=None):
        self.w, self.h = width, height

        # Estados mejorados
        self.pause_completed = False
        self.text_finished = False
        self.preload_completed = False
        self.preload_callback = None

        self.last_time = time.time()
        self.char_interval = 0.05
        self.timer = 0.0
        self.pause_duration = 1.5
        self.finish_timer = 0.0
        self.preload_start_time = 0.0

        self.lines = [
            "INITIATING CERVANTES PROTOCOL...",
            "MEM CHECK: 640K OK",
            "LOADING DRIVERS: [OK]",
            "SYSTEM: REVIVAL OS v1.0",
            "MODE: TRANSLATION DEPLOYMENT",
            "TARGET: SPANISH LOCALIZATION",
            "STATUS: ARMED AND READY_",
        ]
        self.current_line_idx = 0
        self.current_char_idx = 0
        self.cursor_blink_timer = 0.0
        self.show_cursor = True

        self.static_text_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        font_name = font_path if font_path else "Consolas"
        self.font = pygame.font.SysFont(font_name, 20, bold=True)
        self.color_text = (100, 255, 255)
        self.color_glow = (0, 100, 200)
        self.color_scanline = (0, 0, 0, 80)

        self.scanlines_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        self.generate_scanlines()

        self.typewriter_sound = None
        self.load_sound()
        self.start_y = self.h // 2 - (len(self.lines) * 25) // 2
        self.line_height = 25

    def set_preload_callback(self, callback):
        """
        Establece una función callback para ejecutar cuando el texto termine.
        """
        self.preload_callback = callback

    def load_sound(self):
        try:
            path = resource_path("typewriter.ogg")
            if os.path.exists(path):
                self.typewriter_sound = pygame.mixer.Sound(path)
                self.typewriter_sound.set_volume(0.2)
        except Exception:
            pass

    def generate_scanlines(self):
        for y in range(0, self.h, 2):
            pygame.draw.line(
                self.scanlines_surf, self.color_scanline, (0, y), (self.w, y)
            )

    def play_sound(self):
        if self.typewriter_sound:
            try:
                pygame.mixer.Channel(6).play(self.typewriter_sound)
            except:
                pass

    def cache_line(self, line_index):
        if line_index < len(self.lines):
            text = self.lines[line_index]
            y_pos = self.start_y + (line_index * self.line_height)
            glow = self.font.render(text, True, self.color_glow)
            self.static_text_surface.blit(glow, (51, y_pos + 1))
            txt = self.font.render(text, True, self.color_text)
            self.static_text_surface.blit(txt, (50, y_pos))

    def draw(self, surface):
        if self.pause_completed:
            return

        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        if dt > 0.1:
            dt = 0.1

        # 1. LÓGICA DE ESCRITURA DE TEXTO (ACELERADA)
        if self.current_line_idx < len(self.lines):
            self.timer += dt
            if self.timer >= self.char_interval:
                self.timer = 0
                chars_per_frame = 2
                self.current_char_idx += chars_per_frame

                if self.current_char_idx % 3 == 0:
                    self.play_sound()

                target_line = self.lines[self.current_line_idx]
                if self.current_char_idx > len(target_line):
                    self.cache_line(self.current_line_idx)
                    self.current_line_idx += 1
                    self.current_char_idx = 0
                    self.timer = 0

        # 2. TEXTO TERMINADO - INICIAR PRECARGA
        elif not self.text_finished:
            self.text_finished = True
            self.preload_start_time = now
            print("[CRTBoot] Texto terminado. Iniciando precarga...")

        # 3. EJECUTAR PRECARGA SI HAY CALLBACK
        elif self.text_finished and not self.preload_completed:
            if self.preload_callback and not self.preload_completed:
                print("[CRTBoot] Ejecutando callback de precarga...")
                self.preload_completed = self.preload_callback()
            elif self.preload_callback is None:
                print("[CRTBoot] No hay callback de precarga. Saltando...")
                self.preload_completed = True

        # 4. ESPERAR PAUSA DESPUÉS DE PRECARGA
        elif self.preload_completed:
            self.finish_timer += dt
            if self.finish_timer >= 0.3:
                self.pause_completed = True
                print("[CRTBoot] Secuencia de arranque completada.")

        # 5. CURSOR Y ANIMACIÓN
        self.cursor_blink_timer += dt
        if self.cursor_blink_timer > 0.4:
            self.cursor_blink_timer = 0
            self.show_cursor = not self.show_cursor

        # 6. DIBUJO
        surface.fill((5, 10, 15))
        surface.blit(self.static_text_surface, (0, 0))

        if self.current_line_idx < len(self.lines):
            current_text = self.lines[self.current_line_idx][: self.current_char_idx]
            if self.show_cursor:
                current_text += "█"
            y_pos = self.start_y + (self.current_line_idx * self.line_height)
            glow = self.font.render(current_text, True, self.color_glow)
            surface.blit(glow, (51, y_pos + 1))
            txt = self.font.render(current_text, True, self.color_text)
            surface.blit(txt, (50, y_pos))

        surface.blit(self.scanlines_surf, (0, 0))
        scan_h = int(time.time() * 200) % self.h
        pygame.draw.line(surface, (100, 255, 255, 40), (0, scan_h), (self.w, scan_h), 2)

    def reset(self):
        """Reinicia la secuencia de arranque"""
        self.pause_completed = False
        self.text_finished = False
        self.preload_completed = False
        self.current_line_idx = 0
        self.current_char_idx = 0
        self.timer = 0.0
        self.finish_timer = 0.0
        self.last_time = time.time()
        self.static_text_surface.fill((0, 0, 0, 0))


# ============================================================================
# CLASE RETROGRID
# ============================================================================


class RetroGrid:
    """
    Grid perspectiva 3D estilo retro con celdas que se iluminan al ritmo
    Efecto similar a Tron/retro futurismo
    """

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.horizon = height // 2 + 50  # Línea del horizonte

        # Paleta de colores neón para celdas
        self.palette = [
            (255, 0, 110),  # Rosa neón
            (0, 240, 255),  # Cian neón
            (180, 0, 255),  # Púrpura neón
            (220, 255, 0),  # Amarillo neón
        ]

        # Celdas actualmente iluminadas
        self.lit_cells = []
        self.rows = 24

        # Superficie persistente para optimización
        self.grid_surf = pygame.Surface((width, height // 2), pygame.SRCALPHA)

        # Cache de posiciones Y precalculadas
        self.y_cache = [int(10 + (row * 20) ** 1.1) for row in range(self.rows + 5)]

    def _get_projected_point(self, row, col, offset_y, surface_height):
        """
        Calcula la proyección 3D de un punto del grid
        """
        # Usar cache para posiciones Y base
        base_idx = min(row, len(self.y_cache) - 1)
        y_base = self.y_cache[base_idx]
        y_screen = y_base + offset_y

        # Limitar al fondo de la superficie
        if y_screen > surface_height:
            y_screen = surface_height

        # Ratio de profundidad (0=lejos, 1=cerca)
        ratio = y_screen / surface_height
        center_x = self.w // 2

        # Perspectiva simple: líneas convergen en el centro
        x_top = center_x + col * 20  # Arriba (lejos) - menos ancho
        x_bottom = center_x + col * 150  # Abajo (cerca) - más ancho

        # Interpolar según profundidad
        x_screen = x_top + (x_bottom - x_top) * ratio

        return (x_screen, y_screen)

    def draw(self, surface, time_val, kick=0.0):
        """
        Dibuja el grid con perspectiva 3D
        """
        surface_height = self.h // 2
        offset_y = (time_val * 100) % 40  # Desplazamiento animado

        # ====================================================================
        # SPAWN DE CELDAS ILUMINADAS EN GOLPES FUERTES
        # ====================================================================
        if kick > 0.5:
            num_spawns = int(kick * 16) + 2

            for _ in range(num_spawns):
                row = random.randint(0, self.rows - 2)
                col = random.randint(-12, 12)
                color = random.choice(self.palette)

                self.lit_cells.append(
                    [row, col, color, 1.0]
                )  # [fila, col, color, vida]

        # Eliminar celdas con poca vida
        self.lit_cells = [cell for cell in self.lit_cells if cell[3] > 0.05]

        # Limpiar superficie (reutilizable)
        self.grid_surf.fill((0, 0, 0, 0))
        center_x = self.w // 2

        # ====================================================================
        # DIBUJAR CELDAS ILUMINADAS
        # ====================================================================
        for i in range(len(self.lit_cells)):
            cell = self.lit_cells[i]
            row, col, color, life = cell

            # Reducir vida
            cell[3] -= 0.05

            # Calcular puntos del polígono (celda 3D)
            point1 = self._get_projected_point(row, col, offset_y, surface_height)
            point4 = self._get_projected_point(row + 1, col, offset_y, surface_height)

            # Saltar si está fuera de pantalla
            if point1[1] >= surface_height or point4[1] >= surface_height:
                continue

            point2 = self._get_projected_point(row, col + 1, offset_y, surface_height)
            point3 = self._get_projected_point(
                row + 1, col + 1, offset_y, surface_height
            )

            # Color con alpha según vida
            rgba_color = (*color, int(160 * life))

            # Dibujar celda rellena
            pygame.draw.polygon(
                self.grid_surf, rgba_color, [point1, point2, point3, point4]
            )

            # Borde blanco para celdas con mucha vida
            if life > 0.7:
                pygame.draw.polygon(
                    self.grid_surf,
                    (255, 255, 255, 120),
                    [point1, point2, point3, point4],
                    1,
                )

        # ====================================================================
        # DIBUJAR REJILLA BASE
        # ====================================================================
        grid_color = (0, 255, 200)

        # Líneas verticales (convergen en el centro)
        for i in range(-14, 15):
            pygame.draw.line(
                self.grid_surf,
                (*grid_color, 80),
                (center_x + i * 20, 0),
                (center_x + i * 150, surface_height),
                1,
            )

        # Líneas horizontales (perspectiva)
        for i in range(self.rows + 4):
            y_3d = self.y_cache[min(i, len(self.y_cache) - 1)] + offset_y

            if y_3d < surface_height:
                # Alpha según profundidad (más oscuro cuanto más lejos)
                line_alpha = int((y_3d / surface_height) * 200)

                if line_alpha > 10:
                    pygame.draw.line(
                        self.grid_surf,
                        (*grid_color, line_alpha),
                        (0, y_3d),
                        (self.w, y_3d),
                        1,
                    )

        # Cabecera superior (ocultar líneas que sobresalen)
        pygame.draw.rect(self.grid_surf, (10, 10, 18), (0, 0, self.w, 20))

        # Dibujar grid en posición final
        surface.blit(self.grid_surf, (0, self.horizon))


# ============================================================================
# CLASE PEACECODERAIN
# ============================================================================


class PeaceCodeRain:
    """
    Efecto de lluvia de código al estilo Matrix
    Optimizado con pre-renderizado de caracteres para rendimiento
    """

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.drops = []  # Lista de gotas/cadenas de código

        # Fuente estilo terminal
        self.font = pygame.font.SysFont("consolas", 14, bold=True)

        # Número de columnas basado en ancho de caracteres
        self.cols = width // 14

        # ====================================================================
        # CACHÉ DE CARACTERES PRE-RENDERIZADOS
        # ====================================================================
        self.char_cache = {}
        hex_chars = "0123456789ABCDEF"

        # Pre-renderizar cada carácter en dos colores:
        # - Normal: verde oscuro (cuerpo de la gota)
        # - Cabeza: verde claro brillante (primer carácter)
        for char in hex_chars:
            self.char_cache[char] = self.font.render(char, True, (0, 150, 50))
            self.char_cache[char + "_head"] = self.font.render(
                char, True, (200, 255, 200)
            )

        # ====================================================================
        # INICIALIZAR GOTAS
        # ====================================================================
        for i in range(self.cols):
            self.drops.append(
                {
                    "x": i * 14,  # Posición X fija por columna
                    "y": random.randint(-height, 0),  # Posición Y aleatoria
                    "speed": random.uniform(1, 3),  # Velocidad individual
                    "chars": [
                        random.choice(hex_chars) for _ in range(random.randint(5, 15))
                    ],  # Cadena
                    "alpha": random.randint(50, 200),  # Transparencia base
                }
            )

    def update_draw(self, surface):
        """
        Actualiza y dibuja todas las gotas en una sola pasada
        """
        height = self.h

        for drop in self.drops:
            # Mover gota hacia abajo
            drop["y"] += drop["speed"]

            # Reiniciar gota si sale completamente de pantalla
            if drop["y"] > height:
                drop["y"] = random.randint(-100, -20)
                drop["speed"] = random.uniform(1, 3)
                # NO regeneramos chars aquí para mantener variedad

            # ================================================================
            # DIBUJAR CADENA DE CARACTERES
            # ================================================================
            # Solo dibujar si alguna parte está en pantalla
            max_char_height = len(drop["chars"]) * 14
            if drop["y"] + max_char_height < 0:
                continue

            # Dibujar cada carácter de la cadena
            for i, char in enumerate(drop["chars"]):
                y_pos = drop["y"] - i * 14  # Caracteres apilados hacia arriba

                # Solo dibujar si está en el área visible
                if 0 < y_pos < height:
                    # Determinar si es el carácter cabeza (primero)
                    is_head = i == 0
                    cache_key = char + "_head" if is_head else char

                    # Obtener superficie pre-renderizada
                    char_surface = self.char_cache.get(cache_key)

                    if char_surface:
                        # Aplicar alpha decreciente hacia atrás en la cadena
                        if i > 5:
                            char_alpha = max(0, drop["alpha"] - i * 10)
                            char_surface.set_alpha(char_alpha)
                        else:
                            char_surface.set_alpha(drop["alpha"])

                        # Dibujar carácter
                        surface.blit(char_surface, (drop["x"], y_pos))


# ============================================================================
# CLASE PRAXISEVENT: Evento climático final (explosión + secuencia de paz)
# ============================================================================


class PraxisEvent:
    """
    Evento climático final con múltiples fases:
    1. Carga de energía
    2. Explosión/descarga
    3. Secuencia de paz con naves espaciales
    4. Mensajes finales
    """

    def __init__(self, width, height):
        self.w, self.h = width, height

        # Estado del evento
        self.active = False  # Evento activado
        self.wiped = False  # Pantalla limpiada (post-explosión)
        self.start_time = 0  # Tiempo de inicio
        self.phase = "IDLE"  # Fase actual
        self.blast_sound_played = False  # Control de sonido

        # Lluvia de código para fondo de secuencia de paz
        self.peace_rain = PeaceCodeRain(width, height)

        # ====================================================================
        # SUPERFICIES DE TRABAJO (optimización)
        # ====================================================================
        # Superficie baja resolución para efectos de explosión
        self.low_w, self.low_h = 80, 60
        self.low_surf = pygame.Surface((self.low_w, self.low_h))

        # Superficie para secuencia de paz/fallout
        self.fallout_surf = pygame.Surface((width, height))

        # Superficie para grid 3D de fondo
        self.grid_surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # ====================================================================
        # SISTEMAS DE EFECTOS
        # ====================================================================
        self.blobs = []  # Partículas de explosión
        self.squadron = []  # X-Wings (primer plano)
        self.lit_cells = []  # Celdas iluminadas en grid 3D

        # Paleta de colores cyberpunk
        self.cyber_palette = [
            (255, 0, 110),  # Rosa neón
            (0, 240, 255),  # Cian neón
            (180, 0, 255),  # Púrpura neón
            (220, 255, 0),  # Amarillo neón
        ]

        # ====================================================================
        # CONFIGURACIÓN DE SÍMBOLO DE PAZ
        # ====================================================================
        self.peace_center = (width // 2, height // 2)
        self.base_radius = 190
        self.collision_mask = self._generate_collision_mask()

        # ====================================================================
        # RUTAS DE X-WING (primer plano - maniobras complejas)
        # ====================================================================
        self.routes = [
            # Ruta 1: Entrada curva -> inmersión -> salida
            [
                {"x": -1000, "y": -500, "z": 1.0, "action": "FLY"},
                {"x": -500, "y": 0, "z": 8.0, "action": "CURVE_RIGHT"},
                {"x": 0, "y": 400, "z": 15.0, "action": "DIVE"},
                {"x": 600, "y": 200, "z": 25.0, "action": "BARREL_ROLL"},
                {"x": 1000, "y": -200, "z": 50.0, "action": "EXIT"},
            ],
            # Ruta 2: Zigzag agresivo
            [
                {"x": 400, "y": -800, "z": 1.0, "action": "FLY"},
                {"x": 200, "y": -300, "z": 10.0, "action": "ZIGZAG"},
                {"x": -200, "y": 0, "z": 18.0, "action": "ZIGZAG"},
                {"x": 200, "y": 300, "z": 25.0, "action": "ZIGZAG"},
                {"x": 0, "y": 600, "z": 60.0, "action": "EXIT"},
            ],
            # Ruta 3: Vuelo estático -> giro brusco
            [
                {"x": 0, "y": 0, "z": 0.5, "action": "FLY"},
                {"x": 0, "y": 0, "z": 5.0, "action": "FLY"},
                {"x": 300, "y": -200, "z": 12.0, "action": "HARD_TURN_RIGHT"},
                {"x": 600, "y": -400, "z": 30.0, "action": "BARREL_ROLL"},
            ],
            # Ruta 4: Loop vertical
            [
                {"x": -800, "y": 400, "z": 1.0, "action": "FLY"},
                {"x": -400, "y": 0, "z": 10.0, "action": "LOOP_START"},
                {"x": -400, "y": -400, "z": 20.0, "action": "LOOP_MID"},
                {"x": -800, "y": 0, "z": 35.0, "action": "EXIT"},
            ],
        ]

        # ====================================================================
        # RUTAS DE B-WING (fondo - destino: suelo)
        # ====================================================================
        self.bg_routes = [
            # Ruta 1: Diagonal hacia esquina inferior derecha
            [
                {"x": -200, "y": -200, "z": 2.0, "action": "FLY"},
                {"x": 0, "y": 0, "z": 30.0, "action": "FLY"},
                {"x": 800, "y": 600, "z": 150.0, "action": "DIVE"},
            ],
            # Ruta 2: Diagonal hacia esquina inferior izquierda
            [
                {"x": 200, "y": -200, "z": 2.0, "action": "FLY"},
                {"x": 0, "y": 0, "z": 30.0, "action": "FLY"},
                {"x": -800, "y": 600, "z": 150.0, "action": "DIVE"},
            ],
            # Ruta 3: Caída central directa
            [
                {"x": 0, "y": -300, "z": 2.0, "action": "FLY"},
                {"x": 0, "y": -100, "z": 30.0, "action": "ZIGZAG"},
                {"x": 0, "y": 800, "z": 250.0, "action": "DIVE"},
            ],
            # Ruta 4: Barrido rasante horizontal
            [
                {"x": -600, "y": 200, "z": 5.0, "action": "FLY"},
                {"x": 0, "y": 300, "z": 50.0, "action": "BARREL_ROLL"},
                {"x": 600, "y": 500, "z": 200.0, "action": "EXIT"},
            ],
        ]

        # ====================================================================
        # INICIALIZACIÓN DE NAVES
        # ====================================================================
        # Spawn inicial de X-Wings
        for _ in range(8):
            self.spawn_xwing(initial=True)

        # Y-Wings (fondo)
        self.ywings = []
        self.ywing_timer = 0

    def _generate_collision_mask(self):
        """
        Genera máscara de colisión para el símbolo de paz
        """
        temp_surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        center_x, center_y = self.peace_center
        radius = self.base_radius
        line_width = 40

        # Dibujar símbolo de paz (círculo + líneas)
        pygame.draw.circle(
            temp_surface, (255, 255, 255), (center_x, center_y), radius, line_width
        )
        pygame.draw.line(
            temp_surface,
            (255, 255, 255),
            (center_x, center_y - radius),
            (center_x, center_y + radius),
            line_width,
        )

        # Líneas diagonales (45°)
        diagonal_offset = int(radius * 0.707)  # cos(45°) = sin(45°) ≈ 0.707
        pygame.draw.line(
            temp_surface,
            (255, 255, 255),
            (center_x, center_y),
            (center_x - diagonal_offset, center_y + diagonal_offset),
            line_width,
        )
        pygame.draw.line(
            temp_surface,
            (255, 255, 255),
            (center_x, center_y),
            (center_x + diagonal_offset, center_y + diagonal_offset),
            line_width,
        )

        # Convertir a máscara de colisión
        return pygame.mask.from_surface(temp_surface)

    def spawn_xwing(self, initial=False):
        """Genera un nuevo X-Wing en una ruta aleatoria"""
        route = random.choice(self.routes)

        # Pequeñas variaciones aleatorias por nave
        offset_x = random.uniform(-50, 50)
        offset_y = random.uniform(-50, 50)
        start_point = route[0]

        self.squadron.append(
            {
                "x": start_point["x"] + offset_x,
                "y": start_point["y"] + offset_y,
                "z": random.uniform(1.0, 10.0) if initial else 0.5,
                "vx": 0,
                "vy": 0,  # Velocidad
                "vz": random.uniform(0.2, 0.35),  # Velocidad Z
                "route": route,
                "wp_idx": 1,  # Índice de waypoint actual
                "roll": 0.0,  # Rotación en Z
                "bank": 0.0,  # Inclinación lateral
                "trail": [],  # Estela de partículas
                "offset_x": offset_x,
                "offset_y": offset_y,
                "evading": False,  # Evadiendo colisión
            }
        )

    def spawn_ywing_squad(self):
        """Genera un escuadrón de Y-Wings en formación"""
        route = random.choice(self.bg_routes)
        start_point = route[0]
        squad_offset_x = random.uniform(-100, 100)

        # Formación en V invertida
        formation = [
            (0, 0),  # Líder
            (25, -5),  # Ala derecha trasera
            (-25, -5),  # Ala izquierda trasera
            (50, -10),  # Extremo derecho
            (-50, -10),  # Extremo izquierdo
        ]

        # Crear cada nave del escuadrón
        for dx, dy in formation:
            self.ywings.append(
                {
                    "x": start_point["x"] + squad_offset_x + dx,
                    "y": start_point["y"] + dy,
                    "z": start_point["z"],
                    "vx": 0,
                    "vy": 0,
                    "vz": 0,
                    "roll": 0.0,
                    "bank": 0.0,
                    "route": route,
                    "wp_idx": 1,
                    "squad_dx": dx,  # Offset dentro de formación
                    "squad_dy": dy,
                    "offset_x": squad_offset_x,
                    "type": "YWING",
                    "side": 1,
                    "trail_l": [],  # Estela motor izquierdo
                    "trail_r": [],  # Estela motor derecho
                }
            )

    def trigger(self):
        """Activa el evento Praxis (inicia la secuencia)"""
        if not self.active:
            self.active = True
            self.start_time = time.time()
            self.phase = "CHARGE"
            self.blast_sound_played = False

    def play_blast_sound(self):
        """Intenta reproducir sonido de explosión desde diferentes formatos"""
        played = False

        # Intentar diferentes formatos de archivo
        for sound_file in ["blast.ogg", "blast.mp3", "blast.wav"]:
            path = resource_path(sound_file)

            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    pygame.mixer.Channel(5).play(sound)
                    played = True
                    break
                except Exception:
                    continue

        # Fallback: generar voz robótica si no hay archivo
        if not played:
            try:
                # Intento seguro de usar AudioManager, solo si está disponible en scope global
                # (Usualmente se inyecta o se importa si existe el módulo)
                from audio import AudioManager

                robotic_voice = AudioManager.generate_voice("", "temp_blast.wav")
                AudioManager.play_robotic(robotic_voice, base_channel=5)
            except ImportError:
                print("AudioManager no disponible para voz robótica de fallback.")
            except Exception as e:
                print(f"Error al generar sonido fallback: {e}")

    def get_shake(self):
        """Calcula el efecto de sacudida de pantalla según la fase"""
        if not self.active or self.phase == "FALLOUT":
            return (0, 0)

        elapsed = time.time() - self.start_time

        if self.phase == "CHARGE":
            # Sacudida creciente durante carga
            shake_intensity = elapsed * 4
            return (
                random.uniform(-shake_intensity, shake_intensity),
                random.uniform(-shake_intensity, shake_intensity),
            )

        elif self.phase == "BLAST":
            # Sacudida fuerte que decae
            if elapsed - 2.0 < 0.2:  # Pico inicial
                force = 50
            elif elapsed - 2.0 < 4.0:  # Decaimiento
                force = 25 * (1 - ((elapsed - 2.0) / 4.0))
            else:  # Fin
                force = 1

            return (random.uniform(-force, force), random.uniform(-force, force))

        return (0, 0)

    def draw_peace_sign(self, surface, center, radius, color, width):
        """Dibuja el símbolo de paz (círculo + líneas)"""
        center_x, center_y = center

        # Círculo exterior
        pygame.draw.circle(surface, color, (center_x, center_y), radius, width)

        # Línea vertical central
        pygame.draw.line(
            surface,
            color,
            (center_x, center_y - radius),
            (center_x, center_y + radius),
            width,
        )

        # Líneas diagonales (45°)
        diagonal_offset = int(radius * 0.707)  # cos(45°) = sin(45°) ≈ 0.707
        pygame.draw.line(
            surface,
            color,
            (center_x, center_y),
            (center_x - diagonal_offset, center_y + diagonal_offset),
            width,
        )
        pygame.draw.line(
            surface,
            color,
            (center_x, center_y),
            (center_x + diagonal_offset, center_y + diagonal_offset),
            width,
        )

    def draw_xwing_3d(self, surface, ship, center_x, center_y):
        """Dibuja un X-Wing en perspectiva 3D"""
        # ====================================================================
        # TRANSFORMACIÓN 3D
        # ====================================================================
        z = max(0.1, ship["z"])

        # Posición en pantalla
        screen_x = center_x + ship["x"] * (1.0 / z)
        screen_y = center_y + ship["y"] * (1.0 / z)

        # Tamaño según distancia
        size = 80 * (1.0 / z)
        if size < 2:
            return  # Demasiado pequeño

        # ====================================================================
        # ROTACIÓN/INCLINACIÓN
        # ====================================================================
        # Inclinación lateral basada en movimiento horizontal
        target_bank = -ship["vx"] * 0.1
        ship["bank"] += (target_bank - ship["bank"]) * 0.1  # Suavizado

        # Rotación total (inclinación + roll)
        total_rotation = ship["bank"] + ship["roll"]
        cos_rot, sin_rot = math.cos(total_rotation), math.sin(total_rotation)

        # Función para rotar puntos locales
        def rotate_point(px, py):
            return (
                screen_x + px * cos_rot - py * sin_rot,
                screen_y + px * sin_rot + py * cos_rot,
            )

        # ====================================================================
        # GEOMETRÍA DEL X-WING
        # ====================================================================
        # Alas (forma de X)
        wing_span = size * 0.8
        wing_height = size * 0.25

        # Puntos de las alas
        wing_left_top = rotate_point(-wing_span, -wing_height)
        wing_right_bottom = rotate_point(wing_span, wing_height)
        wing_left_bottom = rotate_point(-wing_span, wing_height)
        wing_right_top = rotate_point(wing_span, -wing_height)

        # Dibujar alas (líneas cruzadas)
        pygame.draw.line(
            surface,
            (200, 200, 220),
            wing_left_top,
            wing_right_bottom,
            max(1, int(size * 0.08)),
        )
        pygame.draw.line(
            surface,
            (200, 200, 220),
            wing_left_bottom,
            wing_right_top,
            max(1, int(size * 0.08)),
        )

        # Motores (círculos en extremos de alas)
        engine_size = int(size * 0.1)
        if engine_size > 0:
            for point in [
                wing_left_top,
                wing_right_bottom,
                wing_left_bottom,
                wing_right_top,
            ]:
                pygame.draw.circle(
                    surface, (255, 100, 50), (int(point[0]), int(point[1])), engine_size
                )

        # Fuselaje (línea central)
        fuselage_top = rotate_point(0, -size * 0.5)
        fuselage_bottom = rotate_point(0, size * 0.4)
        pygame.draw.line(
            surface,
            (230, 230, 250),
            fuselage_top,
            fuselage_bottom,
            max(2, int(size * 0.15)),
        )

    def draw_ywing_3d(self, surface, ship, center_x, center_y):
        """Dibuja un Y-Wing en perspectiva 3D (fondo)"""
        z = max(0.1, ship["z"])
        if z > 300:  # Demasiado lejos
            return

        # ====================================================================
        # TRANSFORMACIÓN 3D (escala aumentada para fondo)
        # ====================================================================
        scale = 500.0 / z
        screen_x = center_x + ship["x"] * scale
        screen_y = center_y + ship["y"] * scale

        # Tamaño proporcional a escala (CORRECCIÓN: antes era muy pequeño)
        size = scale * 6.0
        if size < 2:
            return

        # ====================================================================
        # ROTACIÓN/INCLINACIÓN
        # ====================================================================
        target_bank = -ship["vx"] * 0.02
        ship["bank"] += (target_bank - ship["bank"]) * 0.1

        total_rotation = ship["bank"] + ship["roll"]
        cos_rot, sin_rot = math.cos(total_rotation), math.sin(total_rotation)

        def rotate_point(px, py):
            return (
                screen_x + px * cos_rot - py * sin_rot,
                screen_y + px * sin_rot + py * cos_rot,
            )

        # ====================================================================
        # GEOMETRÍA DEL Y-WING
        # ====================================================================
        # Cabina (triángulo frontal)
        pygame.draw.polygon(
            surface,
            (220, 210, 100),
            [
                rotate_point(0, -size * 0.3),  # Punto superior
                rotate_point(-size * 0.1, size * 0.1),  # Esquina inferior izquierda
                rotate_point(size * 0.1, size * 0.1),  # Esquina inferior derecha
            ],
        )

        # Ala central
        pygame.draw.line(
            surface,
            (180, 180, 190),
            rotate_point(-size * 0.4, size * 0.1),
            rotate_point(size * 0.4, size * 0.1),
            max(1, int(size * 0.08)),
        )

        # Brazos laterales (con motores)
        for side_x in [-size * 0.4, size * 0.4]:
            pygame.draw.line(
                surface,
                (180, 180, 190),
                rotate_point(side_x, size * 0.05),
                rotate_point(side_x, size * 0.8),
                max(2, int(size * 0.12)),
            )

            # Motor (círculo en extremo)
            engine_pos = rotate_point(side_x, size * 0.85)
            pygame.draw.circle(
                surface,
                (255, 50, 100),
                (int(engine_pos[0]), int(engine_pos[1])),
                max(2, int(size * 0.15)),
            )

    def render_rainbow_text(
        self, surface, text, center_x, center_y, time_offset, filename=None
    ):
        """Renderiza texto con efecto arcoíris o imagen PNG"""
        # Determinar archivo PNG basado en texto
        if filename is None:
            if "THIS WAR IS OVER" in text:
                filename = "final1.png"
            elif "ENJOY THE MOMENT" in text:
                filename = "final2.png"
            else:
                filename = "final1.png"  # Fallback

        try:
            # Intentar cargar imagen PNG
            png_path = resource_path(filename)

            if os.path.exists(png_path):
                image = pygame.image.load(png_path).convert_alpha()

                # Escalar si es demasiado grande
                img_width, img_height = image.get_size()
                max_width = self.w - 40  # 20px margen a cada lado

                if img_width > max_width:
                    scale_factor = max_width / img_width
                    new_width = max_width
                    new_height = int(img_height * scale_factor)
                    image = pygame.transform.scale(image, (new_width, new_height))

                # Centrar y dibujar imagen
                img_rect = image.get_rect(center=(center_x, center_y))
                surface.blit(image, img_rect)

            else:
                # Fallback a texto arcoíris
                self._draw_fallback_text(surface, text, center_x, center_y, time_offset)

        except Exception as e:
            # Fallback en caso de error
            self._draw_fallback_text(surface, text, center_x, center_y, time_offset)

    def _draw_fallback_text(self, surface, text, center_x, center_y, time_offset):
        """Dibuja texto con efecto arcoíris animado (fallback cuando no hay PNG)"""
        font = pygame.font.SysFont("courier new", 40, bold=True)
        total_width, _ = font.size(text)
        start_x = center_x - total_width // 2

        # Dibujar cada carácter con color diferente
        for i, char in enumerate(text):
            # Calcular hue basado en posición y tiempo
            hue = (time_offset * 3 + i * 0.3) % 6.28  # 2π radianes

            # Color RGB basado en senos desfasados
            red = int(127 + 127 * math.sin(hue))
            green = int(127 + 127 * math.sin(hue + 2))
            blue = int(127 + 127 * math.sin(hue + 4))

            char_surface = font.render(char, True, (red, green, blue))
            surface.blit(char_surface, (start_x, center_y))
            start_x += char_surface.get_width()

    def draw_fallout_screen(self, surface, current_time):
        """Dibuja la pantalla de secuencia de paz (post-explosión)"""
        center_x, center_y = self.w // 2, self.h // 2

        # ====================================================================
        # FONDO Y EFECTOS BASE
        # ====================================================================
        surface.fill((10, 15, 25))  # Azul oscuro espacial

        # Lluvia de código de fondo
        self.peace_rain.update_draw(surface)

        # ====================================================================
        # SÍMBOLO DE PAZ ANIMADO
        # ====================================================================
        pulse = (math.sin(current_time * 2) + 1) / 2  # 0-1 oscilante
        radius = int(180 + pulse * 10)

        # Símbolo de paz doble (borde exterior + interior)
        self.draw_peace_sign(
            surface, (center_x, center_y), radius, (0, 100, 50), 25
        )  # Borde grueso exterior
        self.draw_peace_sign(
            surface, (center_x, center_y), radius, (50, 255, 100), 8
        )  # Borde fino interior

        # ====================================================================
        # GRID 3D DE FONDO (perspectiva de fuga)
        # ====================================================================
        horizon_y = center_y + 50
        camera_height = 600.0
        spacing_z = 2.0  # Espaciado en profundidad
        spacing_x = 2.0  # Espaciado horizontal
        speed_z = 8.0  # Velocidad de scroll
        z_shift = (current_time * speed_z) % spacing_z  # Desplazamiento animado

        def get_screen_pos(x_index, z_depth):
            """Convierte coordenadas 3D a 2D con perspectiva"""
            if z_depth < 0.1:
                z_depth = 0.1

            scale = camera_height / z_depth
            world_x = x_index * spacing_x

            return (center_x + world_x * scale, horizon_y + scale)

        # Limpiar superficie de grid
        self.grid_surf.fill((0, 0, 0, 0))

        # ====================================================================
        # CELDAS ILUMINADAS (activadas por naves)
        # ====================================================================
        # Crear nuevas celdas iluminadas aleatoriamente
        if (math.sin(current_time * 10) + 1) / 2 > 0.9 and random.random() < 0.5:
            lane = random.choice([-1, 0])  # Carril izquierdo o central
            self.lit_cells.append(
                [
                    random.randint(5, 40),  # Profundidad
                    lane,  # Carril
                    random.choice(self.cyber_palette),  # Color
                    1.0,  # Vida inicial
                ]
            )

        # Actualizar y filtrar celdas
        self.lit_cells = [cell for cell in self.lit_cells if cell[3] > 0]
        for cell in self.lit_cells:
            cell[3] -= 0.04  # Decaimiento de vida

        # Dibujar celdas iluminadas
        for z_index, x_index, color, life in self.lit_cells:
            z_near = (z_index * spacing_z) + (spacing_z - z_shift)
            z_far = ((z_index + 1) * spacing_z) + (spacing_z - z_shift)

            if z_near > 0.2:
                # Calcular 4 puntos del polígono (celda 3D)
                p1 = get_screen_pos(x_index, z_near)
                p2 = get_screen_pos(x_index + 1, z_near)
                p3 = get_screen_pos(x_index + 1, z_far)
                p4 = get_screen_pos(x_index, z_far)

                # Dibujar si está en pantalla
                if p1[1] < self.h and p3[1] > horizon_y:
                    pygame.draw.polygon(
                        self.grid_surf, (*color, int(180 * life)), [p1, p2, p3, p4]
                    )

                    # Borde blanco para celdas con mucha vida
                    if life > 0.6:
                        pygame.draw.polygon(
                            self.grid_surf,
                            (255, 255, 255, int(100 * life)),
                            [p1, p2, p3, p4],
                            1,
                        )

        # ====================================================================
        # LÍNEAS HORIZONTALES DEL GRID (perspectiva)
        # ====================================================================
        for i in range(50):  # 50 líneas de profundidad
            z_depth = (i * spacing_z) + (spacing_z - z_shift)

            if z_depth > 0.2:
                p_left = get_screen_pos(-15, z_depth)
                p_right = get_screen_pos(15, z_depth)

                if p_left[1] < self.h and p_left[1] > horizon_y:
                    # Alpha decreciente con profundidad
                    alpha = max(0, min(255, int(255 * (20.0 / (z_depth + 5.0)))))

                    if alpha > 5:
                        pygame.draw.line(
                            self.grid_surf,
                            (0, 200, 100, alpha),
                            (0, p_left[1]),
                            (self.w, p_right[1]),
                            1,
                        )

        # ====================================================================
        # LÍNEAS VERTICALES DEL GRID
        # ====================================================================
        for x_index in range(-15, 16):
            if x_index != 0:  # Omitir línea central
                pygame.draw.line(
                    self.grid_surf,
                    (0, 150, 80, 40),
                    get_screen_pos(x_index, 100.0),  # Lejos
                    get_screen_pos(x_index, 0.2),  # Cerca
                    1,
                )

        # Aplicar grid a la superficie principal
        surface.blit(self.grid_surf, (0, 0))

        # ====================================================================
        # LÓGICA DE Y-WINGS (fondo)
        # ====================================================================
        self.ywing_timer += 1

        # Generar nuevo escuadrón periódicamente
        if self.ywing_timer > 90:
            self.spawn_ywing_squad()
            self.ywing_timer = 0

        # Actualizar cada Y-Wing
        for ywing in self.ywings[:]:  # Copia para poder modificar lista
            route = ywing["route"]
            target = None

            # Navegar por waypoints de la ruta
            if ywing["wp_idx"] < len(route):
                waypoint = route[ywing["wp_idx"]]
                target = {
                    "x": waypoint["x"] + ywing["offset_x"] + ywing["squad_dx"],
                    "y": waypoint["y"] + ywing["squad_dy"],
                    "z": waypoint["z"],
                }

                # Acciones especiales en waypoints
                action = waypoint.get("action")
                if action == "BARREL_ROLL":
                    ywing["roll"] += 0.05
                elif action == "ZIGZAG":
                    ywing["x"] += math.sin(current_time * 4) * 5
                elif action == "DIVE":
                    ywing["y"] += 2.0

            else:
                # Si no hay más waypoints, salir de pantalla
                last_point = route[-1]
                target = {
                    "x": last_point["x"] + ywing["squad_dx"],
                    "y": last_point["y"] + ywing["squad_dy"] + 2000,
                    "z": last_point["z"] + 500,
                }

            # Calcular vector hacia objetivo
            dx = target["x"] - ywing["x"]
            dy = target["y"] - ywing["y"]
            dz = target["z"] - ywing["z"]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)

            # Avanzar waypoint si estamos suficientemente cerca
            if distance < 40.0:
                ywing["wp_idx"] += 1
            else:
                # Movimiento suave hacia objetivo
                speed = 2.5 + (ywing["z"] * 0.08)  # Más rápido cuanto más lejos
                ywing["vx"] += ((dx / distance) * speed - ywing["vx"]) * 0.05
                ywing["vy"] += ((dy / distance) * speed - ywing["vy"]) * 0.05
                ywing["vz"] += ((dz / distance) * speed - ywing["vz"]) * 0.05

            # Aplicar movimiento
            ywing["x"] += ywing["vx"]
            ywing["y"] += ywing["vy"]
            ywing["z"] += ywing["vz"]

            # Coordenadas para dibujo (incluyendo offset de formación)
            draw_x = ywing["x"] + ywing["squad_dx"]
            draw_y = ywing["y"] + ywing["squad_dy"]
            draw_z = ywing["z"]

            if draw_z < 0.5:
                continue

            # ================================================================
            # ESTELAS DE MOTORES
            # ================================================================
            scale = 500.0 / draw_z
            screen_x = center_x + draw_x * scale
            screen_y = center_y + draw_y * scale

            # Offset de motores (proporcional al tamaño)
            engine_offset = 35 * (scale / 90.0) * 1.5

            # Añadir puntos a estelas
            ywing["trail_l"].append((screen_x - engine_offset, screen_y))
            ywing["trail_r"].append((screen_x + engine_offset, screen_y))

            # Limitar longitud de estelas
            if len(ywing["trail_l"]) > 10:
                ywing["trail_l"].pop(0)
                ywing["trail_r"].pop(0)

            # Dibujar estelas si hay suficientes puntos
            if len(ywing["trail_l"]) > 1:
                pygame.draw.lines(surface, (100, 200, 255), False, ywing["trail_l"], 2)
                pygame.draw.lines(surface, (100, 200, 255), False, ywing["trail_r"], 2)

            # ================================================================
            # DIBUJAR Y-WING
            # ================================================================
            ship_draw = ywing.copy()
            ship_draw["x"] = draw_x
            ship_draw["y"] = draw_y
            self.draw_ywing_3d(surface, ship_draw, center_x, center_y)

            # ================================================================
            # ACTIVAR CELDAS CUANDO LAS NAVES PASAN CERCA
            # ================================================================
            if draw_z < 60 and random.random() < 0.1:
                grid_z = int(draw_z / spacing_z) - 2
                if grid_z > 0:
                    self.lit_cells.append(
                        [
                            grid_z,
                            random.choice([-1, 0]),
                            random.choice(self.cyber_palette),
                            1.0,
                        ]
                    )

            # Eliminar Y-Wing si está demasiado lejos
            if ywing["z"] > 400:
                self.ywings.remove(ywing)

        # ====================================================================
        # LÓGICA DE X-WINGS (primer plano)
        # ====================================================================
        # Ordenar por profundidad (más lejos primero)
        self.squadron.sort(key=lambda ship: ship["z"], reverse=True)

        for ship in self.squadron[:]:  # Copia para modificar lista
            route = ship["route"]
            target_point = None

            # Navegar por waypoints
            if ship["wp_idx"] < len(route):
                waypoint = route[ship["wp_idx"]]
                target_point = (
                    waypoint["x"] + ship["offset_x"],
                    waypoint["y"] + ship["offset_y"],
                    waypoint["z"],
                )

                # Acciones especiales
                action = waypoint.get("action")
                if action == "BARREL_ROLL":
                    ship["roll"] += 0.05
                elif action == "ZIGZAG":
                    ship["x"] += math.sin(current_time * 4) * 5
                    ship["roll"] = math.sin(current_time * 4) * 0.5

            else:
                # Continuar en línea recta si no hay más waypoints
                target_point = (ship["x"], ship["y"], ship["z"] + 100)

            # Calcular vector hacia objetivo
            dx = target_point[0] - ship["x"]
            dy = target_point[1] - ship["y"]
            dz = target_point[2] - ship["z"]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)

            if distance < 10.0:
                # Avanzar al siguiente waypoint
                ship["wp_idx"] += 1
            else:
                # Movimiento suave
                vx_target = (dx / distance) * 3.5
                vy_target = (dy / distance) * 3.5

                ship["vx"] += (vx_target - ship["vx"]) * 0.05
                ship["vy"] += (vy_target - ship["vy"]) * 0.05

                # ============================================================
                # DETECCIÓN Y EVASIÓN DE COLISIÓN CON SÍMBOLO DE PAZ
                # ============================================================
                if 1.0 < ship["z"] < 30.0:
                    # Predecir posición futura
                    future_x = int(
                        center_x + ((ship["x"] + ship["vx"] * 10) / ship["z"])
                    )
                    future_y = int(
                        center_y + ((ship["y"] + ship["vy"] * 10) / ship["z"])
                    )

                    if 0 <= future_x < self.w and 0 <= future_y < self.h:
                        try:
                            # Si colisionaría, evadir
                            if self.collision_mask.get_at((future_x, future_y)):
                                ship["evading"] = True
                                # Empujar en dirección opuesta al centro
                                if (future_x - center_x) > 0:
                                    ship["vx"] += 6.0
                                else:
                                    ship["vx"] -= 6.0
                        except:
                            pass  # Fuera de los límites de la máscara

            # Aplicar movimiento
            ship["x"] += ship["vx"]
            ship["y"] += ship["vy"]
            ship["z"] += ship["vz"]

            # ================================================================
            # ESTELA Y DIBUJO
            # ================================================================
            # Proyección a pantalla
            screen_x = center_x + ship["x"] / max(0.1, ship["z"])
            screen_y = center_y + ship["y"] / max(0.1, ship["z"])

            # Añadir punto a estela
            ship["trail"].append((screen_x, screen_y))
            if len(ship["trail"]) > 8:
                ship["trail"].pop(0)

            # Dibujar estela
            if len(ship["trail"]) > 1:
                trail_color = (255, 50, 50) if ship["evading"] else (100, 255, 150)
                pygame.draw.lines(surface, trail_color, False, ship["trail"], 2)

            # Dibujar X-Wing
            self.draw_xwing_3d(surface, ship, center_x, center_y)

            # Eliminar si está demasiado lejos y reponer
            if ship["z"] > 80:
                self.squadron.remove(ship)
                self.spawn_xwing()

        # Reponer escuadrón si hay pocas naves
        if len(self.squadron) < 8:
            self.spawn_xwing()

        # ====================================================================
        # TEXTOS FINALES ANIMADOS
        # ====================================================================
        y_offset = math.sin(current_time * 1.5) * 5  # Flotación vertical

        # Texto principal "THIS WAR IS OVER"
        self.render_rainbow_text(
            surface,
            "> THIS WAR IS OVER!",
            center_x,
            center_y - 50 + y_offset,
            current_time,
        )

        # Texto secundario "ENJOY THE MOMENT"
        self.render_rainbow_text(
            surface,
            "> ENJOY THE MOMENT!",
            center_x,
            center_y + 50 + y_offset,
            current_time + 1.0,
        )

        # Créditos (texto pequeño abajo)
        font_small = pygame.font.SysFont("consolas", 14)
        credits = font_small.render(
            "CODE: MihWeb0hM0ren0h // GFX: LoverActiveMind // AKA: MetalWAR",
            True,
            (0, 200, 200),
        )
        surface.blit(credits, (center_x - credits.get_width() // 2, self.h - 30))

    def draw(self, surface, player_ref):
        """
        Dibuja todo el evento Praxis según la fase actual
        """
        if not self.active:
            return

        current_time = time.time()
        elapsed = current_time - self.start_time

        # ====================================================================
        # FASE 1: CARGA (0-2 segundos)
        # ====================================================================
        if elapsed < 2.0:
            self.phase = "CHARGE"
            progress = elapsed / 2.0

            # Limpiar superficie baja resolución
            self.low_surf.fill((0, 0, 0))
            low_center_x, low_center_y = self.low_w // 2, self.low_h // 2

            # Partículas de energía cargando
            for _ in range(15):
                angle = random.uniform(0, 6.28)
                distance = (1.0 - progress) * 20 + random.uniform(0, 5)

                particle_x = int(low_center_x + math.cos(angle) * distance)
                particle_y = int(low_center_y + math.sin(angle) * distance)

                particle_color = random.choice(
                    [
                        (255, 255, 255),  # Blanco
                        (255, 0, 0),  # Rojo
                        (255, 200, 0),  # Naranja
                    ]
                )

                pygame.draw.circle(
                    self.low_surf, particle_color, (particle_x, particle_y), 2
                )

            # Núcleo de energía central (creciente)
            core_radius = int(3 + random.uniform(-1, 2) + progress * 8)
            pygame.draw.circle(
                self.low_surf,
                (255, 255, 255),
                (low_center_x, low_center_y),
                core_radius,
            )

            # Escalar y aplicar con efecto ADD (brillo)
            scaled_fire = pygame.transform.scale(self.low_surf, (self.w, self.h))
            surface.blit(scaled_fire, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

            # Flash blanco progresivo (cúbico para efecto dramático)
            if int(progress**3 * 255) > 0:
                flash_surf = pygame.Surface((self.w, self.h))
                flash_surf.fill((255, 255, 255))
                flash_surf.set_alpha(int(progress**3 * 255))
                surface.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # ====================================================================
        # FASE 2: EXPLOSIÓN (2+ segundos)
        # ====================================================================
        else:
            if self.phase == "CHARGE":
                # Transición a explosión
                self.phase = "BLAST"
                self.wiped = True

                # Generar partículas de explosión
                for _ in range(100):
                    angle = random.uniform(0, 6.28)
                    speed = random.uniform(0.1, 4.0)

                    self.blobs.append(
                        [
                            self.low_w // 2,  # X inicial (centro)
                            self.low_h // 2,  # Y inicial (centro)
                            math.cos(angle) * speed,  # Velocidad X
                            math.sin(angle)
                            * speed
                            * 0.8,  # Velocidad Y (más lento vertical)
                            random.uniform(2, 6),  # Tamaño inicial
                            random.uniform(2, 5),  # Tamaño máximo
                            random.uniform(2, 5),  # Vida inicial
                        ]
                    )

            # Reproducir sonido de explosión (una sola vez)
            if not self.blast_sound_played:
                self.play_blast_sound()
                player_ref.fade_out_current()  # Apagar música gradualmente
                self.blast_sound_played = True

            # ================================================================
            # ANIMACIÓN DE EXPLOSIÓN
            # ================================================================
            blast_elapsed = elapsed - 2.0
            self.low_surf.fill((0, 0, 0))

            # Actualizar y dibujar partículas de explosión
            for blob in self.blobs:
                # Movimiento
                blob[0] += blob[2]  # X
                blob[1] += blob[3]  # Y

                # Deceleración
                blob[2] *= 0.92
                blob[3] *= 0.92

                # Decaimiento de vida
                blob[6] -= 0.016

                # Dibujar si aún tiene vida
                if blob[6] > 0:
                    # Color: blanco -> amarillo -> rojo -> apagar
                    intensity = max(0, min(255, int(255 * (blob[6] / blob[5]))))
                    color = (255, intensity, 0)

                    pygame.draw.circle(
                        self.low_surf, color, (int(blob[0]), int(blob[1])), int(blob[4])
                    )

            # Escalar explosión a pantalla completa
            big_fire = pygame.transform.scale(self.low_surf, (self.w, self.h))
            big_fire.set_colorkey((0, 0, 0))  # Negro = transparente
            surface.blit(big_fire, (0, 0))

            # ================================================================
            # FASE 3: SECUENCIA DE PAZ (después de 2.5 segundos de explosión)
            # ================================================================
            if blast_elapsed > 2.5:
                if self.phase != "FALLOUT":
                    self.phase = "FALLOUT"
                    player_ref.play_ending_track()  # Reproducir tema final

                # Dibujar secuencia de paz completa
                self.draw_fallout_screen(self.fallout_surf, current_time)

                # Transición suave de la explosión a la secuencia de paz
                alpha = min(255, int(((blast_elapsed - 2.5) / 2.0) * 255))
                self.fallout_surf.set_alpha(alpha)

                # Aplicar sobre la superficie principal
                surface.blit(self.fallout_surf, (0, 0))
