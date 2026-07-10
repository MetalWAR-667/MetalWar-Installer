███╗   ███╗███████╗████████╗ █████╗ ██╗
████╗ ████║██╔════╝╚══██╔══╝██╔══██╗██║
██╔████╔██║█████╗     ██║   ███████║██║
██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██║
██║ ╚═╝ ██║███████╗   ██║   ██║  ██║███████╗
╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝

###############################################################
#                                                             #
#           METALWAR INSTALLER                                #
#                                                             #
#          README v0.0000000001-pre-pre-alpha                #
#                                                             #
#  Certified Overengineered Since Last Tuesday               #
#                                                             #
###############################################################

ENGLISH
=======

Congratulations.

You've somehow ended up reading the documentation for a Windows installer.
This raises several questions.
Mostly about your life choices.

> *"I'm not building an installer. I'm relearning how to code."*

---

## Requirements

✔ Windows
✔ A functioning mouse
✔ A computer with the processing power of a coffee maker
✔ Emotional strength to watch your keyboard turn into a nightclub

---

## What is this?

"It's a technically unnecessary project executed with a completely disproportionate level of dedication."

**On paper:** A Windows installer.

**In reality:** My excuse to touch code again after too many years away.

Python, Git, project structure, documentation, automation, versioning...

The boring stuff.

The necessary stuff.

**MetalWar Installer** isn't just a translation installer; it's a tribute to the **90s Demoscene**. A generic deployment engine designed to distribute fan-made patches and translations with aggressive visuals, real-time 3D graphics, and perfect musical synchronization.

> *"Because if we're going to distribute a fan-made game translation, we're going to do it with style, and two big balls.🤘"*

---

## Why publish something this small?

Everyone shows the finished cathedral.
Almost nobody shows the scaffolding.
This repository is the scaffolding.
You'll see things done well.
You'll see things I fix three commits later.
That's part of the process.
Learning leaves fingerprints.

I'm not hiding them.

---

## Mission

Turn a tiny installer into a testing ground for learning professional development.
Not through endless tutorials.
By building.
Breaking.
Fixing.
Writing about it.

And repeating.

## Architecture

The installer has been carefully designed following decades of industry best practices.

Some of them.
The important ones.
Well...
More or less. 🎸

What is a best practice?

---

## Secondary Mission

Learn Git properly.

Not "I know just enough not to screw it up, until I screw it up."

Properly.

This repo will be my training ground for:

- meaningful commits
- branches
- merges
- tags
- releases
- pull requests
- documentation
- project organization

---

## README Status

This README is alive.

It will evolve as much as the code.

Maybe more.

If you notice weird changes...
You're watching someone learn Markdown thirty years after writing text-mode documentation.

Some start with Markdown.
Others start with ASCII art.

Life is weird.

---

## Philosophy

Old programmers had a curious habit.

Instead of asking *"Can the computer do this?"*
they asked *"How can I convince the computer to do this?"*

That mindset never stopped being cool.

Optimization isn't obsession. It's curiosity.
Documentation isn't bureaucracy. It's respect for Future You.
Clean code isn't posing. It's kindness.

---

## Warning

This repository contains dangerous levels of enthusiasm.

Possible side effects:

- reorganizing folders that were already fine
- renaming variables because they "feel better"
- adding comments nobody asked for
- rewriting documentation at 2 a.m.
- spending more time on the README than on the code

All normal. You may continue your journey.

---

### 🕹️ Main Features (Certified Overengineering)

### 💎 Demoscene Visuals (Because performance is temporary, but style is eternal)
- **Out-of-Control Starfield 3D**: A starfield with camera barrel roll rotation and warp effect reactive to BPM that consumes more CPU than NASA used to reach the Moon.
- **Adaptive Visualizers**: The graphics engine interrogates the audio codec in real-time. If you switch the tracker track, the system switches its render matrices on the fly.
- **Rave Mode (Headbang)**: An interactive visual stress system. If the user clicks like crazy, the engine enters overload and triggers visual effects ignoring any principle of ergonomics.
- **Geometric Transformer**: Rendering of three-dimensional polygons (Spheres and Toroids) calculated with pure trigonometry. No threads, no hardware acceleration, suffering on the main processor like it's 1993.
- **CRT & Glitch Effect**: Simulation of a cathode ray tube monitor with procedural scanlines and chromatic aberration to remind you that flat screens are a passing fad.
- **Tactical HUD**: Targeting system with mathematical SmoothStep smoothing. It's useless in an installer, but it looks spectacular.

