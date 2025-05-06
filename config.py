from dotenv import load_dotenv
import os

# Cargar el archivo .env
load_dotenv()

# Verificar que se carga correctamente
BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    print("No se pudo cargar el token desde el archivo .env en Termux")
else:
    print(f"TOKEN cargado: {BOT_TOKEN}")

