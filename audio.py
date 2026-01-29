# audio.py
# Sistema de audio y música para MetalWar
# Maneja reproducción musical, efectos de sonido y síntesis de voz

import pygame
import time
import os
import random
import pyttsx3
from config import GAME_CONFIG
from utils import resource_path, VOICE_AVAILABLE

class AudioManager:
    """
    Gestiona efectos de audio y síntesis de voz
    Clase estática para acceso global
    """
    
    @staticmethod
    def play_robotic(sound, base_channel=None):
        """
        Reproduce un sonido con efecto robótico (doble canal con delay)
        
        Args:
            sound: Objeto pygame.mixer.Sound a reproducir
            base_channel: Canal base para sincronización (opcional)
        """
        if not sound:
            return
            
        try:
            # Configurar canales para efecto estéreo/delay
            if base_channel is None:
                # Buscar canales disponibles automáticamente
                c1 = pygame.mixer.find_channel()
                c2 = pygame.mixer.find_channel()
            else:
                # Usar canales específicos para sincronización
                c1 = pygame.mixer.Channel(base_channel)
                c2 = pygame.mixer.Channel(base_channel + 1)
            
            # Reproducir en primer canal (volumen completo)
            if c1:
                c1.set_volume(1.0)
                c1.play(sound)
            
            # Reproducir en segundo canal con delay y volumen reducido
            if c2:
                time.sleep(0.02)  # Pequeño delay para efecto estéreo
                c2.set_volume(0.9)
                c2.play(sound)
                
        except Exception:
            # Fallback silencioso en caso de error de audio
            pass

    @staticmethod
    def generate_voice(text, filename):
        """
        Genera archivo de audio a partir de texto usando síntesis de voz
        
        Args:
            text: Texto a convertir a voz
            filename: Nombre del archivo de salida
            
        Returns:
            pygame.mixer.Sound o None si falla
        """
        if not VOICE_AVAILABLE:
            return None
            
        try:
            # Inicializar motor de síntesis de voz
            engine = pyttsx3.init()
            
            # Buscar voz femenina (Zira en Windows)
            for voice in engine.getProperty("voices"):
                if "zira" in voice.name.lower():
                    engine.setProperty("voice", voice.id)
                    break
            
            # Configurar propiedades de voz
            engine.setProperty("rate", 145)     # Velocidad del habla
            engine.setProperty("volume", 1.0)   # Volumen máximo
            
            # Guardar audio en archivo
            engine.save_to_file(text, filename)
            engine.runAndWait()  # Procesar síntesis
            
            # Cargar como sonido de Pygame
            return pygame.mixer.Sound(filename)
            
        except Exception:
            # Fallback si la síntesis de voz falla
            return None