### 🔊 Audio Engine (High Revs)
- **BPM Synchronization**: An internal musical clock that forces the visual engine to dance strictly to the beat.
- **Native Tracker Support**: Direct playback of classic Amiga modules (`.mod`, `.xm`, `.it`). If you don't know what FastTracker II is, you're missing out. Also plays `.mp3` if you're too lazy to find real music.
- **Robotic TTS**: An integrated voice synthesizer with stereo delay that speaks to you as if the computer were coming to life to reproach your operational decisions.

### 🛠️ Hardware Hijacking (Direct Intrusion)
- **Keyboard LED FX**: Direct and violent control of your physical keyboard bus. We make the `Caps`, `Num` and `Scroll Lock` LEDs flash in Knight Rider mode while files are copied. If your mechanical keyboard cost 200 euros, pray.
- **Deep Path Discovery**: Aggressive directory location by scanning hidden manifests in the Windows registry of **Steam** and **Epic Games**. We find the game even if you hid it in a forbidden partition.

---

📂 Architecture and Module Breakdown (Nut Tightening)
Let's change the table to show the weight of silicon in each script:

Module | Function in the Chassis
-------|------------------------
**main.py** | **The Crankshaft.** Main event loop, synchronization with the MusicClock and the state machine that prevents everything from exploding.
**config.py** | **The Octane.** Raw parameters, neon colors that damage the retina, and immutable mathematical constants.
**audio.py** | **The Air Intake.** Tracker module loading, low-level audio channel reservations, and the robot voice.
**effects.py** | **The Nitrous Oxide Injection.** Starfield, 3D transformations based on sines and cosines, and the CRT aberration engine.
**ui.py** | **The Bodywork.** ASCII logo rendering, the Tactical HUD, and the hexadecimal memory dump to scare the kids.
**installer.py** | **The Pistons.** Parallel execution threads to move files while the keyboard flashes and the music roars.
**utils.py** | **The Toolbox.** Dirty but necessary functions, resource paths, and the procedural failure generator.
**Compiler_GUIv2.py** | **The Hydraulic Press.** Monolithic OneFile executable generator using PyInstaller like a beast.

---

## 🚀 The Compiler (OneFile Factory)

The project includes **two compilation tools** to package the project into a single `.exe`:

1.  **Compiler_GUIv2.py**: Modern interface in `customtkinter` with Splash Screen generator, metadata editor, and icon converter.
2.  **compilador.py (CLI)**: Console version with ANSI colors for debugging and automation.

Recommended to use the GUI version for speed. The CLI version is in development.

---

## 🛠️ Installation and Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com
    cd metalwar-installer
Install dependencies:

bash
pip install pygame customtkinter pillow pyttsx3 numpy
Run in development mode:

bash
python main.py
Compile your own installer:

bash
python Compiler_GUIv2.py
Warranty
This installer comes with absolutely no warranty.
Except one.

If you open the source code...
You'll probably find at least one thing that makes you say:

"Huh... that's actually clever."
Finding which one is left as an exercise for the reader. 🎸

Workshop Log

v1.0 - This WAR is OVER!

The installer is stable. The code has been tamed.

v0.8 - Explosive Finale

Every spectacular ending needs a detonation. Added X-Wing fighters doing barrel rolls on the closing screen. Why? Because we could.

v0.6 - Enterprise Star Trek Mode

I watched Star Trek on TV, fell in love with the starfield, and the next day I was coding it. Now it's your visual problem.

v0.5 - Quantum Leap

It works better now and executes three times as many ridiculous tasks with half the effort.

v0.3 - The "Germin-IA" Incident

I felt lonely coding at 3 a.m. I programmed an experimental chatbot based on dog barks called Germin-IA. It doesn't compile well, it doesn't solve doubts, but it says absurd genius things!

v0.2 - The Miracle

It's still running. Nobody knows why. Don't touch the power cable.

v0.1 - First Ignition

It worked on the first try. This was considered highly suspicious by the mechanic team. Checking logs for witchcraft.

