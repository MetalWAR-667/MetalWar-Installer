# main.py
# Punto de entrada principal de MetalWar
# Coordina todos los sistemas: audio, efectos, UI, instalación
# VERSIÓN CORREGIDA PARA PYINSTALLER

# ============================================================================
# IMPORTACIONES DE MÓDULOS PROPIOS (sin pygame inicial aquí)
# ============================================================================
import sys
import os
import time
import math
import random
import threading
import colorsys

# ============================================================================
# FIX CRÍTICO PARA PYINSTALLER - DEBE IR ANTES DE CUALQUIER OTRA IMPORTACIÓN
# ============================================================================


def setup_pyinstaller_fixes():
    """Configura todo lo necesario para que funcione en PyInstaller"""

    # 1. Crear carpeta temporal segura
    if hasattr(sys, "_MEIPASS"):
        # Estamos en un .exe de PyInstaller
        temp_base = os.path.join(os.environ.get("TEMP", "."), "metalwar_temp")
    else:
        # Estamos en desarrollo
        temp_base = os.path.join(".", "temp")

    os.makedirs(temp_base, exist_ok=True)

    # 2. Redirigir rutas temporales
    os.environ["METALWAR_TEMP_DIR"] = temp_base

    # 3. Debug info
    print(f"[PYINSTALLER] Temp dir: {temp_base}")
    print(f"[PYINSTALLER] MEIPASS: {getattr(sys, '_MEIPASS', 'NO (dev mode)')}")

    return temp_base


# Ejecutar inmediatamente
TEMP_DIR = setup_pyinstaller_fixes()

# ============================================================================
# IMPORTAR CONFIG DESPUÉS DE LOS FIXES
# ============================================================================
try:
    from config import GAME_CONFIG

    print("[CONFIG] Configuración cargada correctamente")
except ImportError as e:
    print(f"[ERROR] No se pudo cargar config: {e}")
    print("[ERROR] Creando configuración de emergencia...")

    # Configuración de emergencia
    GAME_CONFIG = {
        "GAME_NAME_DISPLAY": "METALWAR",
        "SUBTITLE_DISPLAY": "",
        "WINDOW_SIZE": (1024, 768),
        "FPS": 60,
        "IDLE_TIMEOUT": 20.0,
        "WINDOW_CAPTION": "MetalWar Installer",
        "COLORS": {
            "BLACK": (10, 10, 18),
            "WHITE": (255, 255, 255),
            "BLUE_NEON": (0, 255, 255),
            "RED_ALERT": (255, 0, 0),
            "BUTTON_GRAY": (40, 40, 50),
            "BUTTON_HOVER": (60, 60, 75),
        },
        "AUDIO": {"BPM": 128, "MUSIC_OFFSET": 0.12},
        "BPM_EFFECT": {"IN_NORMAL_MODE": False, "IN_RAVE_MODE": True},
    }

# ============================================================================
# CONSTANTES GLOBALES
# ============================================================================
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# AÑADIDO: Configuración FPS Counter Cyberpunk
FPS_UPDATE_INTERVAL = 0.35  # Actualizar cada 0.35 segundos
FPS_TITLE_UPDATE_INTERVAL = 0.5  # Actualizar título de ventana cada 0.5 segundos
last_fps_update = 0
last_title_update = 0
fps_value = 0
fps_display = "FPS: --"
fps_title_mode = "normal"  # 'normal' o 'cañero'
title_fps_display = "-- FPS"  # Versión para título de ventana

# Valores de sincronización musical
BPM = GAME_CONFIG["AUDIO"]["BPM"]  # Pulsos por minuto
BEAT_LENGTH = 60.0 / BPM  # Duración de un beat en segundos
MUSIC_OFFSET = GAME_CONFIG["AUDIO"]["MUSIC_OFFSET"]  # Offset de sincronización

# =====================================================================================
# Títulos irónicos para el FPS Counter (removido por redundancia con barra de ventana)
# =====================================================================================
FPS_TITLES = {
    "cañero": [
        "FRAMES POR SEGUNDO: {}",
        "RENDERIZANDO A {} FPS",
        "MOTOR 3D: {} FPS",
        "SYNC: {} FPS",
        "FIREWALL: {} FPS",
        "CORE: {} FPS",
        "INTEL SERIE 13 DETECTADO, EXPLOSION INMINENTE!: {} FPS",
        "NVIDIA APRUEBA ESTO: {} FPS",
        "BPM SYNC: {} FPS",
        "ME DESPEINOOOOO!!!: {} FPS",
        "ROOMBA MODE: {} FPS",
        "METALWAR ENGINE: {} FPS",
    ],
    "normal": [
        "FPS: {}",
        "{} frames/s",
        "{} feosporsegundo",
        "FPS Counter: {}",
        "Frame Rate: {}",
    ],
}

# Títulos para barra de ventana (más cortos)
FPS_TITLES_WINDOW = {
    "cañero": [
        "Vamos CPU, Arrrdee!! | {} FPS",
        "INTEL SERIE 13 DETECTADO, EXPLOSION INMINENTE!: {} FPS",
        "BPM Sync @ {} FPS",
        "Pooowaaa!: {} FPS",
        "Todo en orden Sir!: {} FPS",
        "Suavesito mi amol! {} FPS",
    ],
    "normal": [
        "This Installer made By MetalWAR - {} FPS",
        "¡Quiero más FPS, MAAAS!: {} FPS",
        "NVIDIA NO APRUEBA ESTO: {}FeosPerSecond",
        "{} fps",
    ],
}

# ============================================================================
# VARIABLES GLOBALES
# ============================================================================
# IMPORTANTE: No instanciar objetos pygame a nivel de módulo
geometric_transformer = None
spectrum_analyzer = None
starfield = None
praxis_event = None
crt_boot = None
# ... otras variables globales ...
# VARIABLES PARA EFECTOS RAVE
demo_cache_initialized = False
vignette_surf = None
scanline_surf = None
flare_surf = None
chroma_temp = None
rave_shake_x = 0
rave_shake_y = 0


# ============================================================================
# FUNCIÓN DE PRECARGA (def ANTES de main())
# ============================================================================
def preload_game_resources():
    """
    Esta función se ejecuta AUTOMÁTICAMENTE durante el CRTBoot
    """
    print("[SISTEMA] Precargando recursos...")

    global geometric_transformer, spectrum_analyzer, starfield, praxis_event

    try:
        # Importar dentro de la función para evitar inicialización temprana
        from effects import (
            GeometricTransformer3D,
            SpectrumAnalyzer,
            Starfield,
            PraxisEvent,
        )

        # Cargar objetos pesados aquí
        geometric_transformer = GeometricTransformer3D(SCREEN_WIDTH, SCREEN_HEIGHT)
        spectrum_analyzer = SpectrumAnalyzer(SCREEN_WIDTH, SCREEN_HEIGHT)
        starfield = Starfield(SCREEN_WIDTH, SCREEN_HEIGHT)
        praxis_event = PraxisEvent(SCREEN_WIDTH, SCREEN_HEIGHT)

        print("[SISTEMA] Precarga completada")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


