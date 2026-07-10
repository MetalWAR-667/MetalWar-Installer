# config.py
# Configuración principal del juego MetalWar
# Contiene todos los parámetros ajustables del sistema

GAME_CONFIG = {

    # INFORMACIÓN BÁSICA
    "GAME_FOLDER_NAME": "King's Quest",
    "GAME_NAME_DISPLAY": "King's Quest 2016",
    "WINDOW_CAPTION": "MetalWAR - Instalador",
    "SCROLLER_MESSAGE": "MetalWAR PROUDLY PRESENTS...              THE ULTIMATE SPANISH TRANSLATION FIX FOR KING'S QUEST 2016!                               CODE: Mihweb0hmoren0h         GRAPHICS BY LoverActiveMind...     MUSIC: ALWAYS!...         THANKS TO OUR COMRADES IN ARMS - G3KPLAY - KURT & AFRICA97 - FOR STARTING AND COMPLETING THE TRANSLATION OF EPISODE 1 IN 2016, YOUR EFFORTS WILL BE PRESERVED!. IT TOOK 10 YEARS FOR ME TO BE ENCOURAGED TO RESUME YOUR WORK ON EPISODE 2... LET'S HOPE IT DOESN'T TAKE ANOTHER 10 YEARS FOR SOMEONE TO BE ENCOURAGED TO TAKE ON EPISODE 3... MAYBE ONLY 5 :-P                         GREETINGS TO ELOTROLADO TRANSLATORS MEMBERS AS... Shad0wman1, l0coroco96, HoJuEructus, & whoever arrives!,....    & THANKS TO ALL THE FAKkIN'C0D€R$ ON THIS FAKkIN PLANET FOR MAKING OUR WORK EASIER WITH YOUR AWESOME TOOLS.        RESPECT FOR THAT! \m/      ... and of course to LEGACY OF... FUTURE CREW, IGUANA, THE BLACK LOTUS, KEWLERS, AND SECOND REALITY TEAM...  YOU STARTED MY WAR!",
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