📻 Field Reports

All quotes published here are real. None have been edited to sound less funny. Some have been slightly edited for readability.

"It was a huge scare when the translation started installing and Caps Lock and Num Lock started turning on and off, ignoring that, the translation is really well done, there are some things in English but with the descriptions saying what they are about it's enough really" - Carzdroid

"The fact that it's a .exe file makes me distrust it, also Virus Total gave me a possible Trojan risk when reading the .exe, in the end I didn't test it but just so others know" - Sandov Metal responds: :steamthumbsup:, surely if you know how to use Virus Total, you know how to use a VM or a virtualized space to extract the files, for others it remains an .exe. For convenience and the author's vision. Regards

If you pass by Alcorcon let me know and I'll suck you off. - Artorias

Many thanks mate for bothering. - luferas

Could you make a tutorial for dummies (like me) on how to install it? I got it as a gift from Epic - wolfratable

A screen appears with Conan's music, but I don't know what to do next - @albertol2371

Virus detected it popped up! - @eze86ruiz

Sorry, could you upload a tutorial for the Epic version they gave away recently? I'm not a computer genius and I need steps to understand, I forgot what I said, praised be, and also warn that the translation program is a link through Steam to another place xd -HCreps

VERY PRETTY BUT HOW DO YOU TRANSLATE IT? - @haza-play/Metaltrollking say: PRESS THE BUTTON – THERE'S ONLY ONE TO CONTROL THEM ALL AND PLUNGE THEM INTO DARKNESS.

ESPAÑOL
========

█████████████████████████████████████████████████████████████████████████

Felicidades.

De alguna manera, has acabado leyendo la documentación de un instalador de Windows.
Esto ya plantea varias preguntas.
Se trata principalmente de tus decisiones de vida.

"No estoy construyendo un instalador. Estoy reaprendiendo a programar."

Requisitos
✔ Windows
✔ Un ratón que funcione
✔ Un ordenador con potencia similar a una cafetera.
✔ Fortaleza emocional para ver tu teclado convertirse en una discoteca

¿Qué es esto?
"Es un proyecto técnicamente innecesario ejecutado con un nivel de dedicación completamente desproporcionado."

Sobre el papel: Un instalador para Windows.
En realidad: Mi excusa para volver a tocar código después de demasiados años.

Python, Git, estructura de proyectos, documentación, automatización, versionado...

Lo aburrido.

Lo necesario.

MetalWar Installer no es solo un instalador de traducciones; es un tributo a la Demoscene de los 90. Un motor de despliegue genérico diseñado para distribuir parches y traducciones fanmade con una estética agresiva, visuales 3D en tiempo real y sincronización musical perfecta.

"Porque si vamos a distribuir la traducción fanmade de un juego, vamos a hacerlo con estilo, y dos cojones.🤘"

¿Por qué publicar algo tan pequeño?
Todo el mundo enseña la catedral acabada.
Casi nadie muestra los andamios.
Este repositorio son los andamios.
Verás cosas bien hechas.
Verás cosas que arreglo tres commits después.
Es parte del proceso.
Aprender deja huellas.

No las borro.

Misión
Convertir un instalador minúsculo en un campo de pruebas para aprender desarrollo profesional.
No con tutoriales interminables.
Construyendo.
Rompiendo.
Arreglando.
Escribiendo sobre ello.

Y repitiendo.

Arquitectura
El instalador ha sido cuidadosamente diseñado siguiendo décadas de
mejores prácticas de la industria.

Algunas de ellas.
Las importantes.
Bueno...
Más o menos. 🎸

¿Qué es una buena práctica?

Misión Secundaria
Aprender Git de verdad.

No "conocer lo justo para no cagarla, hasta que acabe ocurriendo."

Este repo será mi campo de entrenamiento para:

commits con sentido
ramas
fusiones
etiquetas
lanzamientos
pull requests
documentación
organización de proyectos

Estado del README
Este README está vivo.

Evolucionará tanto como el código.

Quizá más.

Si ves cambios raros...
Estás viendo a alguien aprender Markdown treinta años después de escribir documentación en texto plano.

Algunos empiezan con Markdown.
Otros con arte ASCII.

La vida es así.

Filosofía
Los programadores viejos tenían una manía.

