import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = [
    "qrcode[pil]",
    "pillow"
]

# Instalar pacotes Python
for package in required_packages:
    install(package)

# Instalar FFmpeg
install_ffmpeg()

print("Todos os pacotes necessários foram instalados com sucesso!")
