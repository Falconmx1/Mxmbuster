# Colores ANSI
R = '\033[91m'   # Rojo
G = '\033[92m'   # Verde
Y = '\033[93m'   # Amarillo
B = '\033[94m'   # Azul
M = '\033[95m'   # Morado
C = '\033[96m'   # Cyan
W = '\033[97m'   # Blanco
RS = '\033[0m'   # Reset

def banner():
    print(f"""
{R}    ⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣶⣶⣤⣀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⢀⣴⠟⠋⠁⠀⠀⠈⠙⢿⣦⡀⠀⠀⠀
    ⠀⠀⠀⣴⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠻⣷⡀⠀⠀
    ⠀⠀⣼⡟⠀⠀⢠⣴⠟⠛⠻⢶⣄⠀⠀⢻⣧⠀⠀
    ⠀⢸⣿⠁⠀⠀⢿⣀⣀⣀⣀⡀⠿⠇⠀⠀⣿⡇⠀
    ⠀⢸⣿⠀⠀⠀⠀⠉⠉⠉⠉⠉⠀⠀⠀⠀⣿⡇⠀
    ⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠃⠀
    ⠀⠀⠸⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⠏⠀⠀
    ⠀⠀⠀⠙⣿⣄⠀⠀⠀⠀⠀⠀⠀⣠⣾⠋⠀⠀⠀
    ⠀⠀⠀⠀⠈⠻⣷⣦⣤⣤⣤⣴⣾⠟⠁⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀{RS}

{C}    █▀▄▀█ █ █▀▀   █▀▄▀█ █ █▀█ █▄░█ █▀▀ █▀█ █▄█
    █░▀░█ █ █▄▄   █░▀░█ █ █▄█ █░▀█ ██▄ █▀▄ ░█░{RS}

{M}    🧨 Mxmbuster v2.0 - Rompiendo el silencio de la red 🧨
{G}    🐉 Modo OFENSIVO | Threads: Dinámico | Resultados guardados
{Y}    🔥 Codificado con sangre, sudor y frijolitos 🔥{RS}
{C}    ════════════════════════════════════════════════════{RS}
    """)
