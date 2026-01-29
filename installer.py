# installer.py
# Sistema de instalación para MetalWar
# Detecta juegos Steam/Epic, maneja extracción de archivos y parcheo post-instalación

import winreg
import re
import os
import zipfile
import threading
import time
import subprocess
import tkinter as tk
import json 
from tkinter import filedialog
import ctypes
import random

from config import GAME_CONFIG
from utils import resource_path
from audio import AudioManager

# ============================================================================
# CLASE KEYBOARDFX: Efectos de teclado LED (solo Windows)
# ============================================================================

class KeyboardFX:
    """
    Controla LEDs del teclado (Caps Lock, Num Lock, Scroll Lock) para efectos visuales
    Solo funciona en Windows con acceso a API de usuario
    """
    
    def __init__(self):
        """Inicializa el controlador de efectos de teclado"""
        self.available = False
        
        # Solo en Windows
        if os.name == 'nt':
            try:
                # Cargar librería de usuario de Windows
                self.user32 = ctypes.windll.user32
                self.available = True
                
                # Códigos de teclas virtuales (Virtual-Key Codes)
                self.VK_NUMLOCK = 0x90    # Tecla Num Lock
                self.VK_SCROLL = 0x91     # Tecla Scroll Lock  
                self.VK_CAPITAL = 0x14    # Tecla Caps Lock
                
            except Exception:
                # Fallback si no se puede acceder a la API
                pass

    def toggle_key(self, key_code):
        """
        Alterna el estado de una tecla LED (prende/apaga)
        
        Args:
            key_code: Código de tecla virtual (VK_NUMLOCK, etc.)
        """
        if not self.available:
            return
            
        try:
            # Simular presión y liberación de tecla
            # 0x45 = KEYEVENTF_EXTENDEDKEY (tecla extendida)
            self.user32.keybd_event(key_code, 0x45, 0x1, 0)  # KEY DOWN
            self.user32.keybd_event(key_code, 0x45, 0x3, 0)  # KEY UP
        except Exception:
            pass

    def get_key_state(self, key_code):
        """
        Obtiene el estado actual de una tecla LED
        
        Args:
            key_code: Código de tecla virtual
            
        Returns:
            1 si está encendida, 0 si apagada
        """
        if not self.available:
            return 0
            
        try:
            # GetKeyState retorna estado alto si la tecla está encendida
            return self.user32.GetKeyState(key_code) & 1
        except Exception:
            return 0

    def disco_mode(self, duration=2.0):
        """
        Efecto discoteca: LEDs parpadeando aleatoriamente
        
        Args:
            duration: Duración del efecto en segundos
        """
        if not self.available:
            return
            
        end_time = time.time() + duration
        led_keys = [self.VK_NUMLOCK, self.VK_CAPITAL, self.VK_SCROLL]
        
        while time.time() < end_time:
            # Seleccionar LED aleatorio
            key = random.choice(led_keys)
            self.toggle_key(key)  # Alternar estado
            time.sleep(0.1)  # Pausa entre cambios
        
        # Estado final: Caps Lock apagado, Num Lock encendido
        if self.get_key_state(self.VK_CAPITAL):
            self.toggle_key(self.VK_CAPITAL)
            
        if not self.get_key_state(self.VK_NUMLOCK):
            self.toggle_key(self.VK_NUMLOCK)

    def knight_rider(self):
        """
        Efecto Knight Rider: LEDs que se mueven en secuencia
        (Num Lock -> Caps Lock -> Scroll Lock -> Caps Lock)
        """
        if not self.available:
            return
            
        sequence = [self.VK_NUMLOCK, self.VK_CAPITAL, self.VK_SCROLL, self.VK_CAPITAL]
        index = 0
        
        while True:
            # Encender LED actual
            key = sequence[index]
            self.toggle_key(key)
            time.sleep(0.15)
            
            # Apagar después de breve pausa
            self.toggle_key(key)
            time.sleep(0.05)
            
            # Siguiente LED en secuencia
            index = (index + 1) % len(sequence)

# ============================================================================
# CLASE INSTALLER: Sistema principal de instalación
# ============================================================================