# ============================================================================
# CLASE MUSICCLOCK: Sincronización BPM adaptada al MusicPlayer real
# ============================================================================


class MusicClock:
    """
    Reloj musical que sincroniza efectos visuales con la música
    Calcula beats, secciones y fase actual para sincronización precisa
    """

    def __init__(self, music_player):
        """
        Inicializa el reloj musical

        Args:
            music_player: Instancia de MusicPlayer para control
        """
        self.player = music_player  # Referencia al reproductor
        self.offset = MUSIC_OFFSET  # Offset de sincronización
        self.last_beat = -1  # Último beat detectado
        self.total_beats = 0  # Total de beats desde inicio
        self.beat_start_time = 0  # Tiempo de inicio del beat
        self.current_bpm = BPM  # BPM actual (puede ajustarse)
        self.beat_history = []  # Historial de tiempos de beat
        self.is_playing = False  # Estado de reproducción
        self.last_section = -1  # Última sección detectada

    def start(self):
        """Inicia el reloj cuando empieza la música"""
        self.beat_start_time = time.time()
        self.is_playing = True
        self.last_beat = -1
        self.total_beats = 0
        print(f"[BPM] Reloj iniciado a {self.current_bpm} BPM")

    def update(self):
        """
        Obtiene el estado actual del beat

        Returns:
            Tupla: (beat, phase, new_beat, section, new_section, total_beats)
        """
        # Verificar si la música está sonando (método REAL de pygame)
        import pygame

        music_playing = pygame.mixer.music.get_busy()

        # Detener reloj si la música paró
        if not music_playing and self.is_playing:
            self.is_playing = False
            return 0, 0.0, False, 0, False, 0

        # Iniciar reloj si la música empezó
        if not self.is_playing and music_playing:
            self.start()

        # Si no hay música, retornar valores por defecto
        if not self.is_playing:
            return 0, 0.0, False, 0, False, 0

        # Calcular tiempo desde inicio (con offset)
        current_time = max(0.0, (time.time() - self.beat_start_time) - self.offset)

        # Calcular beat actual y fase (0.0-1.0 dentro del beat)
        current_beat = int(current_time / BEAT_LENGTH)
        beat_phase = (current_time % BEAT_LENGTH) / BEAT_LENGTH
        new_beat = current_beat != self.last_beat

        # Calcular sección (32 beats por sección)
        current_section = current_beat // 32
        new_section = current_section != self.last_section

        # Actualizar estado
        if new_beat:
            self.total_beats += 1
            self.beat_history.append(time.time())

            # Limitar historial para evitar crecimiento infinito
            if len(self.beat_history) > 100:
                self.beat_history.pop(0)

        self.last_beat = current_beat
        self.last_section = current_section

        return (
            current_beat,
            beat_phase,
            new_beat,
            current_section,
            new_section,
            self.total_beats,
        )

    def estimate_bpm(self):
        """
        Estima el BPM real basado en los beats detectados

        Returns:
            BPM estimado (float)
        """
        if len(self.beat_history) < 4:
            return self.current_bpm

        # Calcular intervalos entre beats
        intervals = []
        for i in range(1, len(self.beat_history)):
            interval = self.beat_history[i] - self.beat_history[i - 1]
            intervals.append(interval)

        if intervals:
            # Promedio de intervalos
            avg_interval = sum(intervals) / len(intervals)

            # Convertir a BPM (60 segundos / intervalo)
            estimated_bpm = 60.0 / avg_interval

            # Suavizar estimación (90% valor anterior, 10% nuevo)
            self.current_bpm = self.current_bpm * 0.9 + estimated_bpm * 0.1

            return self.current_bpm

        return self.current_bpm

    def reset(self):
        """Reinicia el reloj (útil al cambiar de canción)"""
        self.start()


# ============================================================================
# CLASE BPMSYNCHRONIZER: Añade sincronización BPM a los efectos existentes
# ============================================================================


