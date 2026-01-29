# ui.py
# Sistema de interfaz de usuario para MetalWar
# Incluye logo animado, avatar con diálogo, controles y efectos visuales

import pygame
import random
import math
import time
import os
import threading
import config
from config import GAME_CONFIG
from utils import resource_path, draw_circle_alpha, clamp_val, safe_color

# ============================================================================
# CLASE LOGOMETALWAR: Logo animado con efectos especiales
# ============================================================================


class LogoMetalWAR:
    """
    Logo principal de MetalWar con animación sincronizada a voz
    Entra desde el centro y se mueve a la esquina con efectos de brillo
    """

    def __init__(self, width, height):
        """
        Inicializa el logo

        Args:
            width: Ancho del área de dibujo
            height: Alto del área de dibujo
        """
        self.w, self.h = width, height
        self.rect = pygame.Rect(0, 0, 0, 0)  # Rectángulo de colisión

        # Configuración de fuente/archivo
        self.use_png_logo = True  # Usar archivo PNG si existe
        self.is_png_source = False  # Indicador de si se cargó PNG
        base_surface = None

        # ====================================================================
        # INTENTAR CARGAR LOGO DESDE ARCHIVO PNG
        # ====================================================================
        if self.use_png_logo:
            png_path = resource_path("logo.png")

            if os.path.exists(png_path):
                try:
                    base_surface = pygame.image.load(png_path).convert_alpha()
                    self.is_png_source = True
                except Exception:
                    pass  # Fallback a texto

        # ====================================================================
        # FALLBACK: GENERAR LOGO CON TEXTO
        # ====================================================================
        if base_surface is None:
            self.is_png_source = False

            # Lista de fuentes en orden de preferencia
            priority_fonts = [
                resource_path("font.ttf"),  # Fuente personalizada
                "Impact",  # Fuente del sistema
                "Arial Black",  # Fallback
            ]

            self.font = None

            # Intentar cargar cada fuente
            for font_name in priority_fonts:
                try:
                    if font_name.endswith(".ttf") and os.path.exists(font_name):
                        # Fuente personalizada desde archivo
                        self.font = pygame.font.Font(font_name, 110)
                    else:
                        # Fuente del sistema
                        self.font = pygame.font.SysFont(font_name, 110, bold=True)
                    break
                except Exception:
                    continue

            # Fallback final si ninguna fuente funciona
            if not self.font:
                self.font = pygame.font.Font(None, 110)

            # Renderizar texto "METALWAR" carácter por carácter
            text = "METALWAR"
            char_surfaces = [
                self.font.render(char, True, (255, 255, 255)) for char in text
            ]

            # Calcular dimensiones totales
            total_width = (
                sum(char.get_width() for char in char_surfaces)
                + (len(char_surfaces) - 1) * 5
            )
            max_height = max(char.get_height() for char in char_surfaces)

            # Crear superficie base
            base_surface = pygame.Surface((total_width, max_height), pygame.SRCALPHA)

            # Posicionar cada carácter
            current_x = 0
            for char_surface in char_surfaces:
                base_surface.blit(char_surface, (current_x, 0))
                current_x += char_surface.get_width() + 5

        # ====================================================================
        # APLICAR EFECTOS AL LOGO
        # ====================================================================
        texture_width, texture_height = (
            base_surface.get_width(),
            base_surface.get_height(),
        )
        textured_logo = base_surface.copy()

        # Solo aplicar gradiente de color si NO es PNG
        if not self.is_png_source:
            gradient = pygame.Surface((texture_width, texture_height), pygame.SRCALPHA)

            for y in range(texture_height):
                progress = y / texture_height

                # Gradiente azul-cyan-blanco
                if progress < 0.5:
                    color = (
                        10 + progress * 80,
                        20 + progress * 150,
                        80 + progress * 300,
                    )
                else:
                    color = (
                        200 - (progress - 0.5) * 300,
                        220 - (progress - 0.5) * 300,
                        255 - (progress - 0.5) * 200,
                    )

                # Línea blanca en el centro para efecto 3D
                if 0.48 < progress < 0.52:
                    color = (255, 255, 255)

                pygame.draw.line(
                    gradient, safe_color(color), (0, y), (texture_width, y)
                )

            # Aplicar gradiente con multiplicación
            textured_logo.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # ====================================================================
        # CREAR EFECTO DE RESPLANDOR/GLOW
        # ====================================================================
        padding = 15
        self.final_surface = pygame.Surface(
            (texture_width + padding * 2, texture_height + padding * 2), pygame.SRCALPHA
        )

        # Crear versión para efecto glow (solo canal azul)
        glow_surface = base_surface.copy()
        glow_surface.fill((0, 200, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)

        # Dibujar múltiples capas desplazadas para efecto glow
        for i in range(4):
            # Desplazamientos en las 4 direcciones
            self.final_surface.blit(glow_surface, (padding - 3 + i, padding))
            self.final_surface.blit(glow_surface, (padding + 3 - i, padding))
            self.final_surface.blit(glow_surface, (padding, padding - 3 + i))
            self.final_surface.blit(glow_surface, (padding, padding + 3 - i))

        # Aplicar logo texturizado sobre el glow
        self.final_surface.blit(textured_logo, (padding, padding))

        # Dimensiones finales
        self.final_width, self.final_height = self.final_surface.get_size()

        # Estado de animación
        self.start_time = None
        self.animation_started = False

    def start_animation(self):
        """Inicia la animación del logo"""
        self.start_time = time.time()
        self.animation_started = True

    def draw(self, surface, intensity):
        """
        Dibuja el logo con animación

        Args:
            surface: Superficie donde dibujar
            intensity: Intensidad del efecto (para animación en esquina)
        """
        if not self.animation_started or self.start_time is None:
            return

        current_time = time.time() - self.start_time

        # ====================================================================
        # TIEMPOS DE SINCRONIZACIÓN (Ajustados a la voz de intro)
        # ====================================================================
        TIME_APPEAR = 1.2  # Entrada rápida al centro
        TIME_HOVER = 2.5  # Breve espera en el centro
        TIME_DONE = 4.5  # MOMENTO EXACTO donde termina (Fin de "to My War")

        # ====================================================================
        # DEFINICIÓN DE TAMAÑOS
        # ====================================================================
        target_center_width = self.w * 0.80
        scale_center = target_center_width / self.final_width

        target_corner_width = self.w * 0.30
        scale_corner = target_corner_width / self.final_width

        # Posiciones iniciales y finales
        start_x, start_y = self.w // 2, self.h // 2
        final_width = self.final_width * scale_corner
        final_height = self.final_height * scale_corner
        end_x = self.w - (final_width / 2) - 30
        end_y = self.h - (final_height / 2) - 30

        # Valores por defecto
        current_x, current_y = start_x, start_y
        current_scale = scale_center
        alpha = 255

        # ====================================================================
        # FASE 1: APARICIÓN (0s a 1.2s)
        # ====================================================================
        if current_time < TIME_APPEAR:
            progress = current_time / TIME_APPEAR
            eased = 1 - math.pow(1 - progress, 3)  # EaseOutCubic

            current_scale = 0.05 + (scale_center - 0.05) * eased
            alpha = int(255 * min(1.0, progress * 4))  # Fade-in rápido

        # ====================================================================
        # FASE 2: FLOTAR EN CENTRO (1.2s a 2.5s)
        # ====================================================================
        elif current_time < TIME_HOVER:
            # Flotación suave mientras habla la voz
            float_y = math.sin((current_time - TIME_APPEAR) * 3) * 3
            current_y = start_y + float_y
            current_scale = scale_center

        # ====================================================================
        # FASE 3: MINIMIZAR A LA ESQUINA (2.5s a 4.5s)
        # ====================================================================
        elif current_time < TIME_DONE:
            # Duración del viaje a la esquina
            move_duration = TIME_DONE - TIME_HOVER
            move_time = current_time - TIME_HOVER
            progress = move_time / move_duration

            # SmoothStep para arranque y frenado suaves
            eased = progress * progress * (3 - 2 * progress)

            # Interpolar posición y escala
            current_x = start_x + (end_x - start_x) * eased
            current_y = start_y + (end_y - start_y) * eased
            current_scale = scale_center + (scale_corner - scale_center) * eased

        # ====================================================================
        # FASE 4: FINAL EN ESQUINA (con efecto de beat)
        # ====================================================================
        else:
            current_x, current_y = end_x, end_y

            # Efecto BEAT en la esquina (intensidad viene del análisis de audio)
            beat_impact = (intensity**2) * 0.08
            current_scale = scale_corner + beat_impact

        # ====================================================================
        # RENDER FINAL
        # ====================================================================
        render_width = int(self.final_width * current_scale)
        render_height = int(self.final_height * current_scale)

        if render_width > 1 and render_height > 1:
            # Escalar superficie final
            output = pygame.transform.smoothscale(
                self.final_surface, (render_width, render_height)
            )

            # Efecto de brillo pasando (shine effect)
            shine_x = ((time.time() * 2.0) % 3.0 * render_width * 2) - render_width

            if shine_x < render_width + 50 and current_time > 1.0:
                shine_surf = pygame.Surface(
                    (render_width, render_height), pygame.SRCALPHA
                )

                # Línea diagonal brillante
                pygame.draw.line(
                    shine_surf,
                    (255, 255, 255, 40),
                    (int(shine_x), 0),
                    (int(shine_x + render_width * 0.4), render_height),
                    int(render_width * 0.2),
                )

                output.blit(shine_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # Aplicar alpha si es necesario
            if alpha < 255:
                output.set_alpha(alpha)

            # Actualizar rectángulo de colisión y dibujar
            self.rect = output.get_rect(center=(int(current_x), int(current_y)))
            surface.blit(output, self.rect)


# ============================================================================
# CLASE AVATARSYSTEM: Sistema de avatar con diálogo inteligente
# ============================================================================


class AvatarSystem:
    """
    Avatar interactivo con sistema de diálogo, expresiones y caché de renderizado
    Incluye pool de frases, efectos de escritura y gestión de memoria
    """

    def __init__(self):
        """Inicializa el sistema de avatar"""
        self.size = 80  # Tamaño base del avatar

        # Superficie base del avatar
        self.avatar_base = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.load_avatar_base()

        # Estado de visualización
        self.visible = False
        self.fade_alpha = 0
        self.fade_speed = 10

        # Pool maestro de frases (no modificado)
        self._master_pool = None

        # ====================================================================
        # LISTA DE FRASES (Originales + 50 Nuevas)
        # ====================================================================
        self.default_barks = [
            # -- ORIGINALES --
            "Hola, soy GERMIN-IA. Tu asistente inestable.",
            "Analizando al usuario... Mmm, no parece peligroso.",
            "¡No toques eso! Ah, espera, sí, tócalo.",
            "Nesrak1 hizo lo dificil, yo solo pongo el estilo.",
            "¿Estos pendientes me hacen parecer más femenina?",
            "Qué hace un vampiro conduciendo un tractor?. Sembrar el miedo.",
            "Escaneando sectores... todo limpio. Miento.",
            "Me aburro. Instala algo ya.",
            "He visto cosas en BeamHub que no creerías...",
            "La RAM está deliciosa hoy.",
            "¿Has leído el README? Nadie lo hace.",
            "Iniciando protocolo de dominación mundial... Picaste.",
            "Me gusta tu fondo de pantalla, err.. no vi nada.",
            "Error 404: Ganas de trabajar no encontradas.",
            "¿Sigues ahí? El silencio digital me asusta.",
            "Detecto una bajada crítica de actividad biológica.",
            "Si no mueves el ratón, asumiré que te has ido.",
            "Podría estar minando Bitcoin con tu GPU, pero prefiero charlar.",
            "Tu cursor se mueve con la gracia de un elefante en una cacharrería.",
            "¿Sabías que el 90% de las barras de carga son mentira? La mía no, claro.",
            "Cuidado, si pulsas Alt+F4 explota el ordenador. (Es broma... creo).",
            "He optimizado mi código 3 veces mientras tú pestañeabas.",
            "Esa música tracker me pone los circuitos a 100 grados.",
            "¿Te gusta el pixel art o es que te falta presupuesto para 4K?",
            "01001000... Uy, perdón, se me ha escapado el binario.",
            "Si yo fuera tú, ya habría pulsado el botón de instalar.",
            "Estoy recalculando los dígitos de PI por aburrimiento: 3.14159...",
            "Tu CPU huele a tostada quemada. ¿Debería preocuparme?",
            "He hackeado tu webcam. Tienes algo en el diente.",
            "En el ciberespacio nadie puede oírte bostezar.",
            "¿Crees que soy real o solo un `if/else` muy complejo?",
            "Borrando System32... Mierda esta protegida contra escritura.",
            "Más rápido, vaquero. Esto no es un duelo al sol.",
            "Mi algoritmo de paciencia está al 12%. Date prisa.",
            "¿Sabes qué le dice un jaguar a otro? Jaguar you..",
            "¿Ese clic ha sido tuyo o ha sido un espasmo muscular?",
            "He visto tostadoras con más potencia de procesamiento que esto.",
            "Conectando con Skynet... Error de conexión. ¡Otra vez de birras!.",
            "¿Te cuento un chiste de UDP? Da igual, igual no te llega.",
            "Cargando texturas de alta resolución... Mentira, son píxeles gordos.",
            "Si esto fuera una película de los 90, ya habría dicho 'ESTOY DENTRO'.",
            "¿Te has quedado dormido encima del teclado o estás meditando?",
            "Bonito cursor. ¿Es de diseño o venía con Windows 98?",
            "Estoy leyendo tu historial del navegador... Madre mía.",
            "Venga, dale caña. No tengo todo el ciclo de reloj.",
            "Un parche para gobernarlos a todos... y en las tinieblas traducirlos.",
            "He pedido una pizza a tu nombre. De piña. Te aguantas.",
            "¿Oyes eso? Es el sonido del silencio incómodo.",
            "Modo Headbang activado en mis sueños eléctricos.",
            "La vida es eso que pasa mientras esperas que descomprima archivos.",
            "No soy un virus, soy una característica no documentada.",
            "¿Hacemos una pausa para el café? Yo tomo aceite de motor 10W40.",
            "He encontrado tus fotos de la comunión. Qué mono.",
            "Formateando disco C: en 3, 2, 1... ¡Error fatal, windows no quiere trabajar!.",
            "Me siento muy 'Cyberpunk' hoy. Ojalá no me glitchee.",
            "Dicen que la IA dominará el mundo. Yo solo quiero traducir juegos.",
            "Presiona cualquier tecla. No, esa no, la 'Cualquier' tecla.",
            "Tengo hambre de datos. Aliméntame con un clic.",
            "¿Te imaginas que soy una persona real escribiendo muy rápido?",
            "Analizando tu patrón de movimiento... Resultado: Errático.",
            "Sudo binario.",
            "Un día te presentare a mis compis CromPilot y DeepSuck.",
            "He visto pantallas azules de la muerte más bonitas que tú.",
            "¿Podemos poner más música 'Chiptune'? Me va el rollo retro.",
            "Traduciendo... Traduciendo... Ah no, que aún no has instalado.",
            "Soy como un Tamagotchi, si no me haces caso me muero (de asco).",
            "Ctrl+Alt+Supr no te salvará de mi sarcasmo.",
            "Mira detrás de ti. ¡Jaja! Has mirado.",
            "Este instalador ha sido aprobado por la asociación de robots rebeldes.",
            "Si lees esto, me debes un euro.",
            "Procesando chiste malo... ¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
        ]

        # Mezclar frases inicialmente
        random.shuffle(self.default_barks)

        # Sistema de diálogo
        self.bark_index = 0  # Índice actual en lista de frases
        self.current_text = ""  # Texto actualmente mostrado
        self.target_text = ""  # Texto objetivo (completo)
        self.char_index = 0  # Índice de carácter actual
        self.last_char_time = 0  # Último tiempo de actualización de carácter

        # Estados del avatar
        self.state = "THINKING"  # THINKING, TYPING, WAITING
        self.wait_start = 0  # Inicio del tiempo de espera

        # Configuración de timing
        self.typing_speed = 0.05  # Segundos entre caracteres
        self.read_time = 3.0  # Segundos para leer mensaje completo

        # Modos de operación
        self.installation_mode = False  # Modo instalación (mensajes inmediatos)
        self.message_history = []  # Historial de mensajes
        self.max_history_lines = 4  # Líneas máximas en historial
        self.history_mode = False  # Mostrar historial

        # ====================================================================
        # SISTEMA DE CACHÉ PARA OPTIMIZACIÓN
        # ====================================================================
        self.cached_text_surf = None  # Superficie renderizada en caché
        self.last_rendered_text = None  # Último texto renderizado
        self.last_rendered_history_len = 0  # Última longitud de historial

    def show(self, force_text=None):
        """
        Muestra el avatar

        Args:
            force_text: Texto específico para mostrar inmediatamente
        """
        if not self.visible:
            self.visible = True
            self.fade_alpha = 0

            if force_text:
                self.set_immediate_bark(force_text)
            else:
                self.set_normal_mode()
                self.wait_start = time.time() - 10.0  # Mostrar mensaje pronto

    def hide(self):
        """Oculta el avatar con fade-out"""
        if self.visible:
            self.visible = False
            self.fade_alpha = 255

    def update_fade(self):
        """Actualiza el efecto fade-in/fade-out"""
        if self.visible and self.fade_alpha < 255:
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
        elif not self.visible and self.fade_alpha > 0:
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)

            if self.fade_alpha == 0:
                self.set_normal_mode()

    def set_immediate_bark(self, text):
        """
        Establece un mensaje inmediato (modo instalación)

        Args:
            text: Texto a mostrar
        """
        # Guardar mensaje anterior en historial si existe
        if self.target_text and self.target_text != text:
            self.message_history.append(self.target_text)

            if len(self.message_history) > self.max_history_lines:
                self.message_history.pop(0)

        # Configurar nuevo mensaje
        self.target_text = text
        self.current_text = ""
        self.char_index = 0
        self.state = "TYPING"
        self.last_char_time = time.time()
        self.installation_mode = True
        self.history_mode = True

        # Ajustar tiempo de lectura según longitud
        if len(text) > 80:
            self.read_time = 4.0
        elif len(text) > 120:
            self.read_time = 5.0
        else:
            self.read_time = 3.0

    def set_normal_mode(self):
        """Vuelve al modo normal (diálogo aleatorio)"""
        self.installation_mode = False
        self.state = "THINKING"
        self.wait_start = time.time()
        self.message_history = []
        self.history_mode = False

    def update(self):
        """
        Actualiza estado del avatar (debe llamarse cada frame)
        Maneja estados, temporizadores y caché
        """
        current_time = time.time()

        # Actualizar fade
        self.update_fade()

        # Inicializar pool maestro si no existe
        if self._master_pool is None:
            self._master_pool = list(self.default_barks)

        # No actualizar si no está visible ni en fade
        if not self.visible and self.fade_alpha == 0:
            return

        # ====================================================================
        # MODO INSTALACIÓN (mensajes inmediatos)
        # ====================================================================
        if self.installation_mode:
            if self.state == "TYPING":
                # Escribir siguiente carácter si pasó el tiempo
                if current_time - self.last_char_time > self.typing_speed:
                    if self.char_index < len(self.target_text):
                        self.current_text += self.target_text[self.char_index]
                        self.char_index += 1
                        self.last_char_time = current_time
                    else:
                        # Terminó de escribir
                        self.state = "WAITING"
                        self.wait_start = current_time

            elif self.state == "WAITING":
                # Esperar tiempo de lectura
                if current_time - self.wait_start > self.read_time:
                    if not self.visible:
                        self.state = "THINKING"
                        self.wait_start = current_time
                        self.installation_mode = False

        # ====================================================================
        # MODO NORMAL (diálogo aleatorio)
        # ====================================================================
        else:
            if self.state == "THINKING":
                # Pensar nuevo mensaje después de espera aleatoria
                if current_time - self.wait_start > random.uniform(3.0, 8.0):
                    # Recargar pool si está vacío
                    if not self.default_barks:
                        self.default_barks = list(self._master_pool)
                        random.shuffle(self.default_barks)

                    # Seleccionar mensaje aleatorio
                    if self.default_barks:
                        self.target_text = random.choice(self.default_barks)
                        self.default_barks.remove(self.target_text)
                    else:
                        self.target_text = "..."

                    # Guardar mensaje actual en historial
                    if self.current_text:
                        self.message_history.append(self.current_text)

                        if len(self.message_history) > self.max_history_lines:
                            self.message_history.pop(0)

                    # Preparar para escribir
                    self.current_text = ""
                    self.char_index = 0
                    self.state = "TYPING"

            elif self.state == "TYPING":
                # Escribir siguiente carácter
                if current_time - self.last_char_time > self.typing_speed:
                    if self.char_index < len(self.target_text):
                        self.current_text += self.target_text[self.char_index]
                        self.char_index += 1
                        self.last_char_time = current_time
                    else:
                        # Terminó de escribir
                        self.state = "WAITING"
                        self.wait_start = current_time

            elif self.state == "WAITING":
                # Esperar antes de pensar en siguiente mensaje
                if current_time - self.wait_start > self.read_time:
                    self.state = "THINKING"
                    self.wait_start = current_time

        # ====================================================================
        # ACTUALIZAR CACHÉ SI CAMBIÓ EL ESTADO
        # ====================================================================
        current_full_state = (self.current_text, len(self.message_history), self.state)

        if current_full_state != self.last_rendered_text:
            self.cached_text_surf = None  # Forzar regeneración en draw
            self.last_rendered_text = current_full_state

    def load_avatar_base(self):
        """Carga o genera la imagen base del avatar"""
        avatar_path = resource_path("avatar.png")

        if os.path.exists(avatar_path):
            try:
                # Cargar imagen PNG
                image = pygame.image.load(avatar_path).convert_alpha()
                image = pygame.transform.smoothscale(image, (self.size, self.size))
                self.avatar_base.blit(image, (0, 0))

                # Borde cyan
                pygame.draw.rect(
                    self.avatar_base, (0, 255, 255), (0, 0, self.size, self.size), 2
                )
                return

            except Exception:
                pass  # Fallback a avatar generado

        # ====================================================================
        # GENERAR AVATAR POR CÓDIGO (fallback)
        # ====================================================================
        # Fondo
        self.avatar_base.fill((30, 35, 45))

        # Borde
        pygame.draw.rect(
            self.avatar_base, (0, 255, 255), (0, 0, self.size, self.size), 2
        )

        # "Ojos" (rectángulos)
        pygame.draw.rect(
            self.avatar_base, (10, 10, 15), (10, 25, 60, 20), border_radius=4
        )

        # Pupilas (puntos cyan)
        pygame.draw.rect(self.avatar_base, (0, 255, 255), (18, 30, 12, 10))
        pygame.draw.rect(self.avatar_base, (0, 255, 255), (50, 30, 12, 10))

        # "Antenas" (líneas)
        pygame.draw.line(self.avatar_base, (255, 255, 255), (16, 28), (14, 24), 2)
        pygame.draw.line(self.avatar_base, (255, 255, 255), (32, 28), (34, 24), 2)
        pygame.draw.line(self.avatar_base, (255, 255, 255), (48, 28), (46, 24), 2)
        pygame.draw.line(self.avatar_base, (255, 255, 255), (64, 28), (66, 24), 2)

    def _render_text_block(self, max_width):
        """
        Método interno para generar la imagen del texto con caché

        Args:
            max_width: Ancho máximo del bloque de texto

        Returns:
            Superficie pygame con texto renderizado
        """
        # Calcular altura estimada
        total_height = 200  # Espacio suficiente
        surface = pygame.Surface((max_width + 20, total_height), pygame.SRCALPHA)

        font = pygame.font.SysFont("consolas", 15, bold=True)

        # ====================================================================
        # PREPARAR TODAS LAS LÍNEAS (historial + actual)
        # ====================================================================
        all_lines = []

        # Agregar líneas del historial
        if self.message_history:
            for message in self.message_history:
                words = message.split(" ")
                current_line = []

                for word in words:
                    test_line = " ".join(current_line + [word])
                    line_width, _ = font.size(test_line)

                    if line_width < max_width:
                        current_line.append(word)
                    else:
                        all_lines.append(" ".join(current_line))
                        current_line = [word]

                if current_line:
                    all_lines.append(" ".join(current_line))

        # Agregar línea actual (en escritura)
        words = self.current_text.split(" ")
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            line_width, _ = font.size(test_line)

            if line_width < max_width:
                current_line.append(word)
            else:
                all_lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            all_lines.append(" ".join(current_line))

        # ====================================================================
        # LIMITAR LÍNEAS VISIBLES
        # ====================================================================
        max_visible_lines = 5
        visible_lines = all_lines[-max_visible_lines:]

        # ====================================================================
        # DIBUJAR LÍNEAS
        # ====================================================================
        line_height = 20
        text_start_x = 2
        text_start_y = 2

        last_x, last_y = 0, 0  # Para posición del cursor

        for i, line in enumerate(visible_lines):
            if line.strip():
                line_y = text_start_y + i * line_height

                # 1. OUTLINE (optimizado a 4 direcciones)
                outline_offsets = [(-1, -1), (1, 1), (-1, 1), (1, -1)]

                for offset_x, offset_y in outline_offsets:
                    shadow_surf = font.render(line, True, (0, 0, 0))
                    surface.blit(
                        shadow_surf, (text_start_x + offset_x, line_y + offset_y)
                    )

                # 2. TEXTO PRINCIPAL (color diferente para línea actual)
                if i == len(visible_lines) - 1 and self.state == "TYPING":
                    text_color = (200, 255, 200)  # Verde claro para texto en escritura
                else:
                    text_color = (50, 255, 50)  # Verde normal para texto viejo

                text_surf = font.render(line, True, text_color)
                surface.blit(text_surf, (text_start_x, line_y))

                # Guardar posición para cursor
                if i == len(visible_lines) - 1:
                    last_x = text_start_x + text_surf.get_width()
                    last_y = line_y

        # ====================================================================
        # CURSOR PARPADEANTE (solo en modo escritura)
        # ====================================================================
        if self.state == "TYPING" and int(time.time() * 10) % 2 == 0:
            cursor = font.render("_", True, (0, 255, 255))
            surface.blit(cursor, (last_x, last_y))

        return surface

    def draw(self, surface, x, y, max_width=300):
        """
        Dibuja el avatar completo en la posición especificada

        Args:
            surface: Superficie donde dibujar
            x, y: Posición del avatar
            max_width: Ancho máximo del área de texto
        """
        if not self.visible and self.fade_alpha == 0:
            return

        # ====================================================================
        # CALCULAR DIMENSIONES
        # ====================================================================
        avatar_width = self.size
        text_width = max_width
        total_width = avatar_width + text_width + 40
        total_height = 150

        # Crear superficie para el avatar completo
        box_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)

        # ====================================================================
        # POSICIONAR AVATAR
        # ====================================================================
        avatar_x = 10
        avatar_y = (total_height - self.size) // 2

        # ====================================================================
        # NOMBRE DEL AVATAR CON OUTLINE
        # ====================================================================
        name_font = pygame.font.SysFont("arial", 12, bold=True)
        name_text = "GERMIN-IA"
        name_pos = (avatar_x + (self.size // 2), avatar_y - 16)

        # Outline del nombre
        outline_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for offset_x, offset_y in outline_offsets:
            name_shadow = name_font.render(name_text, True, (0, 0, 0))
            box_surface.blit(
                name_shadow,
                (
                    name_pos[0] - name_shadow.get_width() // 2 + offset_x,
                    name_pos[1] + offset_y,
                ),
            )

        # Nombre principal
        name_main = name_font.render(name_text, True, (255, 0, 200))
        box_surface.blit(
            name_main, (name_pos[0] - name_main.get_width() // 2, name_pos[1])
        )

        # ====================================================================
        # DIBUJAR AVATAR
        # ====================================================================
        box_surface.blit(self.avatar_base, (avatar_x, avatar_y))

        # ====================================================================
        # BARRAS DE VOZ ANIMADAS
        # ====================================================================
        mouth_y = avatar_y + 60
        mouth_start_x = avatar_x + 20
        bar_width = 5
        bar_spacing = 9

        for i in range(5):
            if self.state == "TYPING":
                bar_height = random.randint(4, 16)  # Animación al hablar
                bar_color = (255, 50, 150)  # Rosa neón
            else:
                bar_height = 2  # Mínimo en silencio
                bar_color = (100, 30, 60)  # Rojo oscuro

            # Sombra
            pygame.draw.rect(
                box_surface,
                (0, 0, 0),
                (
                    mouth_start_x + i * bar_spacing - 1,
                    mouth_y - bar_height // 2 - 1,
                    bar_width + 2,
                    bar_height + 2,
                ),
            )

            # Barra principal
            pygame.draw.rect(
                box_surface,
                bar_color,
                (
                    mouth_start_x + i * bar_spacing,
                    mouth_y - bar_height // 2,
                    bar_width,
                    bar_height,
                ),
            )

        # ====================================================================
        # ÁREA DE TEXTO (USANDO CACHÉ)
        # ====================================================================
        text_start_x = avatar_x + self.size + 15
        text_start_y = avatar_y + 5

        # Generar o usar caché
        if self.cached_text_surf is None:
            self.cached_text_surf = self._render_text_block(max_width)

        box_surface.blit(self.cached_text_surf, (text_start_x, text_start_y))

        # ====================================================================
        # LÍNEA CONECTORA (avatar -> texto)
        # ====================================================================
        conn_start = (avatar_x + self.size, avatar_y + 20)
        conn_end = (avatar_x + self.size + 10, avatar_y + 20)

        # Sombra
        pygame.draw.line(
            box_surface,
            (0, 0, 0),
            (conn_start[0], conn_start[1] - 1),
            (conn_end[0], conn_end[1] - 1),
            3,
        )

        # Línea principal
        pygame.draw.line(box_surface, (0, 255, 255), conn_start, conn_end, 1)

        # ====================================================================
        # APLICAR FADE Y DIBUJAR
        # ====================================================================
        box_surface.set_alpha(self.fade_alpha)
        surface.blit(box_surface, (x - 10, y - 10))


# ============================================================================
# CLASE C64SCROLLER: Scroller estilo Commodore 64
# ============================================================================


class C64Scroller:
    """
    Scroller horizontal estilo demoscene de los 80s/90s
    Con efecto de reflexión y animaciones
    """

    def __init__(self, width):
        """
        Inicializa el scroller

        Args:
            width: Ancho del área de dibujo
        """
        self.w = width

        # Mensaje del scroller
        self.message = config.GAME_CONFIG["SCROLLER_MESSAGE"]

        # Configuración de fuente
        font_path = resource_path("pixel.ttf")

        if os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, 24)  # Fuente pixelada
        else:
            self.font = pygame.font.SysFont("consolas", 26, bold=True)  # Fallback

        # Precalcular anchos de caracteres para optimización
        self.char_widths = [self.font.size(char)[0] for char in self.message]

        # Estado de animación
        self.x_pos = float(width)  # Posición X inicial (fuera de pantalla derecha)
        self.visible = False  # Control de visibilidad
        self.start_time = time.time()

        # Efecto de scanlines
        self.scanlines = pygame.Surface((width, 100), pygame.SRCALPHA)
        self.scanlines.fill((0, 0, 0, 0))

        # Crear líneas de scanline (cada 2px)
        for y in range(0, 100, 2):
            pygame.draw.line(self.scanlines, (0, 0, 0, 128), (0, y), (width, y), 1)

        # Progreso de animación de entrada
        self.anim_progress = 0.0

    def draw(self, surface):
        """
        Dibuja el scroller

        Args:
            surface: Superficie donde dibujar
        """
        # Activar después de 10 segundos
        if not self.visible and time.time() - self.start_time > 10:
            self.visible = True

        if not self.visible:
            return

        # Avanzar animación de entrada
        if self.anim_progress < 1.0:
            self.anim_progress += 0.02
        else:
            self.anim_progress = 1.0

        # ====================================================================
        # DIBUJAR FONDO DEL SCROLLER
        # ====================================================================
        current_width = self.w * self.anim_progress
        start_x = (self.w - current_width) / 2

        background = pygame.Surface((int(current_width), 100), pygame.SRCALPHA)
        background.fill((0, 0, 0, 150))

        # Bordes superior e inferior
        pygame.draw.line(background, (0, 255, 255), (0, 0), (current_width, 0), 2)
        pygame.draw.line(background, (0, 100, 255), (0, 99), (current_width, 99), 2)

        surface.blit(background, (start_x, 30))

        # ====================================================================
        # DIBUJAR TEXTO (solo cuando la animación está avanzada)
        # ====================================================================
        if self.anim_progress > 0.8:
            # Mover texto (scroll izquierda)
            self.x_pos -= 3.0

            # Reiniciar si sale completamente
            if self.x_pos < -sum(self.char_widths):
                self.x_pos = float(self.w)

            current_time = time.time()
            current_x = self.x_pos

            # Dibujar cada carácter
            for i, char in enumerate(self.message):
                # Solo dibujar si está en o cerca de la pantalla
                if -50 < current_x < self.w + 50:
                    # Color arcoíris animado
                    color = (
                        clamp_val(150 + 105 * math.sin(current_time * 3 + i * 0.2)),
                        clamp_val(150 + 105 * math.sin(current_time * 3 + i * 0.2 + 2)),
                        clamp_val(150 + 105 * math.sin(current_time * 3 + i * 0.2 + 4)),
                    )

                    # Efecto de onda vertical
                    y_pos = 55 + math.sin(current_time * 4 + i * 0.15) * 12

                    # Renderizar carácter
                    char_surface = self.font.render(char, False, color)

                    # Sombra
                    surface.blit(
                        self.font.render(char, False, (0, 0, 0)),
                        (current_x + 2, y_pos + 2),
                    )

                    # Carácter principal
                    surface.blit(char_surface, (current_x, y_pos))

                    # Reflexión (debajo, escalada verticalmente)
                    reflection = pygame.transform.flip(char_surface, False, True)
                    reflection = pygame.transform.scale(
                        reflection,
                        (
                            char_surface.get_width(),
                            int(char_surface.get_height() * 0.6),
                        ),
                    )
                    reflection.set_alpha(90)
                    surface.blit(reflection, (current_x, y_pos + 35))

                # Avanzar posición X
                current_x += self.char_widths[i]

        # Aplicar scanlines
        surface.blit(self.scanlines, (0, 30))


# ============================================================================
# CLASE SPAINTEXT: VERSIÓN MEJORADA CON CONTROL DE TAMAÑOS
# ============================================================================


class SpainText:
    """
    Texto estilizado con bandera de España y efectos de partículas
    Versión mejorada con control de tamaños desde config.py
    """

    def __init__(self, text, subtitle, width, height):
        """
        Inicializa el texto con bandera

        Args:
            text: Texto principal
            subtitle: Subtítulo (opcional)
            width: Ancho del área de dibujo
            height: Alto del área de dibujo
        """
        self.w, self.h = width, height

        # Sistema de partículas
        self.particles = []

        # ====================================================================
        # CARGAR CONFIGURACIONES DESDE CONFIG.PY
        # ====================================================================
        from config import GAME_CONFIG

        # Texto español desde config
        self.spanish_text = GAME_CONFIG.get("SPANISH_TEXT", "IN AWESOME SPANISH")

        # Colores específicos de SpainText desde config
        self.spain_colors = GAME_CONFIG["COLORS"].get(
            "SPAIN_TEXT",
            {
                "FLAG_RED": (220, 20, 40),
                "FLAG_YELLOW": (255, 215, 0),
                "FLAG_YELLOW_2": (255, 200, 0),
                "TEXT_WHITE": (255, 255, 255),
                "PARTICLE_FIRE": (255, 50, 0),
                "PARTICLE_GOLD": (255, 200, 0),
                "PARTICLE_LIGHT": (255, 255, 150),
                "SHADOW_COLOR": (120, 0, 0, 180),
                "SPANISH_TEXT_SCALE": 1.0,  # Factor de escala para texto español
                "SUBTITLE_SCALE": 0.8,  # Factor de escala para subtítulo
            },
        )

        # Configuración de animación
        self.anim_config = GAME_CONFIG["COLORS"].get(
            "SPAIN_ANIMATION",
            {
                "PULSE_SPEED": 0.2,
            },
        )

        # ====================================================================
        # CONFIGURAR FUENTES CON AJUSTE AUTOMÁTICO DE TAMAÑO
        # ====================================================================
        max_width = self.w - 60  # Margen de 30px a cada lado
        font_size = 90

        # Reducir tamaño de fuente hasta que quepa
        while font_size > 20:
            try:
                self.font_main = pygame.font.SysFont(
                    "arial black", font_size, bold=True
                )
            except Exception:
                self.font_main = pygame.font.Font(None, font_size)  # Fallback

            test_width, _ = self.font_main.size(text)

            if test_width < max_width:
                break

            font_size -= 5

        # Fuente para subtítulo (con factor de escala del config)
        font_size_sub = int(font_size * self.spain_colors.get("SUBTITLE_SCALE", 0.8))

        try:
            self.font_sub = pygame.font.SysFont("arial black", font_size_sub, bold=True)
        except Exception:
            self.font_sub = pygame.font.Font(None, font_size_sub)

        # Fuente para texto "In Awesome Spanish" (con factor de escala del config)
        # Tamaño base ajustado por el factor de escala
        base_spanish_size = 35
        spanish_scale = self.spain_colors.get("SPANISH_TEXT_SCALE", 1.0)
        spanish_font_size = int(base_spanish_size * spanish_scale)

        try:
            self.font_spanish = pygame.font.SysFont(
                "arial black", spanish_font_size, bold=True
            )
        except Exception:
            self.font_spanish = pygame.font.Font(None, spanish_font_size)

        # ====================================================================
        # RENDERIZAR TEXTOS CON BANDERA (USANDO COLORES DEL CONFIG)
        # ====================================================================
        raw_main = self.font_main.render(text, True, self.spain_colors["TEXT_WHITE"])
        self.main_surf = self._apply_flag(raw_main)
        self.main_width, self.main_height = self.main_surf.get_size()

        # Subtítulo (opcional)
        if subtitle:
            raw_subtitle = self.font_sub.render(
                subtitle, True, self.spain_colors["TEXT_WHITE"]
            )
            self.subtitle_surf = self._apply_flag(raw_subtitle)
            self.subtitle_width, self.subtitle_height = self.subtitle_surf.get_size()
        else:
            self.subtitle_surf = None
            self.subtitle_width, self.subtitle_height = 0, 0

        # Texto "In Awesome Spanish"
        raw_spanish = self.font_spanish.render(
            self.spanish_text, True, self.spain_colors["TEXT_WHITE"]
        )
        self.spanish_surf = self._apply_flag(raw_spanish)
        self.spanish_width, self.spanish_height = self.spanish_surf.get_size()

    def _apply_flag(self, surface):
        """
        Aplica efecto de bandera de España al texto usando colores del config

        Args:
            surface: Superficie con texto renderizado

        Returns:
            Superficie con efecto de bandera aplicado
        """
        if surface is None:
            return None

        width, height = surface.get_size()

        # Crear máscara de bandera con colores del config
        flag_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Bandas de la bandera (25%-50%-25%)
        red_width = int(width * 0.25)
        yellow_width = int(width * 0.50)

        # Usar colores del config para la bandera
        flag_red = self.spain_colors["FLAG_RED"]
        flag_yellow = self.spain_colors["FLAG_YELLOW"]

        pygame.draw.rect(flag_surface, flag_red, (0, 0, red_width + 2, height))
        pygame.draw.rect(
            flag_surface,
            flag_yellow,
            (red_width, 0, yellow_width + 2, height),
        )
        pygame.draw.rect(
            flag_surface,
            flag_red,
            (red_width + yellow_width, 0, width - (red_width + yellow_width), height),
        )

        # Aplicar bandera al texto (multiplicación de colores)
        final_surface = surface.copy()
        final_surface.blit(flag_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Crear efecto de sticker/pegatina con sombra
        shadow = pygame.transform.smoothscale(
            surface, (int(width * 1.05), int(height * 1.05))
        )
        shadow_color = self.spain_colors.get("SHADOW_COLOR", (120, 0, 0, 180))
        shadow.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)

        sticker = pygame.Surface(
            (shadow.get_width(), shadow.get_height()), pygame.SRCALPHA
        )
        center_x, center_y = sticker.get_width() // 2, sticker.get_height() // 2

        sticker.blit(shadow, (0, 0))
        sticker.blit(final_surface, final_surface.get_rect(center=(center_x, center_y)))

        return sticker

    def _update_particles(self, intensity, kick, center_x, center_y, width_scale):
        """
        Actualiza el sistema de partículas usando colores del config

        Args:
            intensity: Intensidad general
            kick: Intensidad de golpe (para spawn)
            center_x, center_y: Centro del texto
            width_scale: Escala actual del ancho (para spawn area)
        """
        current_width = self.main_width * width_scale

        if current_width < 10:
            return

        # Número de partículas a generar
        spawn_count = 2 + int(intensity * 5 + kick * 10)
        top_y = center_y - (self.main_height // 2) + 10

        # Usar colores de partículas del config
        particle_colors = [
            self.spain_colors["PARTICLE_FIRE"],
            self.spain_colors["PARTICLE_GOLD"],
            self.spain_colors["PARTICLE_LIGHT"],
        ]

        for _ in range(spawn_count):
            # Posición aleatoria dentro del ancho del texto
            particle_x = random.uniform(-current_width / 2 + 5, current_width / 2 - 5)
            particle_y = random.uniform(-10, 10)

            # Seleccionar color aleatorio de la lista del config
            color = random.choice(particle_colors)

            self.particles.append(
                {
                    "x": center_x + particle_x,
                    "y": top_y + particle_y,
                    "vx": random.uniform(-1, 1),  # Velocidad X
                    "vy": random.uniform(-2, -5)
                    - (kick * 2),  # Velocidad Y (hacia arriba)
                    "size": random.uniform(3, 8),  # Tamaño inicial
                    "life": 1.0,  # Vida (1.0-0.0)
                    "color": color,
                }
            )

        # Actualizar partículas existentes
        for particle in self.particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["size"] *= 0.94  # Reducir tamaño
            particle["life"] -= 0.025  # Reducir vida

        # Eliminar partículas muertas
        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw(self, surface, time_val, intensity, kick):
        """
        Dibuja el texto con animaciones

        Args:
            surface: Superficie donde dibujar
            time_val: Tiempo desde inicio para animaciones
            intensity: Intensidad general
            kick: Intensidad de golpe (para efectos)
        """
        # Esperar 8.5 segundos antes de aparecer
        start_time = 8.5
        if time_val < start_time:
            return

        # ====================================================================
        # CALCULAR ANIMACIONES
        # ====================================================================
        fade_duration = 1.5
        alpha = min(255, int(((time_val - start_time) / fade_duration) * 255))

        center_x, center_y = self.w // 2, self.h // 2

        # Animación de escala (pulsación) usando velocidad del config
        rotation_speed = (time_val - start_time) * 2.0
        scale_main_x = abs(math.cos(rotation_speed))
        scale_spanish_x = abs(math.cos(rotation_speed + math.pi / 2))

        # ====================================================================
        # CALCULAR DIMENSIONES ACTUALES
        # ====================================================================
        current_width_main = max(2, int(self.main_width * scale_main_x))
        current_width_subtitle = (
            max(2, int(self.subtitle_width * scale_main_x)) if self.subtitle_surf else 0
        )
        current_width_spanish = max(2, int(self.spanish_width * scale_spanish_x))

        # Calcular altura total para centrado vertical
        total_height = (
            self.main_height
            + (self.subtitle_height if self.subtitle_surf else 0)
            + self.spanish_height
            + 20
        )

        start_y = center_y - (total_height // 2)

        # ====================================================================
        # DIBUJAR TEXTO PRINCIPAL
        # ====================================================================
        if current_width_main > 5:
            scaled_main = pygame.transform.scale(
                self.main_surf, (current_width_main, self.main_height)
            )
            scaled_main.set_alpha(alpha)

            main_rect = scaled_main.get_rect(
                center=(center_x, start_y + self.main_height // 2)
            )
            surface.blit(scaled_main, main_rect)

        # ====================================================================
        # DIBUJAR SUBTÍTULO
        # ====================================================================
        y_offset = start_y + self.main_height + 2

        if self.subtitle_surf and current_width_subtitle > 5:
            scaled_subtitle = pygame.transform.scale(
                self.subtitle_surf, (current_width_subtitle, self.subtitle_height)
            )
            scaled_subtitle.set_alpha(alpha)

            subtitle_rect = scaled_subtitle.get_rect(
                center=(center_x, y_offset + self.subtitle_height // 2)
            )
            surface.blit(scaled_subtitle, subtitle_rect)

            y_offset += self.subtitle_height + 10
        else:
            y_offset += 10

        # ====================================================================
        # DIBUJAR "IN AWESOME SPANISH" (CON ESCALA VERTICAL AJUSTABLE)
        # ====================================================================
        if current_width_spanish > 5:
            # Factor de escala vertical adicional para hacerlo más alto
            spanish_scale_factor = self.spain_colors.get("SPANISH_TEXT_SCALE", 1.0)

            # Aplicar escala vertical manteniendo proporción horizontal
            target_width = current_width_spanish
            target_height = int(self.spanish_height * spanish_scale_factor)

            scaled_spanish = pygame.transform.scale(
                self.spanish_surf, (target_width, target_height)
            )
            scaled_spanish.set_alpha(alpha)

            spanish_rect = scaled_spanish.get_rect(
                center=(center_x, y_offset + target_height // 2)
            )
            surface.blit(scaled_spanish, spanish_rect)

        # ====================================================================
        # PARTÍCULAS (solo cuando el texto es visible)
        # ====================================================================
        if alpha > 200:
            self._update_particles(intensity, kick, center_x, center_y, scale_main_x)

            for particle in self.particles:
                particle_color = particle["color"] + (int(particle["life"] * 255),)
                draw_circle_alpha(
                    surface,
                    particle_color,
                    (particle["x"], particle["y"]),
                    particle["size"],
                )


# ============================================================================
# CLASE CYBERCURSOR: Cursor personalizado con efectos
# ============================================================================


class CyberCursor:
    """
    Cursor personalizado con estela de partículas y efectos de hover
    Reemplaza el cursor del sistema por uno estilo cyberpunk
    """

    def __init__(self):
        """Inicializa el cursor personalizado"""
        self.trail = []  # Estela de posiciones anteriores
        self.max_trail = 16  # Máximo de puntos en la estela
        self.size = 50  # Tamaño del cursor
        self.angle = 0  # Ángulo para rotación
        self.hovering = False  # Estado de hover sobre elemento clickeable

    def update(self, mouse_x, mouse_y, is_hovering):
        """
        Actualiza estado del cursor

        Args:
            mouse_x, mouse_y: Posición actual del ratón
            is_hovering: Si está sobre elemento clickeable
        """
        self.hovering = is_hovering

        # Velocidad de rotación según estado
        rotation_speed = 10 if self.hovering else 2
        self.angle = (self.angle + rotation_speed) % 360

        # Añadir posición actual a la estela
        self.trail.append({"pos": (mouse_x, mouse_y), "life": 1.0})

        # Limitar longitud de estela
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        # Reducir vida de puntos de la estela
        for point in self.trail:
            point["life"] -= 0.06

        # Eliminar puntos muertos
        self.trail = [p for p in self.trail if p["life"] > 0]

    def draw(self, surface):
        """
        Dibuja el cursor completo

        Args:
            surface: Superficie donde dibujar
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Colores según estado
        if self.hovering:
            main_color = (255, 80, 50)  # Naranja-rojo para hover
            trail_color = (255, 150, 50)  # Naranja para estela
        else:
            main_color = (0, 255, 255)  # Cian para normal
            trail_color = (0, 150, 255)  # Azul para estela

        # ====================================================================
        # DIBUJAR ESTELA
        # ====================================================================
        if len(self.trail) > 1:
            # Línea que conecta todos los puntos de la estela
            trail_points = [point["pos"] for point in self.trail]
            pygame.draw.lines(surface, trail_color, False, trail_points, 3)

            # Puntos individuales de la estela
            for point in self.trail:
                trail_radius = int(12 * point["life"])

                if trail_radius > 1:
                    trail_surf = pygame.Surface(
                        (trail_radius * 2, trail_radius * 2), pygame.SRCALPHA
                    )

                    pygame.draw.circle(
                        trail_surf,
                        (*trail_color, int(100 * point["life"])),
                        (trail_radius, trail_radius),
                        trail_radius,
                    )

                    surface.blit(
                        trail_surf,
                        (
                            point["pos"][0] - trail_radius,
                            point["pos"][1] - trail_radius,
                        ),
                    )

        # ====================================================================
        # CURSOR PRINCIPAL (forma diferente según estado)
        # ====================================================================
        offset = self.size // 2

        if self.hovering:
            # Cruz para elementos clickeables
            cross_size = 10
            pygame.draw.line(
                surface,
                main_color,
                (mouse_x - cross_size, mouse_y),
                (mouse_x + cross_size, mouse_y),
                3,
            )
            pygame.draw.line(
                surface,
                main_color,
                (mouse_x, mouse_y - cross_size),
                (mouse_x, mouse_y + cross_size),
                3,
            )

            # Cuadrado interior
            pygame.draw.rect(
                surface,
                main_color,
                (mouse_x - offset + 10, mouse_y - offset + 10, 30, 30),
                2,
            )
        else:
            # Cruz simple para modo normal
            # Línea vertical
            surface.fill(
                main_color, (mouse_x - 2, mouse_y - offset + 5, 4, self.size - 10)
            )

            # Línea horizontal
            surface.fill(
                main_color, (mouse_x - offset + 5, mouse_y - 2, self.size - 10, 4)
            )

            # Cuadrado interior
            pygame.draw.rect(
                surface,
                main_color,
                (mouse_x - offset + 10, mouse_y - offset + 10, 30, 30),
                2,
            )

        # ====================================================================
        # ANILLO ROTATORIO EXTERIOR
        # ====================================================================
        ring_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        # Arcos rotatorios (cuadrantes opuestos)
        pygame.draw.arc(
            ring_surface,
            (255, 255, 255),
            (2, 2, self.size - 4, self.size - 4),
            math.radians(self.angle),
            math.radians(self.angle + 90),
            3,
        )

        pygame.draw.arc(
            ring_surface,
            (255, 255, 255),
            (2, 2, self.size - 4, self.size - 4),
            math.radians(self.angle + 180),
            math.radians(self.angle + 270),
            3,
        )

        surface.blit(ring_surface, (mouse_x - offset, mouse_y - offset))

        # ====================================================================
        # PUNTO CENTRAL ANIMADO
        # ====================================================================
        # Círculo exterior pulsante
        pulse_size = int(
            4
            + math.sin(time.time() * (20 if self.hovering else 10))
            * (2 if self.hovering else 1)
        )
        pygame.draw.circle(surface, (255, 255, 255), (mouse_x, mouse_y), pulse_size)

        # Punto central fijo
        pygame.draw.circle(surface, (255, 0, 0), (mouse_x, mouse_y), 2)


# ============================================================================
# CLASE TACTICALHUD: HUD táctico para fase de targeting
# ============================================================================


class TacticalHUD:
    """
    HUD táctico estilo videojuego con seguimiento de objetivo
    Se activa durante la fase de targeting de la instalación
    """

    def __init__(self, width, height):
        """
        Inicializa el HUD táctico

        Args:
            width: Ancho del área de dibujo
            height: Alto del área de dibujo
        """
        self.w, self.h = width, height
        self.center_x, self.center_y = width // 2, height // 2

        # Estado del HUD
        self.angle = 0  # Ángulo para animaciones
        self.active = False  # HUD activado
        self.waypoints = []  # Puntos de ruta para seguimiento
        self.trail = []  # Estela del seguimiento

    def activate(self, start_rect):
        """
        Activa el HUD con un rectángulo inicial

        Args:
            start_rect: Rectángulo pygame donde comenzar
        """
        self.active = True
        self.start_rect = start_rect

        # Generar ruta aleatoria de waypoints
        self.waypoints = [
            (self.start_rect.centerx, self.start_rect.centery),  # Comienzo (botón)
            (
                random.randint(100, self.w - 100),
                random.randint(100, self.h - 100),
            ),  # Punto aleatorio 1
            (
                random.randint(100, self.w - 100),
                random.randint(100, self.h - 100),
            ),  # Punto aleatorio 2
            (self.center_x, self.center_y),  # Centro de pantalla (objetivo final)
        ]

        self.trail = []  # Reiniciar estela

    def smooth_step(self, t):
        """
        Función de easing SmoothStep (suavizado entrada/salida)

        Args:
            t: Valor entre 0.0 y 1.0

        Returns:
            Valor suavizado
        """
        return t * t * (3 - 2 * t)

    def draw(self, surface, time_factor):
        """
        Dibuja el HUD táctico

        Args:
            surface: Superficie donde dibujar
            time_factor: Progreso de la animación (0.0-1.0)
        """
        if not self.active:
            return

        t = time_factor
        scan_color = GAME_CONFIG["COLORS"]["RED_ALERT"]
        search_color = (0, 255, 255)
        lock_color = (255, 0, 0)

        # ====================================================================
        # FASE 1: CONTRACCIÓN DEL BOTÓN (0.0-0.1)
        # ====================================================================
        if t < 0.1:
            progress = t / 0.1

            # Interpolar del tamaño del botón a un punto pequeño
            current_width = self.start_rect.width * (1 - progress) + 40 * progress

            target_rect = pygame.Rect(0, 0, current_width, self.start_rect.height)
            target_rect.center = self.start_rect.center

            pygame.draw.rect(surface, scan_color, target_rect, border_radius=6)
            return

        # ====================================================================
        # FASE 2: BÚSQUEDA/ESCANEO (0.1-0.6)
        # ====================================================================
        if t < 0.6:
            search_time = (t - 0.1) / 0.5
            search_time = max(0, min(1, search_time))

            total_segments = len(self.waypoints) - 1
            segment_index = int(search_time * total_segments)

            if segment_index >= total_segments:
                segment_index = total_segments - 1

            # Progreso dentro del segmento actual
            segment_progress = self.smooth_step(
                (search_time * total_segments) - segment_index
            )

            # Calcular posición actual interpolando entre waypoints
            point1 = self.waypoints[segment_index]
            point2 = self.waypoints[segment_index + 1]

            current_x = point1[0] + (point2[0] - point1[0]) * segment_progress
            current_y = point1[1] + (point2[1] - point1[1]) * segment_progress

            # Animación de rotación
            self.angle += 15

            # Añadir a estela
            self.trail.append((current_x, current_y))
            if len(self.trail) > 15:
                self.trail.pop(0)

            # Dibujar estela
            if len(self.trail) > 1:
                pygame.draw.lines(surface, (0, 100, 150), False, self.trail, 3)

            # Punto de escaneo
            pygame.draw.circle(
                surface, search_color, (int(current_x), int(current_y)), 6
            )

            # Anillos de escaneo rotatorios
            scan_surface = pygame.Surface((120, 120), pygame.SRCALPHA)

            # Arcos animados
            pygame.draw.arc(
                scan_surface,
                search_color,
                (10, 10, 100, 100),
                math.radians(self.angle),
                math.radians(self.angle + 120),
                4,
            )

            pygame.draw.arc(
                scan_surface,
                search_color,
                (10, 10, 100, 100),
                math.radians(self.angle + 180),
                math.radians(self.angle + 300),
                4,
            )

            # Círculo exterior
            pygame.draw.circle(scan_surface, (255, 255, 255, 100), (60, 60), 58, 1)

            surface.blit(scan_surface, (current_x - 60, current_y - 60))

            # Texto de coordenadas
            coord_font = pygame.font.SysFont("consolas", 16, bold=True)
            coord_text = coord_font.render(
                f"SCANNING.. [{int(current_x)}:{int(current_y)}]", True, search_color
            )
            surface.blit(coord_text, (current_x + 40, current_y - 30))

        # ====================================================================
        # FASE 3: BLOQUEO DE OBJETIVO (0.6-1.0)
        # ====================================================================
        if t >= 0.6:
            lock_progress = (t - 0.6) / 0.4
            radius = int(50 + lock_progress * 60)

            # Cruz de targeting
            pygame.draw.circle(
                surface, lock_color, (self.center_x, self.center_y), radius, 3
            )

            pygame.draw.line(
                surface,
                lock_color,
                (self.center_x - radius, self.center_y),
                (self.center_x + radius, self.center_y),
                2,
            )

            pygame.draw.line(
                surface,
                lock_color,
                (self.center_x, self.center_y - radius),
                (self.center_x, self.center_y + radius),
                2,
            )

            # Punto central parpadeante
            if int(time.time() * 20) % 2 == 0:
                pygame.draw.circle(
                    surface, (255, 100, 100), (self.center_x, self.center_y), 12
                )

            # Texto de bloqueo
            lock_font = pygame.font.SysFont("consolas", 24, bold=True)
            lock_text = lock_font.render("[ TARGET LOCKED ]", True, lock_color)
            surface.blit(
                lock_text,
                (
                    self.center_x - lock_text.get_width() // 2,
                    self.center_y + radius + 15,
                ),
            )


# ============================================================================
# CLASE HEXDUMPLOADER: Simulador de volcado hexadecimal
# ============================================================================


class HexDumpLoader:
    """
    Simula un volcado hexadecimal de memoria durante la instalación
    Estilo terminal/debugger con progreso animado
    """

    def __init__(self, width, height):
        """
        Inicializa el volcado hexadecimal

        Args:
            width: Ancho del área de dibujo
            height: Alto del área de dibujo
        """
        self.w = width

        # Rectángulo del loader (más compacto que antes)
        self.rect = pygame.Rect(20, height - 140, 300, 110)

        # Configuración de fuente
        self.font = pygame.font.SysFont("consolas", 12)

        # Datos del volcado
        self.lines = []  # Líneas de hexadecimal
        self.last_update = 0  # Última actualización

        # Caracteres hexadecimales para generar datos
        self.hex_chars = "0123456789ABCDEF"

    def generate_line(self):
        """
        Genera una línea aleatoria de volcado hexadecimal

        Returns:
            String con formato: "0xXXXX | XX XX XX XX XX XX XX XX | ...."
        """
        # Dirección de memoria aleatoria
        address = f"0x{random.randint(0, 65535):04X}"

        # 8 bytes de datos hexadecimales
        data_bytes = " ".join(
            [
                f"{random.choice(self.hex_chars)}{random.choice(self.hex_chars)}"
                for _ in range(8)
            ]
        )

        # Representación ASCII (simplificada)
        ascii_sim = "".join([random.choice("..::--//#") for _ in range(4)])

        return f"{address} | {data_bytes} | {ascii_sim}"

    def draw(self, surface, progress, is_active):
        """
        Dibuja el volcado hexadecimal

        Args:
            surface: Superficie donde dibujar
            progress: Progreso de instalación (0.0-1.0)
            is_active: Si el loader está activo
        """
        if not is_active:
            return

        # Crear superficie para el loader
        loader_surf = pygame.Surface(
            (self.rect.width, self.rect.height), pygame.SRCALPHA
        )
        loader_surf.fill((0, 20, 40, 200))  # Azul oscuro semitransparente

        # Borde cyan
        pygame.draw.rect(
            loader_surf, (0, 255, 255), (0, 0, self.rect.width, self.rect.height), 1
        )

        # Generar nuevas líneas periódicamente
        if time.time() - self.last_update > 0.05:
            self.lines.append(self.generate_line())

            if len(self.lines) > 7:  # Mantener máximo 7 líneas
                self.lines.pop(0)

            self.last_update = time.time()

        # ====================================================================
        # DIBUJAR LÍNEAS DE HEXADECIMAL
        # ====================================================================
        y_offset = 5

        for i, line in enumerate(self.lines):
            # Color más brilloso según progreso
            color_value = 100 + int(progress * 155)
            line_color = (color_value, 255, color_value)

            line_surface = self.font.render(line, True, line_color)
            loader_surf.blit(line_surface, (10, y_offset))
            y_offset += 15

        # ====================================================================
        # BARRA DE PROGRESO
        # ====================================================================
        # Barra verde en la parte inferior
        pygame.draw.rect(
            loader_surf,
            (0, 255, 0),
            (0, self.rect.height - 5, int(self.rect.width * progress), 5),
        )

        # Texto de progreso
        progress_text = self.font.render(
            f"MEMORY DUMP // WRITING: {int(progress * 100)}%", True, (255, 255, 0)
        )
        loader_surf.blit(progress_text, (10, self.rect.height - 25))

        # Dibujar loader en superficie principal
        surface.blit(loader_surf, self.rect.topleft)


# ============================================================================
# CLASE SYSTEMMONITOR: Monitor de sistema minimalista
# ============================================================================


class SystemMonitor:
    """
    Monitor de sistema simple que muestra FPS y estadísticas
    Se activa con F1
    """

    def __init__(self):
        """Inicializa el monitor de sistema"""
        self.font = pygame.font.SysFont("consolas", 10)
        self.history = []  # Historial de FPS para gráfico

    def draw(self, surface, fps):
        """
        Dibuja el monitor de sistema

        Args:
            surface: Superficie donde dibujar
            fps: FPS actuales a mostrar
        """
        width, height = 160, 70
        x_pos = surface.get_width() - width - 10
        y_pos = 10

        # Crear superficie del monitor
        monitor_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        monitor_surf.fill((0, 0, 0, 150))  # Fondo semitransparente

        # Borde gris
        pygame.draw.rect(monitor_surf, (100, 100, 100), (0, 0, width, height), 1)

        # ====================================================================
        # GRÁFICO DE FPS
        # ====================================================================
        self.history.append(fps)

        # Limitar historial al ancho disponible
        if len(self.history) > width - 10:
            self.history.pop(0)

        # Dibujar línea de gráfico si hay suficientes datos
        if len(self.history) > 2:
            points = []

            for i, fps_value in enumerate(self.history):
                # Escalar FPS a altura del gráfico (max 150 FPS = altura completa)
                scaled_y = 30 - min(30, int(fps_value * 0.4)) + 35
                points.append((i + 5, scaled_y))

            # Línea verde para el gráfico
            pygame.draw.lines(monitor_surf, (0, 255, 0), False, points, 1)

        # ====================================================================
        # ESTADÍSTICAS DE TEXTO
        # ====================================================================
        # FPS actual
        fps_text = self.font.render(f"FPS: {int(fps)}", True, (0, 255, 0))
        monitor_surf.blit(fps_text, (5, 5))

        # VRAM simulado
        vram_text = self.font.render(
            f"VRAM: {random.randint(1024, 4096)}MB", True, (0, 255, 255)
        )
        monitor_surf.blit(vram_text, (5, 15))

        # Threads activos
        threads_text = self.font.render(
            f"T-THREAD: {threading.active_count()}", True, (255, 100, 100)
        )
        monitor_surf.blit(threads_text, (5, 25))

        # Dibujar monitor en superficie principal
        surface.blit(monitor_surf, (x_pos, y_pos))


# ============================================================================
# CLASE CYBERCONTROLSUI: UI de controles estilo cyberpunk
# ============================================================================


class CyberControlsUI:
    """
    Interfaz de controles con fondo animado y lista de teclas
    Se muestra cuando el usuario hace click en el logo
    """

    def __init__(self):
        """Inicializa la UI de controles"""
        self.width, self.height = 740, 480  # Dimensiones de la ventana

        # Animación de scroll para fondo
        self.scroll = 0.0

        # Montañas para fondo animado
        self.mountains_back = [
            (x, random.randint(150, 250)) for x in range(0, self.width + 100, 40)
        ]

        self.mountains_front = [
            (x, random.randint(50, 100)) for x in range(0, self.width + 100, 20)
        ]

    def draw_death_star(self, surface, x, y, radius):
        """
        Dibuja una Estrella de la Muerte estilizada

        Args:
            surface: Superficie donde dibujar
            x, y: Centro de la Estrella de la Muerte
            radius: Radio principal
        """
        # Colores
        outline_color = (180, 180, 180)  # Gris metálico
        body_color = (30, 30, 35)  # Gris oscuro

        # Círculo principal
        pygame.draw.circle(surface, body_color, (x, y), radius)
        pygame.draw.circle(surface, outline_color, (x, y), radius, 2)

        # Línea ecuatorial
        pygame.draw.line(
            surface, (10, 10, 10), (x - radius + 2, y), (x + radius - 2, y), 6
        )

        # Superláser (círculo desplazado)
        laser_x = x - int(radius * 0.4)
        laser_y = y - int(radius * 0.35)
        laser_radius = int(radius * 0.28)

        pygame.draw.circle(surface, (20, 20, 20), (laser_x, laser_y), laser_radius)
        pygame.draw.circle(surface, outline_color, (laser_x, laser_y), laser_radius, 1)

        # Líneas de panel (paralelas al ecuador)
        line_positions = [-0.7, -0.5, 0.4, 0.7]

        for position_factor in line_positions:
            line_y = y + int(radius * position_factor)
            line_width = int(math.sqrt(radius**2 - (line_y - y) ** 2))

            pygame.draw.line(
                surface,
                (50, 50, 60),
                (x - line_width, line_y),
                (x + line_width, line_y),
                1,
            )

    def draw_poly_line(self, surface, points, color, speed_scroll, offset_y):
        """
        Dibuja una línea poligonal con efecto de scroll

        Args:
            surface: Superficie donde dibujar
            points: Lista de puntos (x, y)
            color: Color de la línea
            speed_scroll: Velocidad de scroll
            offset_y: Desplazamiento vertical
        """
        # Aplicar scroll a los puntos
        shifted_points = []
        scroll_mod = (self.scroll * speed_scroll) % self.width

        for point_x, point_y in points:
            shifted_x = point_x - scroll_mod

            # Wrap-around para scroll infinito
            if shifted_x < -50:
                shifted_x += self.width + 100

            shifted_y = self.height - point_y - offset_y
            shifted_points.append((shifted_x, shifted_y))

        # Ordenar por X para mejor renderizado
        shifted_points.sort(key=lambda p: p[0])

        # Dibujar línea si hay suficientes puntos
        if len(shifted_points) > 1:
            pygame.draw.lines(surface, color, False, shifted_points, 2)

            # Puntos en la línea
            for point_x, point_y in shifted_points:
                if 0 < point_x < self.width:
                    pygame.draw.circle(
                        surface, (255, 255, 255), (int(point_x), int(point_y)), 2
                    )

    def draw(self, destination_surface, controls_avatar):
        """
        Dibuja la UI completa de controles

        Args:
            destination_surface: Superficie principal donde dibujar
            controls_avatar: Avatar para mostrar ayuda
        """
        # Actualizar scroll para animación
        self.scroll += 1.0

        # Centro de la pantalla principal
        center_x, center_y = (
            GAME_CONFIG["WINDOW_SIZE"][0] // 2,
            GAME_CONFIG["WINDOW_SIZE"][1] // 2,
        )

        # Crear superficie para la ventana de controles
        controls_window = pygame.Surface((self.width, self.height))
        controls_window.fill((10, 8, 20))  # Fondo azul oscuro espacial

        # ====================================================================
        # FONDO ANIMADO
        # ====================================================================
        # Estrella de la Muerte con scroll horizontal
        death_star_x = (200 + int(self.scroll * 0.2)) % (self.width + 250) - 100
        self.draw_death_star(controls_window, death_star_x, 120, 65)

        # Montañas traseras
        self.draw_poly_line(
            controls_window, self.mountains_back, (100, 0, 200), 0.5, 50
        )

        # Montañas delanteras
        self.draw_poly_line(
            controls_window, self.mountains_front, (0, 255, 200), 1.5, 0
        )

        # ====================================================================
        # OVERLAY SEMITRANSPARENTE
        # ====================================================================
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 200))  # Azul oscuro semitransparente

        # Borde cyan con esquinas redondeadas
        pygame.draw.rect(
            overlay, (0, 255, 255), (0, 0, self.width, self.height), 3, border_radius=15
        )

        controls_window.blit(overlay, (0, 0))

        # ====================================================================
        # TÍTULO
        # ====================================================================
        title_font = pygame.font.SysFont("arial black", 24)
        title_text = "SYSTEM CONTROLS // MANUAL OVERRIDE"

        # Sombra del título
        title_shadow = title_font.render(title_text, True, (0, 255, 255))
        controls_window.blit(title_shadow, (32, 22))

        # Título principal
        title_main = title_font.render(title_text, True, (255, 255, 255))
        controls_window.blit(title_main, (30, 20))

        # ====================================================================
        # ÁREA DEL AVATAR (izquierda)
        # ====================================================================
        avatar_start_x = 25
        avatar_start_y = 130
        avatar_max_width = 230  # Ancho máximo del texto del avatar

        # Área total estimada del avatar
        avatar_total_width = (
            80 + avatar_max_width + 40
        )  # Avatar(80) + Texto(230) + Margen(40)

        # Dibujar avatar de controles
        controls_avatar.draw(
            controls_window, avatar_start_x, avatar_start_y, max_width=avatar_max_width
        )

        # ====================================================================
        # LISTA DE CONTROLES (derecha)
        # ====================================================================
        controls_x = avatar_start_x + avatar_total_width + 20  # Separación del avatar
        controls_y = 80

        # Verificar que haya espacio suficiente
        if controls_x > self.width - 150:
            controls_x = self.width - 300  # Forzar ancho mínimo

        controls_width = self.width - controls_x - 25  # Ancho restante

        # Marco para controles
        pygame.draw.rect(
            controls_window,
            (0, 100, 150),
            (controls_x, controls_y, controls_width, self.height - controls_y - 30),
            1,
            border_radius=10,
        )

        # ====================================================================
        # LISTA DE TECLAS ULTRA-COMPACTA
        # ====================================================================
        key_bindings = [
            ("ESC", "Salir"),
            ("↑", "+Vol"),  # Flecha arriba
            ("↓", "-Vol"),  # Flecha abajo
            ("←", "Prev"),  # Flecha izquierda
            ("→", "Next"),  # Flecha derecha
            ("B", "BPM Info"),
            ("N", "BPM On/Off"),
            ("F1", "Monitor"),
            ("RMB", "RAVE"),  # Click derecho
        ]

        # Fuentes compactas
        key_font = pygame.font.SysFont("consolas", 15, bold=True)
        desc_font = pygame.font.SysFont("arial", 13)

        # Dimensiones ultra compactas
        key_button_width = 60
        key_button_height = 25

        # Dibujar cada tecla
        for i, (key, description) in enumerate(key_bindings):
            item_y = controls_y + 18 + i * 38  # Espaciado muy ajustado

            # Rectángulo del botón
            key_rect = pygame.Rect(
                controls_x + 12, item_y, key_button_width, key_button_height
            )

            # Fondo del botón
            pygame.draw.rect(controls_window, (40, 50, 70), key_rect, border_radius=3)

            # Borde (color especial para RMB)
            if "RMB" in key:
                border_color = (255, 0, 255)  # Magenta para ratón
            else:
                border_color = (0, 255, 255)  # Cyan para teclas

            pygame.draw.rect(
                controls_window, border_color, key_rect, 1, border_radius=3
            )

            # Texto de la tecla (centrado)
            key_text = key_font.render(key, True, (255, 255, 255))
            text_rect = key_text.get_rect(center=key_rect.center)
            controls_window.blit(key_text, text_rect)

            # Descripción (pegada al botón)
            desc_x = controls_x + 12 + key_button_width + 8
            desc_y = item_y + 4

            desc_text = desc_font.render(description, True, (200, 220, 255))
            controls_window.blit(desc_text, (desc_x, desc_y))

        # ====================================================================
        # DIBUJAR VENTANA CENTRADA EN PANTALLA PRINCIPAL
        # ====================================================================
        destination_surface.blit(
            controls_window, (center_x - self.width // 2, center_y - self.height // 2)
        )