class Installer:
    """
    Maneja la instalación completa del parche/traducción
    Incluye detección automática, extracción y post-procesamiento
    """
    
    def __init__(self, avatar_system=None, key_fx=None):
        """
        Inicializa el instalador
        
        Args:
            avatar_system: Referencia al sistema de avatar (opcional)
            key_fx: Referencia a efectos de teclado (opcional)
        """
        # Estado del instalador
        self.state = "WAIT"           # Estados: WAIT, WORK, ARMING, TARGETING, FIRED
        self.real_progress = 0.0      # Progreso real de extracción (0.0-1.0)
        self.visual_progress = 0.0    # Progreso visual (suavizado para animación)
        
        # Detección de ruta
        self.detected_path = None     # Ruta detectada del juego
        self.mode = "MANUAL"          # Modo: MANUAL, STEAM, EPIC
        self.status_text = "SELECCIONAR RUTA"  # Texto de estado en UI
        
        # Temporizadores para efectos
        self.start_time = 0          # Inicio de instalación
        self.armed_time = 0          # Inicio de fase "ARMING"
        self.targeting_time = 0      # Inicio de fase "TARGETING"
        
        # Control de voces/sonidos
        self.voice_triggered = False          # Voz "Systems Armed" reproducida
        self.locked_voice_played = False      # Voz "Target Locked" reproducida
        self.firing_voice_played = False      # Voz "Firing" reproducida
        
        # Referencias a sistemas externos
        self.avatar = avatar_system  # Sistema de avatar para mensajes
        self.key_fx = key_fx        # Efectos de teclado
        
        # Intentar detección automática
        if not self.detect_steam():
            self.detect_epic()

    def detect_steam(self):
        """
        Detecta instalación de Steam y busca el juego
        
        Returns:
            True si se encontró en Steam, False en caso contrario
        """
        try:
            # Abrir registro de Windows para Steam
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                         r"Software\Valve\Steam")
            
            # Obtener ruta de instalación de Steam
            steam_path, _ = winreg.QueryValueEx(registry_key, "SteamPath")
            registry_key.Close()
            
            # Lista de posibles carpetas de biblioteca
            library_folders = [
                os.path.join(os.path.normpath(steam_path), "steamapps")
            ]
            
            # Buscar bibliotecas adicionales en libraryfolders.vdf
            vdf_path = os.path.join(library_folders[0], "libraryfolders.vdf")
            if os.path.exists(vdf_path):
                with open(vdf_path, "r", encoding="utf-8") as vdf_file:
                    content = vdf_file.read()
                    
                    # Extraer rutas de bibliotecas adicionales
                    for match in re.findall(r'"path"\s+"(.*?)"', content):
                        library_folders.append(
                            os.path.join(match.replace("\\\\", "\\"), "steamapps")
                        )
            
            # Buscar el juego en cada biblioteca
            for library in library_folders:
                game_path = os.path.join(library, "common", GAME_CONFIG["GAME_FOLDER_NAME"])
                
                if os.path.exists(game_path):
                    self.detected_path = game_path
                    self.mode = "STEAM"
                    self.status_text = "INSTALAR (STEAM)"
                    return True
                    
        except Exception:
            # Fallback silencioso si hay error en registro
            pass
            
        return False

    def detect_epic(self):
        """
        Detecta instalación de Epic Games Launcher y busca el juego
        
        Returns:
            True si se encontró en Epic, False en caso contrario
        """
        try:
            # Ruta de manifiestos de Epic Games
            manifest_dir = os.path.join(
                os.environ["ProgramData"], 
                "Epic", 
                "EpicGamesLauncher", 
                "Data", 
                "Manifests"
            )
            
            if os.path.exists(manifest_dir):
                # Buscar en todos los archivos .item (manifiestos)
                for filename in os.listdir(manifest_dir):
                    if filename.endswith(".item"):
                        try:
                            manifest_path = os.path.join(manifest_dir, filename)
                            
                            with open(manifest_path, "r", encoding="utf-8") as json_file:
                                manifest_data = json.load(json_file)
                                
                                install_location = manifest_data.get("InstallLocation")
                                
                                if install_location and os.path.exists(install_location):
                                    # Verificar si es nuestro juego
                                    folder_name = os.path.basename(os.path.normpath(install_location))
                                    
                                    if folder_name == GAME_CONFIG["GAME_FOLDER_NAME"]:
                                        self.detected_path = install_location
                                        self.mode = "EPIC"
                                        self.status_text = "INSTALAR (EPIC)"
                                        return True
                                        
                        except Exception:
                            # Continuar con siguiente manifiesto en caso de error
                            continue
                            
        except Exception:
            # Fallback si no se puede acceder a datos de Epic
            pass
        
        # Modo manual si no se detectó automáticamente
        self.status_text = "SELECCIONAR RUTA"
        self.mode = "MANUAL"
        return False

    def start(self):
        """Inicia el proceso de instalación"""
        if self.state != "WAIT":
            return
            
        # Notificar al avatar
        if self.avatar:
            self.avatar.show("⚙️ Iniciando instalación... Analizando archivos...")
        
        # Modo manual: solicitar ruta al usuario
        if self.mode == "MANUAL":
            try:
                # Crear ventana Tkinter oculta para diálogo de selección
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)  # Mantener sobre otras ventanas
                
                # Diálogo para seleccionar carpeta
                selected_folder = filedialog.askdirectory(
                    initialdir="C:/", 
                    title="Selecciona la carpeta del juego"
                )
                
                root.destroy()  # Cerrar ventana Tkinter
                
                if not selected_folder:
                    # Usuario canceló
                    self.status_text = "SELECCIONAR RUTA"
                    if self.avatar:
                        self.avatar.hide()
                    return
                    
                self.detected_path = selected_folder
                
            except Exception as e:
                # Error en interfaz gráfica
                self.status_text = "ERROR UI"
                if self.avatar:
                    self.avatar.hide()
                return
        
        # Cambiar a estado de trabajo y comenzar en hilo separado
        self.state = "WORK"
        self.start_time = time.time()
        
        # Ejecutar extracción en hilo separado para no bloquear interfaz
        threading.Thread(target=self._run_extract, daemon=True).start()

    def _run_extract(self):
        """
        Ejecuta la extracción real de archivos (en hilo separado)
        Incluye búsqueda de archivo, extracción y post-procesamiento
        """
        dest_folder = self.detected_path
        
        # Validar ruta de destino
        if not dest_folder or not os.path.exists(dest_folder):
            self.state = "WAIT"
            self.status_text = "RUTA INVALIDA"
            
            if self.avatar:
                self.avatar.set_immediate_bark("❌ Ruta inválida.")
                time.sleep(2.0)
                self.avatar.hide()
                
            return
        
        # ====================================================================
        # BUSCAR ARCHIVO COMPRIMIDO
        # ====================================================================
        archive_found = None
        archive_formats = ["packed.dat", "packed.zip", "packed.rar"]
        
        for archive_name in archive_formats:
            check_path = resource_path(archive_name)
            
            if os.path.exists(check_path):
                archive_found = check_path
                break
        
        # Error si no se encuentra archivo
        if not archive_found:
            self.state = "WAIT"
            self.status_text = "ERROR: NO ARCHIVE"
            
            if self.avatar:
                self.avatar.set_immediate_bark("⚠️ No encuentro los archivos.")
                time.sleep(2.0)
                self.avatar.hide()
                
            return
        
        try:
            # ================================================================
            # EXTRACCIÓN DE ARCHIVOS
            # ================================================================
            if archive_found.endswith(".dat") or archive_found.endswith(".zip"):
                # Extraer ZIP/DAT
                with zipfile.ZipFile(archive_found) as zip_file:
                    file_list = zip_file.infolist()
                    total_files = len(file_list)
                    
                    for i, file_info in enumerate(file_list):
                        zip_file.extract(file_info, dest_folder)
                        
                        # Actualizar progreso
                        self.real_progress = (i + 1) / total_files
                        
                        # Pequeña pausa para archivos pequeños (mejor UX)
                        if total_files < 20:
                            time.sleep(0.05)
                            
            elif archive_found.endswith(".rar"):
                # Extraer RAR (requiere librería rarfile)
                try:
                    import rarfile
                    
                    with rarfile.RarFile(archive_found) as rar_file:
                        file_list = rar_file.infolist()
                        total_files = len(file_list)
                        
                        for i, file_info in enumerate(file_list):
                            rar_file.extract(file_info, dest_folder)
                            self.real_progress = (i + 1) / total_files
                            
                except Exception as rar_error:
                    self.state = "WAIT"
                    self.status_text = "ERROR RAR"
                    return
            
            # ================================================================
            # POST-INSTALACIÓN: PARCHE CRC (MEJORADO)
            # ================================================================
            if GAME_CONFIG.get("POST_INSTALL", {}).get("ENABLED", False):
                self.status_text = "BUSCANDO ARCHIVO PARA PARCHEAR..."
                time.sleep(1.0)  # Breve pausa para UX
                
                # 1. BÚSQUEDA RECURSIVA PROFUNDA
                target_file_name = GAME_CONFIG["POST_INSTALL"]["TARGET_FILE"]
                target_full_path = None
                found_paths = []
                
                # Búsqueda exhaustiva en TODOS los subdirectorios
                for root, dirs, files in os.walk(dest_folder):
                    if target_file_name in files:
                        full_path = os.path.join(root, target_file_name)
                        found_paths.append(full_path)
                
                # Si encontramos múltiples, elegir el más específico
                if found_paths:
                    # Ordenar por longitud de ruta (más larga = más específica)
                    found_paths.sort(key=len, reverse=True)
                    target_full_path = found_paths[0]
                    
                    # Debug: mostrar resultados
                    print(f"[PARCHE] Encontrados {len(found_paths)} archivos {target_file_name}")
                    print(f"[PARCHE] Usando: {target_full_path}")
                
                # 2. APLICAR PARCHE SI SE ENCONTRÓ ARCHIVO
                if target_full_path:
                    patcher_exe = resource_path(GAME_CONFIG["POST_INSTALL"]["PATCHER_EXE"])
                    
                    if os.path.exists(patcher_exe):
                        self.status_text = "APLICANDO PARCHE..."
                        patch_argument = GAME_CONFIG["POST_INSTALL"]["ARGUMENT"]
                        
                        # Configurar para ocultar ventana de consola (Windows)
                        startup_info = None
                        if os.name == "nt":
                            startup_info = subprocess.STARTUPINFO()
                            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            startup_info.wShowWindow = subprocess.SW_HIDE
                        
                        # Ejecutar parcheador
                        print(f"[PARCHE] Ejecutando: {patcher_exe} {patch_argument} \"{target_full_path}\"")
                        
                        result = subprocess.run(
                            [patcher_exe, patch_argument, target_full_path],
                            startupinfo=startup_info,
                            capture_output=True,
                            text=True
                        )
                        
                        # Verificar resultado
                        if result.returncode == 0:
                            self.status_text = "✅ PARCHE APLICADO"
                            
                            if self.avatar:
                                self.avatar.set_immediate_bark("🎉 ¡Parche aplicado!")
                                
                            print(f"[PARCHE] Parche aplicado exitosamente")
                        else:
                            self.status_text = "ERROR EN PARCHE"
                            
                            if self.avatar:
                                self.avatar.set_immediate_bark("⚠️ Error al aplicar parche")
                                
                            print(f"[PARCHE] Error: {result.stderr}")
                        
                        time.sleep(2.0)  # Pausa para leer mensaje
                        
                    else:
                        self.status_text = "PARCHER NO ENCONTRADO"
                        
                        if self.avatar:
                            self.avatar.set_immediate_bark("⚠️ No encuentro el .exe del parcheador.")
                            
                        print(f"[PARCHE] No se encontró: {patcher_exe}")
                        
                else:
                    self.status_text = "ARCHIVO NO ENCONTRADO"
                    error_msg = f"⚠️ No encontré {target_file_name} en {dest_folder}"
                    
                    if self.avatar:
                        self.avatar.set_immediate_bark(error_msg)
                        
                    print(f"[PARCHE] {error_msg}")
                    
                    # Debug: listar contenido para diagnóstico
                    try:
                        print(f"[PARCHE] Contenido de {dest_folder}:")
                        for item in os.listdir(dest_folder)[:10]:  # Primeros 10 elementos
                            print(f"  - {item}")
                    except Exception:
                        pass
                    
                    time.sleep(2.0)
            
            # ================================================================
            # FINALIZACIÓN EXITOSA
            # ================================================================
            if self.avatar:
                self.avatar.set_immediate_bark("✅ ¡Instalación completada!")
                
                # Efecto de teclado disco (en hilo separado)
                if self.key_fx:
                    threading.Thread(
                        target=lambda: self.key_fx.disco_mode(4.0),
                        daemon=True
                    ).start()
                
                time.sleep(3.0)
                self.avatar.hide()
                
        except Exception as e:
            # ERROR GENERAL
            self.state = "WAIT"
            self.status_text = "ERROR GENERICO"
            
            if self.avatar:
                error_message = f"💥 Error: {str(e)[:30]}..."  # Limitar longitud
                self.avatar.set_immediate_bark(error_message)
                time.sleep(2.0)
                self.avatar.hide()

    def update(self):
        """
        Actualiza estado del instalador (debe llamarse cada frame)
        Maneja animaciones, transiciones y efectos de sonido
        """
        # ====================================================================
        # ESTADO: TRABAJANDO (extracción en progreso)
        # ====================================================================
        if self.state == "WORK":
            elapsed = time.time() - self.start_time
            
            # Progreso falso para animación (más rápido que el real)
            fake_target = min(1.0, elapsed / 4.0)
            
            # Progreso real limitado por extracción
            target = min(self.real_progress, fake_target)
            
            # Suavizar progreso visual (animación)
            self.visual_progress += (target - self.visual_progress) * 0.1
            
            # Efecto de "overshoot" cuando termina
            if self.real_progress >= 1.0:
                self.visual_progress += 0.01
            
            # Actualizar texto de progreso
            self.status_text = f"PROGRESO {int(self.visual_progress * 100)}%"
            
            # Transición a siguiente estado cuando termina
            if self.visual_progress >= 0.99:
                self.state = "ARMING"
                self.armed_time = time.time()
                self.status_text = "⚠ SYSTEMS ARMED ⚠"
        
        # ====================================================================
        # ESTADO: ARMING (sistemas armados - pre-explosión)
        # ====================================================================
        elif self.state == "ARMING":
            # Reproducir voz "Systems Armed" (una sola vez)
            if not self.voice_triggered:
                self.voice_triggered = True
                
                AudioManager.play_robotic(
                    AudioManager.generate_voice("Systems Armed. Weapons Deployed.", 
                                              "temp_armed.wav")
                )
            
            # Esperar 2 segundos antes de targeting
            if time.time() - self.armed_time > 2.0:
                self.state = "TARGETING"
                self.targeting_time = time.time()
                self.status_text = "ACQUIRING TARGET..."
        
        # ====================================================================
        # ESTADO: TARGETING (adquiriendo objetivo - efectos visuales)
        # ====================================================================
        elif self.state == "TARGETING":
            elapsed = time.time() - self.targeting_time
            
            # Voz "Target Locked" después de 2.4 segundos
            if elapsed > 2.4 and not self.locked_voice_played:
                self.locked_voice_played = True
                
                AudioManager.play_robotic(
                    AudioManager.generate_voice("Target Locked.", "temp_locked.wav"),
                    base_channel=1
                )
            
            # Voz "Firing" después de 3.8 segundos
            if elapsed > 3.8 and not self.firing_voice_played:
                self.firing_voice_played = True
                
                AudioManager.play_robotic(
                    AudioManager.generate_voice("Firing.", "temp_firing.wav"),
                    base_channel=3
                )
            
            # Transición a estado final después de 4 segundos
            if elapsed > 4.0:
                self.state = "FIRED"
                
                # Ocultar avatar si está visible
                if self.avatar and (self.avatar.visible or self.avatar.fade_alpha > 0):
                    self.avatar.hide()