class MusicPlayer:
    """
    Reproductor de música con playlist aleatoria y efectos visuales HUD
    Soporta múltiples formatos: tracker (MOD, S3M, XM, IT) y audio (MP3, OGG)
    """
    
    def __init__(self):
        """Inicializa el reproductor con configuración por defecto"""
        self.playlist = []      # Lista de archivos de música
        self.idx = 0           # Índice actual en playlist
        self.vol = 0.4         # Volumen (0.0 a 1.0)
        self.is_tracker = False  # Indica si el formato actual es tracker
        self.ht = 0            # Tiempo de expiración del HUD
        self.htxt = ""         # Texto del HUD
        self.htyp = "TEXT"     # Tipo de HUD ("TEXT" o "VOL")
        self.current_fmt = "mp3"  # Formato del archivo actual
        self.peace_mode = False  # Modo de finalización activado
        
        # Reservar canales de audio para efectos específicos
        pygame.mixer.set_reserved(8)
        
        # Buscar archivos de música en la carpeta de recursos
        base_dir = resource_path(".")
        if os.path.exists(base_dir):
            for filename in os.listdir(base_dir):
                f_lower = filename.lower()
                
                # Filtrar formatos soportados y excluir archivos especiales
                if (any(f_lower.endswith(ext) for ext in [".s3m", ".mod", ".xm", ".it", ".ogg", ".mp3"]) 
                    and "temp_" not in f_lower 
                    and "ending" not in f_lower 
                    and "blast" not in f_lower 
                    and "typewriter" not in f_lower):
                    
                    self.playlist.append(os.path.join(base_dir, filename))
        
        # Aleatorizar playlist si hay archivos
        if self.playlist:
            random.shuffle(self.playlist)

    def play(self, specific_file=None, show_hud=True):
        """
        Reproduce un archivo de música
        
        Args:
            specific_file: Archivo específico a reproducir (None para playlist)
            show_hud: Mostrar información en HUD
        """
        try:
            # Determinar qué archivo reproducir
            if specific_file:
                path = specific_file
                display_name = "PEACE THEME"
            elif self.playlist:
                path = self.playlist[self.idx]
                display_name = os.path.basename(path)
            else:
                return  # No hay música para reproducir

            # Determinar formato y si es tracker module
            self.current_fmt = os.path.splitext(path)[1].lower().replace(".", "")
            self.is_tracker = self.current_fmt in ["s3m", "mod", "xm", "it"]
            
            # Cargar y reproducir música
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(0)  # Reproducir una vez (sin loop)
            pygame.mixer.music.set_volume(self.vol)
            
            # Mostrar información en HUD si no estamos en modo paz
            if show_hud and not self.peace_mode:
                self.hud(f"REPRODUCIENDO: {display_name}", duration=3)
                
        except Exception as e:
            # En caso de error, pasar a siguiente canción
            print(f"Error reproduciendo: {e}")
            if self.playlist:
                self.next(show_hud=show_hud)

    def start_playlist(self):
        """Inicia la reproducción de la playlist"""
        if self.playlist:
            self.play()

    def update(self):
        """
        Actualiza estado del reproductor (debe llamarse cada frame)
        
        Returns:
            "EXIT" si el modo paz ha terminado, None en otros casos
        """
        if self.peace_mode:
            # En modo paz, verificar si la música terminó
            if not pygame.mixer.music.get_busy():
                return "EXIT"
            return None
            
        # Avanzar a siguiente canción cuando termine la actual
        if self.playlist and not pygame.mixer.music.get_busy():
            self.next()
            
        return None

    def fade_out_current(self):
        """Apaga gradualmente la música actual (2 segundos)"""
        pygame.mixer.music.fadeout(2000)

    def play_ending_track(self):
        """
        Reproduce la pista de finalización (modo paz)
        Cambia a modo especial con transición suave
        """
        if self.peace_mode:
            return
            
        self.peace_mode = True
        
        # Buscar archivo de ending en diferentes formatos
        found = None
        for ext in [".mp3", ".ogg", ".wav"]:
            filepath = resource_path("ending" + ext)
            if os.path.exists(filepath):
                found = filepath
                break
        
        # Reproducir ending si se encontró
        if found:
            try:
                pygame.mixer.music.load(found)
                pygame.mixer.music.set_volume(self.vol)
                pygame.mixer.music.play(loops=0, fade_ms=4000)  # Fade-in de 4 segundos
            except Exception:
                pass

    def next(self, show_hud=True):
        """Avanza a la siguiente canción en la playlist"""
        if self.playlist:
            self.idx = (self.idx + 1) % len(self.playlist)
            self.play(show_hud=show_hud)

    def prev(self, show_hud=True):
        """Retrocede a la canción anterior en la playlist"""
        if self.playlist:
            self.idx = (self.idx - 1) % len(self.playlist)
            self.play(show_hud=show_hud)

    def vol_ch(self, delta):
        """
        Cambia el volumen
        
        Args:
            delta: Cambio de volumen (+ para subir, - para bajar)
        """
        # Ajustar volumen con límites 0.0-1.0
        self.vol = max(0, min(1, self.vol + delta))
        pygame.mixer.music.set_volume(self.vol)
        
        # Aplicar nuevo volumen a todos los canales reservados
        for i in range(8):
            try:
                pygame.mixer.Channel(i).set_volume(self.vol)
            except Exception:
                pass
        
        # Mostrar HUD de volumen
        self.hud("VOLUMEN", "VOL", duration=2)

    def hud(self, text, hud_type="TEXT", duration=2):
        """
        Muestra texto en el HUD de música
        
        Args:
            text: Texto a mostrar
            hud_type: Tipo de HUD ("TEXT" o "VOL")
            duration: Duración en segundos
        """
        self.htxt = text
        self.htyp = hud_type
        self.ht = time.time() + duration

    def draw_hud(self, surface):
        """
        Dibuja el HUD de música en la pantalla
        
        Args:
            surface: Superficie donde dibujar
        """
        # Verificar si el HUD debe mostrarse
        if time.time() > self.ht or self.peace_mode:
            return
            
        # Calcular alpha para fade-out
        alpha = min(255, int((self.ht - time.time()) * 255))
        
        # Dimensiones del HUD
        width, height = 350, 35
        
        # Crear superficie con transparencia
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))  # Fondo semitransparente
        pygame.draw.rect(bg, (0, 255, 255), (0, 0, width, height), 1)  # Borde cyan
        
        font = pygame.font.SysFont("arial", 14, bold=True)
        
        # HUD de volumen (barra horizontal)
        if self.htyp == "VOL":
            bar_width = int((width - 20) * self.vol)
            pygame.draw.rect(bg, (0, 255, 255), (10, 12, bar_width, 10))  # Barra de volumen
            bg.blit(font.render(f"VOL: {int(self.vol * 100)}%", True, 
                               GAME_CONFIG["COLORS"]["WHITE"]), (10, -2))
        
        # HUD de texto (nombre de canción)
        else:
            if "REPRODUCIENDO:" in self.htxt:
                # Separar etiqueta y nombre de canción para colores diferentes
                label = "REPRODUCIENDO: "
                song_name = self.htxt.replace(label, "")
                
                label_surf = font.render(label, True, GAME_CONFIG["COLORS"]["LIGHT_TEXT"])
                song_surf = font.render(song_name, True, GAME_CONFIG["COLORS"]["WHITE"])
                
                # Combinar ambas superficies
                combined = pygame.Surface((label_surf.get_width() + song_surf.get_width(), 
                                         label_surf.get_height()), pygame.SRCALPHA)
                combined.blit(label_surf, (0, 0))
                combined.blit(song_surf, (label_surf.get_width(), 0))
                text_surface = combined
            else:
                text_surface = font.render(self.htxt, True, GAME_CONFIG["COLORS"]["LIGHT_TEXT"])
            
            text_width = text_surface.get_width()
            margin = 10
            
            # Ajustar visualización según ancho del texto
            if text_width <= width - 20:
                # Centrar si cabe
                bg.blit(text_surface, (margin, 8))
            else:
                # Scroll horizontal si es muy largo
                offset = int(time.time() * 60) % (text_width + 50)
                bg.blit(text_surface, (margin - offset, 8))
                bg.blit(text_surface, (margin - offset + text_width + 50, 8))
        
        # Aplicar fade-out y dibujar
        bg.set_alpha(alpha)
        screen_height = GAME_CONFIG["WINDOW_SIZE"][1]
        surface.blit(bg, (20, screen_height - 100))