class BPMSynchronizer:
    """
    Extiende los efectos visuales con sincronización BPM
    Genera pulsos, flashes y efectos rítmicos
    """

    def __init__(self, width, height):
        """
        Inicializa el sincronizador BPM

        Args:
            width: Ancho del área de dibujo
            height: Alto del área de dibujo
        """
        self.width = width
        self.height = height

        # Parámetros de efectos BPM
        self.beat_pulse = 0.0  # Intensidad del pulso actual (0.0-1.0)
        self.flash_alpha = 0  # Alpha para efecto flash
        self.strobe_active = False  # Efecto strobe activo
        self.strobe_timer = 0  # Temporizador para strobe
        self.color_shift = 0.0  # Desplazamiento de color
        self.current_section = 0  # Sección musical actual
        self.section_progress = 0.0  # Progreso dentro de la sección

        # Control de timing
        self.beat_counter = 0  # Contador de beats
        self.last_beat_time = 0  # Tiempo del último beat
        self.beat_interval = BEAT_LENGTH  # Intervalo ideal entre beats

        # Estado del efecto BPM (será sobrescrito por configuración)
        self.bpm_enabled = True

    def on_beat(self, beat, phase, strength=1.0):
        """
        Llamado en cada beat para activar efectos

        Args:
            beat: Número de beat actual
            phase: Fase dentro del beat (0.0-1.0)
            strength: Fuerza del beat (0.0-1.0)
        """
        current_time = time.time()
        self.beat_counter = beat
        self.beat_pulse = strength

        # Calcular timing perfecto (cuán cerca del beat ideal)
        if self.last_beat_time > 0:
            actual_interval = current_time - self.last_beat_time
            timing_perfect = 1.0 - min(
                1.0, abs(actual_interval - self.beat_interval) / self.beat_interval
            )
            strength *= timing_perfect

        self.last_beat_time = current_time

        # ====================================================================
        # EFECTOS ESPECÍFICOS POR TIPO DE BEAT
        # ====================================================================
        if beat % 4 == 0:  # Beat fuerte (cada 4 beats)
            self.flash_alpha = 100 * strength
            self._trigger_strong_effects(beat)

        elif beat % 2 == 0:  # Beat medio (cada 2 beats)
            self.flash_alpha = 60 * strength
            self._trigger_medium_effects(beat)

        else:  # Beat débil
            self.flash_alpha = 30 * strength

        # ====================================================================
        # CAMBIO DE SECCIÓN (cada 32 beats)
        # ====================================================================
        section = beat // 32
        if section != self.current_section:
            self.current_section = section
            self._on_section_change(section)

    def _trigger_strong_effects(self, beat):
        """
        Efectos para beats fuertes

        Args:
            beat: Número de beat actual
        """
        # Flash más intenso
        self.flash_alpha = 150

        # Ocasionalmente activar strobe en beats específicos
        if beat % 16 == 0 and random.random() < 0.3:
            self.strobe_active = True
            self.strobe_timer = 4  # ~0.06 segundos a 60 FPS

    def _trigger_medium_effects(self, beat):
        """
        Efectos para beats medios

        Args:
            beat: Número de beat actual
        """
        # Efectos sutiles
        if beat % 8 == 0 and random.random() < 0.2:
            self.strobe_active = True
            self.strobe_timer = 2

    def _on_section_change(self, section):
        """
        Cuando cambia la sección musical

        Args:
            section: Número de sección nueva
        """
        print(f"[BPM] Cambiando a sección {section}")
        # Sección 0: Intro, 1: Build-up, 2: Drop, 3: Breakdown, etc.

    def update(self, phase, intensity):
        """
        Actualiza efectos entre beats

        Args:
            phase: Fase actual del beat (0.0-1.0)
            intensity: Intensidad base del efecto

        Returns:
            Intensidad modulada por BPM
        """
        # Decaer efectos gradualmente
        self.beat_pulse *= 0.85
        self.flash_alpha *= 0.7

        # Actualizar strobe
        if self.strobe_active:
            self.strobe_timer -= 1
            if self.strobe_timer <= 0:
                self.strobe_active = False

        # Calcular intensidad modulada por BPM
        beat_wave = math.sin(phase * math.pi * 2)
        modulated_intensity = intensity * (0.6 + 0.4 * beat_wave)

        # Añadir pulso del beat
        modulated_intensity += self.beat_pulse * 0.4

        return min(1.0, modulated_intensity)

    def draw_overlay(self, surface):
        """
        Dibuja efectos overlay (flash, strobe, etc.)

        Args:
            surface: Superficie donde dibujar
        """
        # NOTA: Flash blanco ELIMINADO para evitar molestias visuales
        # Se mantiene solo el strobe para otros efectos

        # Strobe effect (mantenido para usos específicos)
        if self.strobe_active:
            import pygame

            strobe_surf = pygame.Surface((self.width, self.height))
            strobe_surf.fill((255, 255, 255))
            strobe_surf.set_alpha(50)
            surface.blit(strobe_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def toggle_bpm_effect(self):
        """Alterna el efecto BPM en las formas geométricas"""
        self.bpm_enabled = not self.bpm_enabled
        print(
            f"[BPM] Efecto BPM en formas: {'ACTIVADO' if self.bpm_enabled else 'DESACTIVADO'}"
        )

    def get_bpm_state(self):
        """
        Obtiene el estado actual del efecto BPM

        Returns:
            Diccionario con estado BPM
        """
        # Determinar tipo de beat actual
        is_strong_beat = self.beat_counter % 4 == 0
        is_medium_beat = self.beat_counter % 2 == 0 and not is_strong_beat

        return {
            "enabled": self.bpm_enabled,
            "beat_pulse": self.beat_pulse,
            "strong_beat": is_strong_beat,
            "medium_beat": is_medium_beat,
        }


# ============================================================================
# FUNCIÓN PRINCIPAL COMPLETA (CORREGIDA PARA PYINSTALLER)
# ============================================================================


def main():
    """Función principal - Punto de entrada del programa"""
    # AÑADIDO: Variables globales para FPS counter
    global last_fps_update, last_title_update, fps_value, fps_display, fps_title_mode, title_fps_display
    global demo_cache_initialized, vignette_surf, scanline_surf, flare_surf, chroma_temp, rave_shake_x, rave_shake_y

    print("MetalWar Final (Modular V1.0) - CON TODAS LAS FUNCIONES + BPM SYNC...")
    print(f"[PYINSTALLER] Temp directory: {TEMP_DIR}")

    # Centrar ventana en pantalla
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    # ========================================================================
    # IMPORTAR PYGAME DENTRO DE main() PARA EVITAR PROBLEMAS DE INICIALIZACIÓN
    # ========================================================================
    import pygame

    # ========================================================================
    # INICIALIZACIÓN DE PYGAME Y SPLASH SCREEN
    # ========================================================================
    splash_active = False

    # Intentar cerrar splash screen de PyInstaller si existe
    try:
        import pyi_splash  # type: ignore
    except ImportError:
        # No hay splash screen (ejecución normal)
        pyi_splash = None

    if pyi_splash and pyi_splash.is_alive():
        splash_active = True
        pyi_splash.update_text("Cargando Motor de Audio...")

    # Inicializar pygame (¡AHORA SÍ!)
    pygame.init()

    # ========================================================================
    # CONFIGURACIÓN DE AUDIO (intentar diferentes frecuencias)
    # ========================================================================
    audio_initialized = False
    audio_configs = [
        (44100, -16, 2, 1024),  # Estándar CD
        (48000, -16, 2, 1024),  # Estándar DVD
    ]

    for freq, size, channels, buffer in audio_configs:
        try:
            pygame.mixer.init(freq, size, channels, buffer)
            audio_initialized = True
            break
        except pygame.error:
            continue

    # Fallback a configuración por defecto
    if not audio_initialized:
        pygame.mixer.init()

    # ========================================================================
    # AHORA SÍ IMPORTAR LOS MÓDULOS QUE USAN PYGAME
    # ========================================================================
    from utils import resource_path, clean_temp_files, apply_glitch, safe_color
    from audio import AudioManager, MusicPlayer
    from ui import (
        LogoMetalWAR,
        C64Scroller,
        SpainText,
        AvatarSystem,
        CyberCursor,
        TacticalHUD,
        HexDumpLoader,
        SystemMonitor,
        CyberControlsUI,
    )
    from effects import (
        Starfield,
        GeometricTransformer3D,
        SpectrumAnalyzer,
        CRTBoot,
        RetroGrid,
        PraxisEvent,
    )
    from installer import Installer, KeyboardFX

    # ========================================================================
    # CONFIGURACIÓN DE VENTANA
    # ========================================================================
    WIDTH, HEIGHT = GAME_CONFIG["WINDOW_SIZE"]
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Título inicial de ventana (sin FPS aún)
    base_title = GAME_CONFIG.get("WINDOW_CAPTION", "MetalWar Installer")
    pygame.display.set_caption(base_title)

    pygame.mouse.set_visible(False)  # Usaremos cursor personalizado

    # Cerrar splash screen si estaba activo
    if splash_active:
        try:
            pyi_splash.close()
        except Exception:
            pass

    # ========================================================================
    # ICONO DE VENTANA (CORREGIDO PARA PYINSTALLER)
    # ========================================================================
    icon_files = ["icon.ico", "icon.png", "logo.png"]

    for icon_file in icon_files:
        try:
            icon_path = resource_path(icon_file)

            # Verificar si el archivo existe
            if os.path.exists(icon_path):
                try:
                    icon_image = pygame.image.load(icon_path)
                    pygame.display.set_icon(icon_image)
                    print(f"[ICONO] Cargado: {icon_file}")
                    break
                except Exception as e:
                    print(f"[ICONO] Error cargando {icon_file}: {e}")
        except Exception as e:
            print(f"[ICONO] Error buscando {icon_file}: {e}")
            continue

    # ========================================================================
    # INICIALIZACIÓN DE SISTEMAS
    # ========================================================================
    clock = pygame.time.Clock()

    # CREAR CRTBoot DESPUÉS de inicializar pygame
    global crt_boot
    crt_boot = CRTBoot(WIDTH, HEIGHT)
    crt_boot.set_preload_callback(preload_game_resources)

    # Inicializar otros sistemas
    stars = Starfield(WIDTH, HEIGHT)
    geometry = GeometricTransformer3D(WIDTH, HEIGHT)
    logo = LogoMetalWAR(WIDTH, HEIGHT)
    scroller = C64Scroller(WIDTH)
    spain_text = SpainText(
        GAME_CONFIG["GAME_NAME_DISPLAY"], GAME_CONFIG["SUBTITLE_DISPLAY"], WIDTH, HEIGHT
    )

    # Audio y música
    player = MusicPlayer()  # ¡REPRODUCTOR ORIGINAL FUNCIONAL!

    # Sistemas de UI e instalación
    avatar_sys = AvatarSystem()
    key_fx = KeyboardFX()
    installer = Installer(avatar_system=avatar_sys, key_fx=key_fx)
    grid = RetroGrid(WIDTH, HEIGHT)
    hex_loader = HexDumpLoader(WIDTH, HEIGHT)
    sys_monitor = SystemMonitor()
    controls_ui = CyberControlsUI()

    # Avatar para controles (modo ayuda)
    controls_avatar = AvatarSystem()
    controls_avatar.visible = True
    controls_avatar.fade_alpha = 255
    controls_avatar.installation_mode = False
    controls_avatar.default_barks = [
        "Usa las flechas para navegar música.",
        "ESC para salir.",
        "Subir volumen: Flecha Arriba.",
        "Bajar volumen: Flecha Abajo.",
        "F1: Monitor del sistema.",
        "Click derecho en logo: Modo RAVE.",
        "Tecla B: Info BPM.",
        "Tecla N: Control BPM en formas.",
    ]
    controls_avatar.state = "THINKING"
    controls_avatar.wait_start = time.time() - 4.0  # Mostrar mensaje pronto

    # Efectos especiales
    praxis_event = PraxisEvent(WIDTH, HEIGHT)
    analyzer = SpectrumAnalyzer(WIDTH, HEIGHT)
    tactical_hud = TacticalHUD(WIDTH, HEIGHT)
    cyber_cursor = CyberCursor()

    # Sincronización BPM (NUEVO)
    bpm_sync = BPMSynchronizer(WIDTH, HEIGHT)

    # Iniciar según configuración para modo NORMAL (BPM desactivado por defecto)
    bpm_sync.bpm_enabled = GAME_CONFIG["BPM_EFFECT"]["IN_NORMAL_MODE"]
    music_clock = MusicClock(player)

    # Log inicial de configuración BPM
    print(
        f"[BPM CONFIG] Normal: {'ON' if GAME_CONFIG['BPM_EFFECT']['IN_NORMAL_MODE'] else 'OFF'}, Rave: {'ON' if GAME_CONFIG['BPM_EFFECT']['IN_RAVE_MODE'] else 'OFF'}"
    )

    # ========================================================================
    # AUDIO DE INTRODUCCIÓN (CORREGIDO PARA PYINSTALLER)
    # ========================================================================
    # Usar TEMP_DIR en lugar de ruta relativa
    temp_intro_path = os.path.join(TEMP_DIR, "temp_intro.wav")
    print(f"[VOZ] Ruta temporal: {temp_intro_path}")

    intro_voice = AudioManager.generate_voice(
        "System... initialized... Welcome... to My War.",
        temp_intro_path,  # ← ¡CORREGIDO!
    )
    intro_played = False
    main_start_time = None

    # ========================================================================
    # VARIABLES DE ESTADO GLOBAL
    # ========================================================================
    show_controls = False  # Mostrar UI de controles
    show_monitor = False  # Mostrar monitor de sistema
    kitt_triggered = False  # Efecto Knight Rider activado
    rave_mode = False  # Modo RAVE activado
    bpm_debug = False  # Mostrar info BPM debug
    music_started = False  # Música iniciada

    run = True  # Bucle principal activo
    main_canvas = pygame.Surface((WIDTH, HEIGHT))  # Superficie de dibujo principal
    last_input_time = time.time()  # Última interacción (para timeout)

    # NO iniciar playlist automáticamente - lo hará el boot sequence

    # ========================================================================
    # INFORMACIÓN DE CONTROLES (consola) - VERSIÓN COMPLETA RESTAURADA
    # ========================================================================
    print("\n" + "=" * 60)
    print("CONTROLES DISPONIBLES:")
    print("=" * 60)
    print("  [Flechas]     Navegar música y volumen")
    print("  [ESC]         Salir del juego")
    print("  [F1]          Mostrar/Ocultar monitor del sistema")
    print("  [B]           Mostrar/Ocultar info BPM")
    print("  [N]           Activar/Desactivar BPM en formas geométricas")
    print("  [P]           Pausar/Reanudar música")
    print("  [R]           Reiniciar timeline BPM")
    print("  [Click Izq]   Instalar / Mostrar controles (en logo)")
    print("  [Click Der]   Activar/Desactivar MODO RAVE (en logo)")
    print("  [Click Der]   Alterna BPM en formas según modo actual")
    print("=" * 60)
    print("MODO RAVE: Click derecho en logo. Glitch, shake y efectos extremos.")
    print("BPM SYNC:  Todo sincronizado con música (beat detection automático).")
    print("=" * 60)

    # ========================================================================
    # EJECUTAR SECUENCIA DE BOOT
    # ========================================================================
    print("[SISTEMA] Iniciando secuencia de arranque...")

    while not crt_boot.pause_completed and run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                run = False

        crt_boot.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    # NUEVO: FADE DEL SONIDO
    pygame.mixer.fadeout(200)

    if not run:
        pygame.quit()
        return

    print("[SISTEMA] Arranque completado")

    # ========================================================================
    # BUCLE PRINCIPAL (continuación del código original)
    # ========================================================================
    while run:
        current_time = time.time()

        # ====================================================================
        # ACTUALIZACIÓN DE FPS COUNTER CYBERPUNK (AÑADIDO)
        # ====================================================================
        # Actualizar valor de FPS periódicamente
        if current_time - last_fps_update > FPS_UPDATE_INTERVAL:
            fps_value = int(clock.get_fps())
            last_fps_update = current_time

            # 50% chance de usar título cañero vs normal
            if random.random() < 0.5:
                fps_title_mode = "cañero"
                titles = FPS_TITLES["cañero"]
            else:
                fps_title_mode = "normal"
                titles = FPS_TITLES["normal"]

            # Seleccionar título aleatorio del modo actual
            title_template = random.choice(titles)
            fps_display = title_template.format(fps_value)

        # Actualizar título de ventana con FPS (más lento para no saturar)
        if current_time - last_title_update > FPS_TITLE_UPDATE_INTERVAL:
            last_title_update = current_time

            # 30% chance de usar título cañero en ventana
            if random.random() < 0.3:
                window_mode = "cañero"
                window_titles = FPS_TITLES_WINDOW["cañero"]
            else:
                window_mode = "normal"
                window_titles = FPS_TITLES_WINDOW["normal"]

            # Seleccionar título para ventana
            window_template = random.choice(window_titles)
            title_fps_display = window_template.format(fps_value)

            # Actualizar título de ventana
            full_title = f"{base_title} | {title_fps_display}"
            pygame.display.set_caption(full_title)

        # ====================================================================
        # 1. SINCRO BPM (solo si la música está sonando) - SISTEMA COMPLETO
        # ====================================================================
        if pygame.mixer.music.get_busy() or music_started:
            beat, beat_phase, new_beat, section, new_section, total_beats = (
                music_clock.update()
            )

            # Eventos en cada beat NUEVO - SINCRONIZACIÓN PRECISA
            if new_beat:
                # Calcular fuerza del beat (fuerte cada 4 beats)
                beat_strength = (
                    1.0 if beat % 4 == 0 else (0.7 if beat % 2 == 0 else 0.4)
                )
                bpm_sync.on_beat(beat, beat_phase, beat_strength)

                # Mostrar info debug ocasionalmente
                if beat % 16 == 0 and bpm_debug:
                    estimated_bpm = music_clock.estimate_bpm()
                    print(
                        f"[BPM] Beat: {beat} | Sección: {section} | BPM: {estimated_bpm:.1f}"
                    )
        else:
            # Si no hay música, usar valores por defecto
            beat, beat_phase, new_beat, section = 0, 0.0, False, 0
            total_beats = 0

        # ====================================================================
        # 2. INTENSIDAD Y KICK (sistema original + BPM)
        # ====================================================================
        if rave_mode:
            # Modo RAVE con BPM sync
            kick = 0.6 + math.sin(current_time * 50) * 0.3
            intensity = 0.7 + (random.random() * 0.2)
        else:
            # Modo normal
            kick = max(0, math.sin(current_time * 7)) ** 10

            # Si hay música sincronizada, usar fase del beat
            if pygame.mixer.music.get_busy():
                intensity = 0.5 + 0.3 * math.sin(beat_phase * math.pi)
            else:
                intensity = (math.sin(current_time * 4) + 1) / 2

        # Modular intensidad con BPM
        modulated_intensity = bpm_sync.update(beat_phase, intensity)

        # ====================================================================
        # 3. DIBUJAR FONDO
        # ====================================================================
        main_canvas.fill(GAME_CONFIG["COLORS"]["BLACK"])

        # ====================================================================
        # 4. INICIALIZAR SISTEMA PRINCIPAL (post-boot)
        # ====================================================================
        if main_start_time is None:
            main_start_time = current_time
            logo.start_animation()
            intro_played = False

            # Iniciar música DESPUÉS del boot sequence
            if not music_started:
                player.start_playlist()
                music_started = True
                music_clock.start()
                print("[MÚSICA] Playlist iniciada")

        main_time = current_time - main_start_time

        # ====================================================================
        # 5. ACTUALIZACIONES DE SISTEMAS
        # ====================================================================
        # Actualizar instalador
        installer.update()

        # Actualizar avatar principal
        avatar_sys.update()

        # Actualizar avatar de controles si está visible
        if show_controls:
            controls_avatar.update()

        # Actualizar reproductor de música (ORIGINAL)
        player_update_result = player.update()
        if player_update_result == "EXIT":
            run = False

        # Reproducir intro si no se ha hecho
        if not intro_played:
            AudioManager.play_robotic(intro_voice)
            intro_played = True

        # ====================================================================
        # 6. MANEJO DE INPUT Y CURSOR
        # ====================================================================
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_clickable = False

        # Determinar elementos clickeables
        install_button = pygame.Rect(20, 540, 240, 40)  # Botón de instalación

        if installer.state in ["WAIT", "WORK"] and install_button.collidepoint(
            mouse_x, mouse_y
        ):
            is_clickable = True
        elif logo.rect.collidepoint(mouse_x, mouse_y):
            is_clickable = True

        # Actualizar cursor personalizado
        cyber_cursor.update(mouse_x, mouse_y, is_clickable)

        # Ocultar controles durante instalación
        if installer.state in ["ARMING", "TARGETING", "FIRED"]:
            show_controls = False

        # Timeout de inactividad
        if installer.state in ["WAIT", "WORK"]:
            if current_time - last_input_time > GAME_CONFIG["IDLE_TIMEOUT"]:
                if show_controls:
                    show_controls = False

                if not avatar_sys.visible:
                    avatar_sys.show()
            else:
                if (
                    installer.state == "WAIT"
                    and avatar_sys.visible
                    and not avatar_sys.installation_mode
                ):
                    avatar_sys.hide()

        # ====================================================================
        # 7. MANEJO DE EVENTOS (TODOS LOS ORIGINALES + NUEVOS)
        # ====================================================================
        for event in pygame.event.get():
            last_input_time = current_time  # Resetear timeout

            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # Controles originales
                if event.key == pygame.K_ESCAPE:
                    run = False

                elif event.key == pygame.K_RIGHT:
                    player.next(show_hud=True)
                    music_clock.reset()  # Reiniciar sincro al cambiar canción

                elif event.key == pygame.K_LEFT:
                    player.prev(show_hud=True)
                    music_clock.reset()

                elif event.key == pygame.K_UP:
                    player.vol_ch(0.1)

                elif event.key == pygame.K_DOWN:
                    player.vol_ch(-0.1)

                elif event.key == pygame.K_F1:
                    show_monitor = not show_monitor

                # Controles nuevos BPM
                elif event.key == pygame.K_b:
                    bpm_debug = not bpm_debug

                    if bpm_debug:
                        print("[BPM] Info activada")
                    else:
                        print("[BPM] Info desactivada")

                elif event.key == pygame.K_n:  # NUEVA TECLA para alternar BPM en formas
                    bpm_sync.toggle_bpm_effect()
                    current_state = bpm_sync.bpm_enabled
                    print(
                        f"[BPM] Efecto en formas: {'ACTIVADO' if current_state else 'DESACTIVADO'}"
                    )

                elif event.key == pygame.K_p:  # Pausa/continuar música
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                        print("[MÚSICA] Pausada")
                    else:
                        pygame.mixer.music.unpause()
                        print("[MÚSICA] Reanudada")

                elif event.key == pygame.K_r:  # Reiniciar timeline
                    music_clock.reset()
                    print("[BPM] Timeline reiniciada")

            # Eventos del transformador 3D (rotación manual)
            geometry.handle_input(event)

            # Eventos de ratón
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    if (
                        installer.state not in ["ARMING", "TARGETING", "FIRED"]
                        and not praxis_event.wiped
                    ):
                        if logo.rect.collidepoint(mouse_x, mouse_y):
                            show_controls = not show_controls

                            if show_controls:
                                controls_avatar.set_immediate_bark(
                                    "Controles activados. Usa las teclas."
                                )
                            else:
                                controls_avatar.set_immediate_bark("Controles ocultos.")

                        elif show_controls:
                            show_controls = False

                    # Botón de instalación
                    if installer.state == "WAIT" and install_button.collidepoint(
                        mouse_x, mouse_y
                    ):
                        installer.start()

                elif event.button == 3:  # Click derecho - MODO RAVE
                    if (
                        logo.rect.collidepoint(mouse_x, mouse_y)
                        and not praxis_event.wiped
                    ):
                        rave_mode = not rave_mode
                        player.vol = 1.0 if rave_mode else 0.4
                        pygame.mixer.music.set_volume(player.vol)

                        # Obtener configuración objetivo según modo actual
                        if rave_mode:
                            target_config = GAME_CONFIG["BPM_EFFECT"][
                                "IN_RAVE_MODE"
                            ]  # True
                        else:
                            target_config = GAME_CONFIG["BPM_EFFECT"][
                                "IN_NORMAL_MODE"
                            ]  # False

                        # APLICAR LA CONFIGURACIÓN DEL MODO ACTUAL DIRECTAMENTE
                        bpm_sync.bpm_enabled = target_config

                        # Solo mostrar información sobre lo que recomienda la configuración
                        config_recommendation = "ON" if target_config else "OFF"
                        current_state = (
                            "ACTIVADO" if bpm_sync.bpm_enabled else "DESACTIVADO"
                        )

                        # Si el estado actual es diferente a lo recomendado, mostrar mensaje informativo
                        if bpm_sync.bpm_enabled != target_config:
                            status_info = (
                                f" (config recomienda: {config_recommendation})"
                            )
                        else:
                            status_info = ""

                        if rave_mode:
                            message = f"😎 ¡MODO RAVE ACTIVADO!{status_info}"
                        else:
                            message = f"😅 Volviendo a modo normal.{status_info}"

                        controls_avatar.set_immediate_bark(message)
                        print(
                            f"[MODO] {'RAVE activado' if rave_mode else 'Modo normal'}"
                        )
                        print(
                            f"[BPM] Efecto en formas: {current_state} (config recomienda: {config_recommendation})"
                        )

        # ====================================================================
        # 8. DIBUJADO PRINCIPAL (TODOS LOS EFECTOS ORIGINALES)
        # ====================================================================
        if not praxis_event.wiped:
            # Efectos de fondo
            stars.draw(main_canvas, modulated_intensity * 0.8)
            grid.draw(main_canvas, current_time, kick)

            # Analizador de espectro (usa el formato actual de música)
            analyzer.draw(main_canvas, modulated_intensity, kick, player.current_fmt)

            # Geometría 3D principal con control BPM
            bpm_state = bpm_sync.get_bpm_state()
            geometry.draw(
                main_canvas,
                modulated_intensity,
                main_time,
                player.current_fmt,
                bpm_state,
            )

            # Logo y texto
            logo.draw(main_canvas, modulated_intensity)
            spain_text.draw(main_canvas, main_time, modulated_intensity, kick)

            # Scroller y HUD de música
            scroller.draw(main_canvas)
            player.draw_hud(main_canvas)

            # Modo RAVE overlay
            if rave_mode:
                rave_font = pygame.font.SysFont("arial black", 40, bold=True)
                rave_text = rave_font.render(
                    "!!! HEADBANG MODE !!!",
                    True,
                    (
                        random.randint(100, 255),
                        random.randint(100, 255),
                        random.randint(100, 255),
                    ),
                )

                # Efecto de vibración aleatoria
                text_x = WIDTH // 2 - rave_text.get_width() // 2 + random.randint(-3, 3)
                text_y = 160 + random.randint(-3, 3)
                main_canvas.blit(rave_text, (text_x, text_y))

            # Avatar durante instalación
            is_installing = installer.state in ["WORK", "ARMING", "TARGETING"]

            if avatar_sys.visible or avatar_sys.fade_alpha > 0:
                # Posición diferente según estado
                if is_installing:
                    avatar_x, avatar_y, avatar_width = 400, 430, 220
                else:
                    avatar_x, avatar_y, avatar_width = 280, 450, 300

                avatar_sys.draw(main_canvas, avatar_x, avatar_y, max_width=avatar_width)

            # Hex loader durante instalación
            if is_installing:
                hex_loader.draw(main_canvas, installer.visual_progress, True)

            # Monitor del sistema
            if show_monitor:
                sys_monitor.draw(main_canvas, clock.get_fps())

            # Info BPM debug
            if bpm_debug:
                debug_font = pygame.font.SysFont("Consolas", 14)
                estimated_bpm = music_clock.estimate_bpm()
                bpm_state_info = bpm_sync.get_bpm_state()

                bpm_info = [
                    f"BPM: {estimated_bpm:.1f}",
                    f"Beat: {beat} (Phase: {beat_phase:.2f})",
                    f"Section: {section}",
                    f"Total Beats: {total_beats}",
                    f"BPM en formas: {'ON' if bpm_state_info['enabled'] else 'OFF'}",
                    f"Beat Pulse: {bpm_state_info['beat_pulse']:.2f}",
                    f"Strong Beat: {bpm_state_info['strong_beat']}",
                    f"Intensity: {modulated_intensity:.2f}",
                    f"Kick: {kick:.2f}",
                    f"Mode: {'RAVE' if rave_mode else 'NORMAL'}",
                ]

                # Fondo semitransparente para panel de debug
                panel_width = 150
                panel_height = len(bpm_info) * 20 + 10
                panel_x = WIDTH - 160
                panel_y = 50

                debug_bg = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
                pygame.draw.rect(main_canvas, (0, 0, 0, 180), debug_bg)
                pygame.draw.rect(main_canvas, (0, 200, 255), debug_bg, 1)

                # Dibujar cada línea de info
                for i, line in enumerate(bpm_info):
                    text_surface = debug_font.render(line, True, (0, 255, 255))
                    main_canvas.blit(text_surface, (panel_x + 5, panel_y + 5 + i * 20))

            # Overlay de dimming para transiciones
            dim_alpha = 0

            if installer.state == "TARGETING":
                dim_alpha = int(
                    min(1.0, (current_time - installer.targeting_time) / 4.0) * 51
                )
            elif installer.state == "FIRED" and not praxis_event.wiped:
                dim_alpha = 51

            if dim_alpha > 0:
                dim_surf = pygame.Surface(GAME_CONFIG["WINDOW_SIZE"])
                dim_surf.fill((0, 0, 0))
                dim_surf.set_alpha(dim_alpha)
                main_canvas.blit(dim_surf, (0, 0))

            # HUD táctico durante targeting
            if installer.state == "TARGETING":
                tactical_hud.activate(install_button)
                targeting_progress = min(
                    1.0, (current_time - installer.targeting_time) / 4.0
                )
                tactical_hud.draw(main_canvas, targeting_progress)

            # Botón de instalación (estados diferentes)
            if installer.state == "ARMING":
                # Efecto de parpadeo rojo de alerta
                if int(current_time * 10) % 2 == 0:
                    button_color = GAME_CONFIG["COLORS"]["RED_ALERT"]
                else:
                    button_color = (50, 0, 0)

                pygame.draw.rect(
                    main_canvas, button_color, install_button, border_radius=6
                )
                pygame.draw.rect(
                    main_canvas, (255, 100, 100), install_button, 2, border_radius=6
                )

                button_font = pygame.font.SysFont("arial", 18, bold=True)
                button_text = button_font.render(
                    installer.status_text, True, (255, 255, 255)
                )
                text_rect = button_text.get_rect(center=install_button.center)
                main_canvas.blit(button_text, text_rect)

            elif installer.state != "FIRED":
                # Botón normal o hover
                if install_button.collidepoint(mouse_x, mouse_y):
                    button_color = GAME_CONFIG["COLORS"]["BUTTON_HOVER"]
                else:
                    button_color = GAME_CONFIG["COLORS"]["BUTTON_GRAY"]

                pygame.draw.rect(
                    main_canvas, button_color, install_button, border_radius=6
                )
                pygame.draw.rect(
                    main_canvas, (100, 100, 255), install_button, 2, border_radius=6
                )

                button_font = pygame.font.SysFont("arial", 18, bold=True)
                button_text = button_font.render(
                    installer.status_text, True, (255, 255, 255)
                )
                text_rect = button_text.get_rect(center=install_button.center)
                main_canvas.blit(button_text, text_rect)

            # Borde exterior dinámico
            border_color = safe_color(
                (
                    20 + 30 * modulated_intensity,
                    20 + 30 * modulated_intensity,
                    50 + 30 * modulated_intensity,
                )
            )
            pygame.draw.rect(
                main_canvas, border_color, (10, 10, WIDTH - 20, HEIGHT - 20), 1
            )

            # Cursor personalizado
            cyber_cursor.draw(main_canvas)

            # UI de controles
            if show_controls:
                controls_ui.draw(main_canvas, controls_avatar)

        # ====================================================================
        # 9. EVENTO PRAXIS (explosión final)
        # ====================================================================
        if installer.state == "FIRED":
            praxis_event.trigger()

        praxis_event.draw(main_canvas, player)

        # Knight Rider effect al final (solo una vez)
        if praxis_event.wiped and not kitt_triggered:
            threading.Thread(target=key_fx.knight_rider, daemon=True).start()
            kitt_triggered = True

        # ====================================================================
        # 10. OVERLAY DE EFECTOS BPM (flash, strobe, etc.)
        # ====================================================================
        bpm_sync.draw_overlay(main_canvas)

        # ====================================================================
        # 11. POST-PROCESAMIENTO (glitch, shake, etc.)
        # ====================================================================
        shake_x, shake_y = 0, 0
        final_frame = main_canvas.copy()

        # Shake y glitch para explosión final
        if praxis_event.active and not praxis_event.wiped:
            shake_x, shake_y = praxis_event.get_shake()
            final_frame = apply_glitch(main_canvas, kick, WIDTH, HEIGHT)

        # Efectos especiales para modo RAVE - CON BPM SYNC
        elif rave_mode:
            # ================================================================
            # OBTENER DATOS BPM (asegurarse que existen)
            # ================================================================
            bpm_state = bpm_sync.get_bpm_state()
            beat_val = bpm_state.get("beat_pulse", 0.0)
            is_strong = bpm_state.get("strong_beat", False)

            # ================================================================
            # INICIALIZACIÓN DE CACHÉ (Solo ocurre la primera vez)
            # ================================================================
            if not demo_cache_initialized:
                # 1. Caché para Vignette (Estático)
                vignette_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                max_radius = int((WIDTH**2 + HEIGHT**2) ** 0.5 / 2)
                for r in range(max_radius, 0, -2):
                    alpha = int(255 * (r / max_radius) ** 3)
                    if alpha > 0:
                        pygame.draw.circle(
                            vignette_surf, (0, 0, 0, 5), (WIDTH // 2, HEIGHT // 2), r
                        )

                # 2. Caché para Scanlines (Textura repetible)
                scanline_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                for y in range(0, HEIGHT, 4):
                    alpha = 90 + (y % 8) * 10
                    pygame.draw.line(
                        scanline_surf, (0, 0, 0, alpha), (0, y), (WIDTH, y), 1
                    )

                # 3. Caché para Lens Flare (Sprite pre-renderizado)
                flare_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
                for r in range(150, 0, -2):
                    alpha = int(100 * (1 - (r / 150) ** 0.5))
                    pygame.draw.circle(
                        flare_surf, (255, 255, 220, alpha), (150, 150), r
                    )

                # 4. Surface temporal para efectos
                chroma_temp = pygame.Surface((WIDTH, HEIGHT))

                demo_cache_initialized = True
                rave_shake_x = 0
                rave_shake_y = 0

            # ================================================================
            # 1. SHAKE "LIQUID" CON BPM
            # ================================================================
            base_shake = beat_val * 25

            if new_beat:
                if is_strong:
                    rave_shake_x = random.choice([-1, 1]) * (20 + base_shake)
                    rave_shake_y = random.choice([-1, 1]) * (15 + base_shake)
                elif beat % 2 == 0:
                    rave_shake_x = random.uniform(-10, 10) * (1 + beat_val)
                    rave_shake_y = random.uniform(-8, 8) * (1 + beat_val)
                else:
                    rave_shake_x = random.uniform(-5, 5) * beat_val
                    rave_shake_y = random.uniform(-4, 4) * beat_val

            damping = 0.8 if beat_val > 0.5 else 0.85
            rave_shake_x *= damping
            rave_shake_y *= damping

            bpm_factor = BPM / 120.0
            sway_x = math.sin(main_time * 2.5 * bpm_factor) * (3 + beat_val * 2)
            sway_y = math.cos(main_time * 1.8 * bpm_factor) * (2 + beat_val * 2)

            shake_x = int(rave_shake_x + sway_x)
            shake_y = int(rave_shake_y + sway_y)

            # ================================================================
            # 2. CHROMATIC ABERRATION (RGB Split)
            # ================================================================
            split_amount = int(beat_val * 15)

            if split_amount > 1:
                chroma_temp.blit(main_canvas, (0, 0))
                final_frame.fill((0, 0, 0))
                final_frame.blit(
                    chroma_temp,
                    (shake_x - split_amount, shake_y),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )
                final_frame.blit(
                    chroma_temp,
                    (shake_x + split_amount, shake_y),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )

                hue_shift = (beat / 16.0) % 1.0
                r, g, b = colorsys.hsv_to_rgb(hue_shift, 0.7, 1.0)
                tint_color = (int(r * 255), int(g * 255), int(b * 255))
                final_frame.fill(tint_color, special_flags=pygame.BLEND_MULT)
            else:
                final_frame.blit(main_canvas, (shake_x, shake_y))

            # ================================================================
            # 3. BLOOM "DOWNSAMPLE" - INTENSIDAD BPM
            # ================================================================
            if beat_val > 0.2:
                scale_factor = 8 - int(beat_val * 5)
                scale_factor = max(3, min(8, scale_factor))

                small_w, small_h = WIDTH // scale_factor, HEIGHT // scale_factor
                mini_surf = pygame.transform.smoothscale(
                    main_canvas, (small_w, small_h)
                )
                bloom_layer = pygame.transform.smoothscale(mini_surf, (WIDTH, HEIGHT))

                bloom_alpha = int(beat_val * 200)
                bloom_layer.set_alpha(bloom_alpha)
                final_frame.blit(bloom_layer, (0, 0), special_flags=pygame.BLEND_ADD)

            # ================================================================
            # 4. SCANLINES & NOISE - VELOCIDAD BPM
            # ================================================================
            scan_speed = 50 * (BPM / 120.0)
            scan_offset = int(main_time * scan_speed) % 4
            final_frame.blit(scanline_surf, (0, scan_offset - 2))

            glitch_chance = 0.05 + (beat_val * 0.25)
            if random.random() < glitch_chance:
                h_strip = random.randint(10, 30 + int(beat_val * 40))
                y_pos = random.randint(0, HEIGHT - h_strip)
                strip_surf = final_frame.subsurface((0, y_pos, WIDTH, h_strip)).copy()
                direction = -1 if beat % 2 == 0 else 1
                offset_strip = direction * (5 + int(beat_val * 15))
                final_frame.blit(strip_surf, (offset_strip, y_pos))

            # ================================================================
            # 5. LENS FLARE / STROBE - ACTIVADO POR BPM
            # ================================================================
            if is_strong and beat_val > 0.4:
                orbit_radius = (WIDTH // 3) * (0.5 + beat_val * 0.5)
                angle = (beat / 4.0) * math.pi
                flare_x = (WIDTH // 2) + math.cos(angle) * orbit_radius
                flare_y = (HEIGHT // 2) + math.sin(angle) * orbit_radius
                scale = 0.8 + (beat_val * 0.8)
                w_f = int(300 * scale)
                h_f = int(300 * scale)
                flare_instance = pygame.transform.scale(flare_surf, (w_f, h_f))
                dest_rect = flare_instance.get_rect(center=(int(flare_x), int(flare_y)))
                flare_alpha = int(255 * beat_val)
                flare_instance.set_alpha(flare_alpha)
                final_frame.blit(
                    flare_instance, dest_rect, special_flags=pygame.BLEND_ADD
                )
                if beat_val > 0.8:
                    flash_alpha = int(beat_val * 60)
                    flash_surf = pygame.Surface((WIDTH, HEIGHT))
                    flash_surf.fill((255, 255, 255))
                    flash_surf.set_alpha(flash_alpha)
                    final_frame.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_ADD)

            # ================================================================
            # 6. VIGNETTE PULSANTE - RESPIRACIÓN RÍTMICA
            # ================================================================
            pulse_speed = 4.0 * (BPM / 120.0)
            vignette_pulse = 20 + int(math.sin(main_time * pulse_speed) * 20)
            base_alpha = 120 + int(beat_val * 50)
            vignette_surf.set_alpha(base_alpha + vignette_pulse)
            final_frame.blit(vignette_surf, (0, 0))
        # Efectos normales con glitch leve en beats fuertes
        else:
            if kick > 0.7:
                glitch_amount = 0.05 + (kick - 0.7) * 0.2
                final_frame = apply_glitch(main_canvas, glitch_amount, WIDTH, HEIGHT)

        # ====================================================================
        # 12. RENDER FINAL A PANTALLA (SIN FPS COUNTER)
        # ====================================================================
        screen.blit(final_frame, (int(shake_x), int(shake_y)))

        # Actualizar pantalla
        pygame.display.flip()

        # Mantener FPS objetivo
        clock.tick(FPS)

    # ========================================================================
    # 13. LIMPIEZA Y SALIDA (fin del programa)
    # ========================================================================
    print("\nFinalizando MetalWar...")

    # Restaurar título original de ventana al salir
    pygame.display.set_caption(base_title)

    # Detener música gradualmente
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(1000)
        time.sleep(1.1)  # Esperar que termine el fadeout

    # Limpiar archivos temporales de audio (CORREGIDO PARA TEMP_DIR)
    try:
        # Importar clean_temp_files si no está ya
        from utils import clean_temp_files

        # Pasar el directorio temporal específico
        clean_temp_files(TEMP_DIR)
    except Exception as e:
        print(f"[LIMPEZA] Error limpiando archivos: {e}")

    # Salir de pygame y sistema
    pygame.quit()
    sys.exit()


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================
if __name__ == "__main__":
    main()