En lugar de preguntar "¿Puede el ordenador hacer esto?"
preguntaban "¿Cómo puedo convencer al ordenador de que haga esto?"

Esa mentalidad nunca dejó de molar.

La optimización no es obsesión. Es curiosidad.
La documentación no es burocracia. Es respeto por tu yo futuro.
El código limpio no es postureo. Es amabilidad.

Aviso
Este repositorio contiene niveles peligrosos de entusiasmo.

Posibles efectos secundarios:

reorganizar carpetas que ya estaban bien
renombrar variables porque "quedan mejor"
añadir comentarios que nadie pidió
reescribir documentación a las 2 a.m.
pasar más tiempo en el README que en el código

Todo normal, puedes continuar tu viaje.

## 🕹️ Características Principales (Sobreingeniería Certificada)
💎 Visuales Demoscene (Porque el rendimiento es temporal, pero el estilo es eterno)
Starfield 3D Fuera de Control: Un campo de estrellas con rotación de cámara tipo barrel roll y efecto warp reactivo al BPM que consume más CPU de la que la NASA usó para llegar a la Luna.

Visualizadores Adaptativos: El motor gráfico interroga al codec de audio en tiempo real. Si cambias la pista tracker, el sistema conmuta sus matrices de renderizado sobre la marcha.

Rave Mode (Headbang): Un sistema de estrés visual interactivo. Si el usuario hace clic como un loco, el motor entra en sobrecarga y dispara los efectos visuales ignorando cualquier principio de ergonomía.

Geometric Transformer: Renderizado de polígonos tridimensionales (Esferas y Toroides) calculados a base de pura trigonometría a pelo. Sin hilos, sin aceleración por hardware, sufriendo en el procesador principal como en 1993.

Efecto CRT & Glitch: Simulación de monitor de tubo de rayos catódicos con scanlines procedurales y aberración cromática para recordarte que los monitores planos son una moda pasajera.

Tactical HUD: Sistema de targeting con suavizado matemático SmoothStep. No sirve para nada en un instalador, pero queda espectacular.

🔊 Motor de Audio (Altas Revoluciones)
Sincronización BPM: Un reloj musical interno que obliga al motor visual a bailar al ritmo del bit de forma estricta.

Soporte Tracker Nativo: Reproducción directa de módulos clásicos de la Amiga (.mod, .xm, .it). Si no sabes qué es el FastTracker II, te falta taller. También reproduce .mp3 si te da pereza buscar música de verdad.

Robotic TTS: Un sintetizador de voz integrado con delay estéreo que te habla como si el ordenador estuviera cobrando vida para recriminarte tus decisiones operativas.

🛠️ Hardware Hijacking (Intrusión Directa)
Keyboard LED FX: Control directo y violento del bus de tu teclado físico. Ponemos a parpadear los LEDs de Caps, Num y Scroll Lock en modo Coche Fantástico mientras se copian los archivos. Si tu teclado mecánico costó 200 euros, reza.

Deep Path Discovery: Localización agresiva de directorios mediante el escaneo de manifiestos ocultos en el registro de Windows de Steam y Epic Games. Encontramos el juego aunque lo hayas escondido en una partición prohibida.

📂 Arquitectura y Desglose por Módulos (Ajuste de Tuercas)
Cambiemos la tabla para que se note el peso del silicio en cada script:

Módulo	Función en el Chasis
main.py	El Cigüeñal. Bucle de eventos principal, sincronización con el MusicClock y la máquina de estados que evita que todo explote.
config.py	El Octanaje. Parámetros en bruto, colores neón que dañan la retina y constantes matemáticas inmutables.
audio.py	La Admisión de Aire. Carga de módulos tracker, reservas de canales de audio a bajo nivel y la voz del robot.
effects.py	La Inyección de Óxido Nitroso. Starfield, transformaciones 3D a base de senos y cosenos, y el motor de aberración CRT.
ui.py	La Carrocería. Renderizado del logo ASCII, el Tactical HUD y el volcado de memoria en hexadecimal para asustar a los niños.
installer.py	Los Pistones. Hilos de ejecución en paralelo para mover los archivos mientras el teclado parpadea y la música ruge.
utils.py	La Caja de Herramientas. Funciones sucias pero necesarias, rutas de recursos y el generador de fallos procedurales.
Compiler_GUIv2.py	La Prensa Hidráulica. Generador de ejecutables monolíticos OneFile usando PyInstaller a lo bestia.
🚀 El Compilador (Fábrica de OneFiles)
El proyecto incluye dos herramientas de compilación para empaquetar el proyecto en un único .exe:

Compiler_GUIv2.py: Interfaz moderna en customtkinter con generador de Splash Screens, editor de metadatos y conversión de iconos.

compilador.py (CLI): Versión de consola con colores ANSI para debugging y automatización.

Recomendable usar la versión GUI para ir rápido. La versión CLI está en desarrollo.

🛠️ Instalación y Uso
Clonar el repositorio:

bash
git clone https://github.com
cd metalwar-installer
Instalar dependencias:

bash
pip install pygame customtkinter pillow pyttsx3 numpy
Ejecutar en modo desarrollo:

bash
python main.py
Compilar tu propio instalador:

bash
python Compiler_GUIv2.py
Garantía
Este instalador no tiene absolutamente ninguna garantía.
Excepto una.

Si abres el código fuente...
Probablemente encontrarás al menos una cosa que te haga decir:

"Eh... eso sí que es ingenioso."
Descubrir cuál es se deja como ejercicio para el lector. 🎸

Workshop Log

v1.0 - This WAR is OVER!

El instalador es estable. El código ha sido domado.

v0.8 - Explosive Finale

Cada final espectacular necesita una detonación. Añadidos cazas X-Wing haciendo barrel rolls en la pantalla de cierre. ¿Por qué? Porque podíamos.

v0.6 - Enterprise Star Trek Mode

Vi Star Trek por la tele, me enamoré del campo de estrellas y al día siguiente estaba picado en el código. Ahora es tu problema visual.

v0.5 - Quantum Leap

Ahora funciona mejor y ejecuta tareas el triple de ridículas con la mitad de esfuerzo.

v0.3 - The "Germin-IA" Incident

Me sentía solo picando a las tres de la madrugada. Programé un chatbot experimental basado en ladridos de perro llamado Germin-IA. No compila bien, no resuelve dudas, ¡pero dice genialidades absurdas!.

v0.2 - The Miracle

Sigue funcionando. Nadie sabe por qué. No toques el cable de alimentación.

v0.1 - First Ignition

Funcionó a la primera. Esto fue considerado altamente sospechoso por el equipo de mecánicos. Revisando registros en busca de brujería.

📻 Field Reports

Todas las citas aquí publicadas son reales. Ninguna ha sido editada para que suene menos graciosa. Algunos han sido ligeramente editados para facilitar su lectura.

"Fue un susto tremendo cuando al instalar la traducción empezó a activarse y desactivarse el caps lock y el num lock, ignorando eso, la traducción está super bien hecha, hay algunas cositas en inglés pero con las descripciones diciendo de que se tratan es suficiente la verdad" - Carzdroid

"Que sea .exe el archivo me genera desconfianza, además virus total me tiró posible riesgo de troyano al leer el .exe, al final no lo probé pero solo para que lo tengan en cuenta los demás" - Sandov Metal responde: :steamthumbsup:, seguro que si sabes usar virustotal, sabes usar una vm o un espacio virtualizado para extraer los archivos, para los demás se queda como un exe. Por comodidad y por visión del autor. Un saludo

Si pasas por alcorcon avisa y te la chupo. - Artorias

Muchísimas gracias crack por molestarte. - luferas

Podrías hacer un tuto para tontos (como yo) de como instalarlo? Lo tengo de regalo de epic - wolfratable

Me sale una pantalla con la música de Conan, pero no sé qué hay que hacer después - @albertol2371

virus detectado me salto! - @eze86ruiz

disculpe no podrá subir un tutorial para la versión de epic que regalo hace poco? no soy un genio de la informática y necesito pasos para entender, olvide lo que dije alabado sea y de paso avise que el programa de traducción es un link a través de steam a otro lado xd -HCreps

MUY LINDO TODO PERO, CÓMO SE TRADUCE ?- @haza-play/Metal say: PRESS THE BUTTON – THERE'S ONLY ONE TO CONTROL THEM ALL AND PLUNGE THEM INTO DARKNESS.