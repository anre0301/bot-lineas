from config import *  # Asegúrate que aquí está tu BOT_TOKEN
import telebot
import json
import os
import re
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

def es_seller(user_id):
    print(f"Verificando seller para el user_id: {user_id}")  # Agrega esta línea para depurar
    return user_id in sellers
    
# Cargar los sellers desde el archivo JSON
def cargar_sellers():
    try:
        with open('sellers.json', 'r') as f:
            data = json.load(f)
        return data.get('sellers', [])
    except FileNotFoundError:
        return []   

# Guardar sellers en archivo
def guardar_sellers():
    with open("sellers.json", "w") as f:
        json.dump({'sellers': sellers}, f, indent=4)

# Cargar los sellers al inicio del programa
sellers = cargar_sellers()

bot = telebot.TeleBot(BOT_TOKEN)

creditos_usuarios = {}

# Cargar los créditos de los usuarios
def cargar_creditos():
    global creditos_usuarios
    try:
        with open("creditos.json", "r") as f:
            creditos_usuarios = json.load(f)
    except FileNotFoundError:
        creditos_usuarios = {}

# Guardar créditos de los usuarios
def guardar_creditos():
    with open("creditos.json", "w") as f:
        json.dump(creditos_usuarios, f)


# Cargar los créditos al inicio
cargar_creditos()

GROUP_CHAT_ID = -1002658121599  # Tu grupo con temas activados
ADMIN_USER_ID = 7819787342

# Diccionarios para seguimiento
user_message_ids = {}

# Cargar datos si existen
if os.path.exists("user_data.json"):
    with open("user_data.json", "r") as f:
        data = json.load(f)
        user_topics = {int(k): v for k, v in data.get("topics", {}).items()}
        user_registration_date = {int(k): v for k, v in data.get("registration", {}).items()}
else:
    user_topics = {}
    user_registration_date = {}

# Guardar los datos en archivo JSON
def guardar_datos():
    with open("user_data.json", "w") as f:
        json.dump({
            "topics": user_topics,
            "registration": user_registration_date
        }, f)
def reenviar_mensaje(message):
    try:
        user_id = message.from_user.id
        if user_id in user_topics:
            thread_id = user_topics[user_id]

            respuesta_automatica = ""
            if message.text.startswith("/"):
                # Si el mensaje es un comando, busca si hay una respuesta automática conocida
                if message.text.startswith("/me"):
                    respuesta_automatica = "📋 Mostrando perfil del usuario"
                elif message.text.startswith("/planes"):
                    respuesta_automatica = "📜 Mostrando los planes disponibles"
                elif message.text.startswith("/buy"):
                    respuesta_automatica = "🛒 Mostrando instrucciones de compra"
                elif message.text.startswith("/cmds"):
                    respuesta_automatica = "📚 Mostrando todos los comandos"
                elif message.text.startswith("/register"):
                    respuesta_automatica = "👤 Registro del usuario solicitado"
                # Puedes agregar más comandos según sea necesario

            texto = f"📩 *{message.from_user.first_name}*: {message.text}"
            if respuesta_automatica:
                texto += f"\n🤖 *Respuesta automática:* {respuesta_automatica}"

            sent = bot.send_message(
                GROUP_CHAT_ID,
                texto,
                parse_mode="Markdown",
                message_thread_id=thread_id
            )
            user_message_ids[sent.message_id] = user_id
        else:
            bot.send_message(user_id, "⚠️ Aún no estás registrado. Usa /register para crear tu carpeta.")
            print(f"No se encontró tema para el usuario {user_id}.")
    except Exception as e:
        print(f"Error al reenviar mensaje: {e}")
        
@bot.message_handler(func=lambda message: message.chat.id == GROUP_CHAT_ID and message.message_thread_id is not None)
def responder_desde_tema(message):
    try:
        thread_id = message.message_thread_id
        user_id = None

        # Buscar el usuario que tiene este thread_id
        for uid, tid in user_topics.items():
            if tid == thread_id:
                user_id = uid
                break

        if user_id:
            # Enviar solo el contenido del mensaje sin encabezado
            bot.send_message(user_id, message.text)
        else:
            print("⚠️ No se encontró el usuario asociado al tema.")

    except Exception as e:
        print(f"Error al responder desde el tema: {e}")

@bot.message_handler(commands=['bamv', 'block'])
def cmd_bamv_or_block(message):
    user_id = str(message.from_user.id)

    # Extraer los argumentos después del comando
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(user_id, "❌ Debes ingresar un número. Ejemplo: /bamv 987654321")
        return

    numero = args[1]
    if not re.fullmatch(r"9\d{8}", numero):
        bot.send_message(user_id, "❌ El número debe empezar con 9 y tener 9 dígitos.")
        return

    if user_id not in creditos_usuarios or creditos_usuarios[user_id] <= 0:
        bot.send_message(user_id, "❌ No tienes saldo suficiente.")
        return

    creditos_usuarios[user_id] -= 1
    guardar_creditos()

    bot.send_message(user_id,
    f"✅ El número {numero} ha sido registrado exitosamente 💀\n\n"
    "⏳ Tiempo de espera: 10 - 25 min ...\n\n"
    "⚠️ 𝚁𝚎𝚌𝚞𝚎𝚛𝚍𝚊 𝚚𝚞𝚎 𝚗𝚘 𝚑𝚊𝚢 𝚍𝚎𝚟𝚘𝚕𝚞𝚌𝚒ó𝚗 𝚍𝚎 𝚌𝚛é𝚍𝚒𝚝𝚘𝚜 ⚠️"
)



    reenviar_mensaje(message)



@bot.message_handler(commands=['register'])
def cmd_register(message):
    try:
        user = message.from_user
        user_id = user.id
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        full_name = (first_name + " " + last_name).strip() or "usuario"
        username = f"@{user.username}" if user.username else "Sin username"
        language = user.language_code or "No especificado"
        language_flag = "🇪🇸" if language == "es" else "🌐"

        if user_id in user_topics:
            bot.send_message(
                user_id,
                f"⚠️ Hola {full_name}, ya estás registrado en el sistema.\n"
                f"Usa /me para ver tu perfil."
            )
            return

        # Crear un nuevo tema con el nombre del usuario
        thread = bot.create_forum_topic(GROUP_CHAT_ID, name=full_name)

        # Guardamos los datos
        user_topics[user_id] = thread.message_thread_id
        user_registration_date[user_id] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        guardar_datos()

        # Enviamos mensaje de bienvenida al thread
        bot.send_message(
            GROUP_CHAT_ID,
            f"• ID: `{user.id}`\n"
            f"• Nombre: {full_name}\n"
            f"• @Username: {username}\n"
            f"• Idioma: {language} {language_flag}\n"
            f"#id{user.id}",
            parse_mode="Markdown",
            message_thread_id=thread.message_thread_id
        )

        # Enviamos mensaje privado al usuario
        texto = (
            f"➣ 𝗕𝗜𝗘𝗡𝗩𝗘𝗡𝗜𝗗𝗢, {full_name}\n\n"
            "📍 Bienvenido a ⟦ 𝗣𝗵𝗼𝗻𝗲 𝗕𝗹𝗼𝗰𝗸 ⟧\n"
            "𝘌𝘭 𝘤𝘦𝘯𝘵𝘳𝘰 𝘥𝘰𝘯𝘥𝘦 𝘭𝘢 𝘪𝘯𝘧𝘰𝘳𝘮𝘢𝘤𝘪ó𝘯 𝘴𝘦 𝘷𝘶𝘦𝘭𝘷𝘦 𝘱𝘰𝘥𝘦𝘳.\n\n"
            "𝗕𝗶𝗲𝗻𝘃𝗲𝗻𝗶𝗱𝗼 𝗮 𝘂𝗻 𝘀𝗶𝘀𝘁𝗲𝗺𝗮 𝗱𝗲𝘀𝗮𝗿𝗿𝗼𝗹𝗹𝗮𝗱𝗼 𝗽𝗮𝗿𝗮 𝗽𝗲𝗿𝘀𝗼𝗻𝗮𝘀 𝗾𝗻 𝗕𝗨𝗦𝗖𝗔𝗡 𝗥𝗔𝗣𝗜𝗗𝗘𝗭 𝗬 𝗣𝗥𝗘𝗖𝗜𝗦𝗜Ó𝗡.\n\n"
            "🔥 𝐄𝐱𝐩𝐥𝐨𝐫𝐚 𝐥𝐚𝐬 𝐨𝐩𝐜𝐢𝐨𝐧𝐞𝐬 𝐝𝐢𝐬𝐩𝐨𝐧𝐢𝐛𝐥𝐞𝐬 𝐲 𝐝𝐞𝐬𝐜𝐮𝐛𝐫𝐞 𝐥𝐨 𝐪𝐮𝐞 𝐧𝐞𝐜𝐞𝐬𝐢𝐭𝐚𝐬 𝐞𝐧 𝐜𝐮𝐞𝐬𝐭𝐢𝐨́𝐧 𝐝𝐞 𝐬𝐞𝐠𝐮𝐧𝐝𝐨𝐬 🔥\n\n"
            "💻 𝗕𝘆: @SERVICIOSALBERTPE"
        )
        imagen_url = "https://i.ibb.co/BVwh22Lj/test.jpg"
        bot.send_photo(user_id, imagen_url, caption=texto)

    except Exception as e:
        print(f"Error en /register: {e}")
    
@bot.message_handler(commands=['me'])
def cmd_me(message):
    try:
        reenviar_mensaje(message)

        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name or "Usuario"
        username = f"@{message.from_user.username}" if message.from_user.username else "No disponible"

        # Cargar sellers
        try:
            with open("sellers.json", "r") as f:
                sellers_data = json.load(f)
                lista_sellers = [str(i) for i in sellers_data.get("sellers", [])]
        except FileNotFoundError:
            lista_sellers = []

        # Cargar la fecha de registro desde user_data.json
        try:
            with open("user_data.json", "r") as f:
                user_data = json.load(f)
                registro_completo = user_data.get("registration", {}).get(user_id, None)
                if registro_completo:
                    fecha_registro = registro_completo.split(" ")[0]  # Solo la fecha (YYYY-MM-DD)
                else:
                    fecha_registro = "No registrado aún"
        except FileNotFoundError:
            fecha_registro = "No registrado aún"

        estado = "REGISTRADO"
        creditos = creditos_usuarios.get(user_id, 0)
        rol = "👑 SELLER" if user_id in lista_sellers else "CLIENTE"

        texto_me = (
            "[#𝗣𝗛𝗢𝗡𝗘_𝗕𝗟𝗢𝗖𝗞 v1.0] ➾ ME - PERFIL\n\n"
            f"PERFIL DE ➾ *{first_name}*\n\n"
            "INFORMACIÓN PERSONAL\n\n"
            f"[🆔] 𝗜𝗗 ➾ `{user_id}`\n"
            f"[👨🏻‍💻] 𝗨𝗦𝗘𝗥 ➾ {username}\n"
            f"[🚨] 𝗘𝗦𝗧𝗔𝗗𝗢 ➾ {estado}\n"
            f"[📅] 𝗙. 𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗢 ➾ {fecha_registro}\n"
            f"[💰] 𝗕𝗟𝗢𝗤𝗨𝗘𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦 ➾ {creditos}\n"
            f"[〽️] 𝗥𝗢𝗟 ➾ {rol}"
        )

        bot.send_photo(
            message.chat.id,
            photo="https://ibb.co/BVwh22Lj",
            caption=texto_me,
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")
        


@bot.message_handler(commands=['buy'])
def cmd_buy(message):
    try:
        # Texto del mensaje con formato
        texto_compra = (
            "⚡ 𝗥𝗲𝗮𝗹𝗶𝘇𝗮 𝗲𝗹 𝗽𝗮𝗴𝗼 𝗲𝗻 𝗲𝗹 𝘀𝗶𝗴𝘂𝗶𝗲𝗻𝘁𝗲 𝗤𝗥, {0}, 𝗮 𝗻𝗼𝗺𝗯𝗿𝗲 𝗱𝗲 𝗜𝘇𝗶*𝗦𝗲𝗿𝘃𝗶𝗰𝗶𝗼𝘀𝗔𝗹𝗯𝗲𝗿𝘁\n\n"
            "⟦🔰⟧ Recuerda colocar el plan que vas a elegir\n\n"
            "⟦🔰⟧ Recuerda colocar el monto exacto ya que no hay devolución\n\n"
            "⟦🔰⟧ Una vez realizado el pago recuerda poner el comando /block o /bamv seguido con el número y solicitarle al bot el bloqueo\n\n"
            "⟦❗⟧ 𝗖𝘂𝗮𝗹𝗾𝘂𝗶𝗲𝗿 𝗱𝘂𝗱𝗮, 𝗿𝗲𝗰𝗹𝗮𝗺𝗼 𝗼 𝗶𝗻𝗰𝗼𝗻𝘃𝗲𝗻𝗶𝗲𝗻𝘁𝗲 𝗿𝗲𝘀𝗽𝗲𝗰𝘁𝗼 𝗮𝗹 𝗽𝗮𝗴𝗼, 𝗯𝗹𝗼𝗾𝘂𝗲𝗼 𝗲𝗻𝘁𝗿𝗲 𝗼𝘁𝗿𝗮𝘀..."
        ).format(message.from_user.first_name)

        # Imagen (si es desde enlace directo)
        imagen_url = "https://ibb.co/kgdXWyBG"  # Asegúrate de usar el enlace directo a la imagen (termina en .png, .jpg, etc.)

        # Crear botón
        markup = InlineKeyboardMarkup()
        boton = InlineKeyboardButton("🐺 SERVICIOS ALBERT PE 🐺", url="https://t.me/serviciosalbertpe")
        markup.add(boton)

        # Enviar imagen con caption + botón debajo
        bot.send_photo(message.chat.id, photo=imagen_url, caption=texto_compra, reply_markup=markup)

        # Opcional: reenviar el mensaje al grupo
        reenviar_mensaje(message)

    except Exception as e:
        print(f"Error en /buy: {e}")

@bot.message_handler(commands=['planes'])
def cmd_planes(message):
    try:
        # Definir el texto para el comando /planes
        texto_planes = (
            "💰 𝐏𝐋𝐀𝐍𝐄𝐒 - {0}\n\n"
            "📍️ LINEA + EQUIPO\n\n"
            "🔅 1 bloqueo ➣️ S/ 13\n"
            "🔅 2 bloqueos ➣ S/ 20\n"
            "🔅 3 bloqueos ➣ S/ 30\n\n"
            "📍 𝐁𝐀𝐍𝐂𝐀 𝐘 𝐓𝐀𝐑𝐉𝐄𝐓𝐀𝐒\n\n"
            "🔅 1 bloqueo ➣ S/ 25\n"
            "🔅 2 bloqueos ➣ S/ 30\n"
            "🔅 3 bloqueos ➣ S/ 45\n\n"
            "✏️ 𝗦𝗼𝗹𝗼 𝗽𝘂𝗲𝗱𝗲𝘀 𝗿𝗲𝗮𝗹𝗶𝘇𝗮𝗿 𝟯 𝗯𝗹𝗼𝗾𝘂𝗲𝗼𝘀 𝗮𝗹 𝗱𝗶́𝗮...\n"
            "𝗨𝘀𝗮 𝗲𝗹 𝗰𝗼𝗺𝗮𝗻𝗱𝗼 /buy 𝗽𝗮𝗿𝗮 𝗮𝗱𝗾𝘂𝗶𝗿𝗶𝗿 𝗲𝗹 𝗯𝗹𝗼𝗾𝘂𝗲𝗼, 𝗿𝗲𝗰𝘂𝗲𝗿𝗱𝗮 𝗽𝗼𝗻𝗲𝗿 𝗯𝗶𝗲𝗻 𝗲𝗹 𝗺𝗼𝗻𝘁𝗼"
            
        ).format(message.from_user.first_name)  # Incluye el nombre del usuario

        # Enviar la imagen y el texto
        imagen_url = "https://ibb.co/BVwh22Lj"
        bot.send_photo(message.chat.id, imagen_url, caption=texto_planes)
        
        # ⬅️ Esta línea agrega el reenvío del comando al grupo
        reenviar_mensaje(message)
        
    except Exception as e:
        print(f"Error en /planes: {e}")

@bot.message_handler(commands=['cmds'])
def cmd_cmds(message):
    try:
        # Definir el texto de los comandos
        comandos = (
            "𝗖𝗢𝗠𝗔𝗡𝗗𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦\n\n"
            "[#phoneblocking_bot]\n\n"
            "Categoria : 𝐁𝐋𝐎𝐐𝐔𝐄𝐎 [🛡]\n"
            "=====================\n\n"
            "[📌] 𝐁𝐋𝐎𝐐𝐔𝐄𝐎 𝐃𝐄 𝐋𝐈𝐍𝐄𝐀𝐒\n"
            "-------------------------\n"
            "🚀 Uso: /block <número>\n"
            "💰 Consumo: 15 soles\n\n"
            "👉 𝗕𝗹𝗼𝗾𝘂𝗲𝗼 𝗱𝗲 𝗰𝘂𝗮𝗹𝗾𝘂𝗶𝗲𝗿 𝘁𝗶𝗽𝗼 𝗱𝗲 𝗼𝗽𝗲𝗿𝗮𝗱𝗼𝗿 𝘁𝗲𝗹𝗲𝗳𝗼́𝗻𝗶𝗰𝗼 𝗱𝗲𝗹 𝗣𝗲𝗿𝘂́\n\n"
            "==============================\n\n"
            "[📌] 𝐁𝐋𝐎𝐐𝐔𝐄𝐎 𝐃𝐄 𝐁𝐀𝐍𝐂𝐀 𝐌𝐎𝐕𝐈𝐋\n"
            "-------------------------\n"
            "🚀 Uso: /bamv <número>\n"
            "💰 Consumo: 20 soles\n\n"
            "👉 𝗕𝗹𝗼𝗾𝘂𝗲𝗼 𝗱𝗲 𝗹𝗮 𝗯𝗮𝗻𝗰𝗮 𝗺𝗼́𝘃𝗶𝗹 \"𝗬𝗮𝗽𝗲\" 𝗰𝗼𝗻 𝘀𝗼𝗹𝗼 𝗲𝗹 𝗻𝘂́𝗺𝗲𝗿𝗼 𝗱𝗲 𝗰𝗲𝗹𝘂𝗹𝗮𝗿\n\n"
            "==============================\n\n"
           "⚠ 𝙻𝚘𝚜 𝚌𝚘𝚖𝚊𝚗𝚍𝚘𝚜 𝚜𝚎 𝚑𝚊𝚋𝚒𝚕𝚒𝚝𝚊𝚛𝚊́𝚗 𝚊𝚞𝚝𝚘𝚖𝚊𝚝𝚒𝚌𝚊𝚖𝚎𝚗𝚝𝚎 𝚍𝚎𝚜𝚙𝚞𝚎𝚜 𝚍𝚎 𝚑𝚊𝚋𝚎𝚛 𝚛𝚎𝚊𝚕𝚒𝚣𝚊𝚍𝚘 𝚎𝚕 𝚙𝚊𝚐𝚘 ⚠"
        )
        # Enviar primero la imagen
        imagen_url = "https://ibb.co/BVwh22Lj"
        bot.send_photo(message.chat.id, imagen_url, caption=comandos)
        
         # ⬅️ Esta línea agrega el reenvío del comando al grupo
        reenviar_mensaje(message)
        
    except Exception as e:
        print(f"Error en /cmds: {e}")
        
@bot.message_handler(commands=['block'])
def cmd_block(message):
    try:
        partes = message.text.strip().split()
        if len(partes) == 2 and re.fullmatch(r"9\d{8}", partes[1]):  # Valida que empiece con '9' y tenga 9 dígitos
            respuesta = (
                "➣ 𝕊𝕠𝕝𝕚𝕔𝕚𝕥𝕦𝕕 𝕖𝕟𝕧𝕚𝕒𝕕𝕒 𝕔𝕠𝕟 𝕖́𝕩𝕚𝕥𝕠 ✅\n\n"
                "⚠ 𝚁𝚎𝚌𝚞𝚎𝚛𝚍𝚊 𝚚𝚞𝚎 𝚜𝚒 𝚎𝚕 𝚙𝚊𝚐𝚘 𝚗𝚘 𝚜𝚎 𝚑𝚊 𝚎𝚏𝚎𝚌𝚝𝚞𝚊𝚍𝚘, 𝚕𝚊 𝚜𝚘𝚕𝚒𝚌𝚒𝚝𝚞𝚍 𝚚𝚞𝚎𝚍𝚊 𝚛𝚎𝚌𝚑𝚊𝚣𝚊𝚍𝚊 𝚊𝚞𝚝𝚘𝚖𝚊́𝚝𝚒𝚌𝚊𝚖𝚎𝚗𝚝𝚎 ⚠"
            )
            bot.send_message(message.chat.id, respuesta)

            # Reenviar al hilo correspondiente del grupo (opcional)
            reenviar_mensaje(message)
        else:
            bot.send_message(message.chat.id, "❗ Usa el comando así: /block 999999999 (9 dígitos)")
    except Exception as e:
        print(f"Error en /block: {e}")
        
@bot.message_handler(commands=['bamv'])
def cmd_bamv(message):
    try:
        partes = message.text.strip().split()
        if len(partes) == 2 and re.fullmatch(r"9\d{8}", partes[1]):  # Valida que empiece con '9' y tenga 9 dígitos
            respuesta = (
                "➣ 𝕊𝕠𝕝𝕚𝕔𝕚𝕥𝕦𝕕 𝕖𝕟𝕧𝕚𝕒𝕕𝕒 𝕔𝕠𝕟 𝕖́𝕩𝕚𝕥𝕠 ✅\n\n"
                "⚠ 𝚁𝚎𝚌𝚞𝚎𝚛𝚍𝚊 𝚚𝚞𝚎 𝚜𝚒 𝚎𝚕 𝚙𝚊𝚐𝚘 𝚗𝚘 𝚜𝚎 𝚑𝚊 𝚎𝚏𝚎𝚌𝚝𝚞𝚊𝚍𝚘, 𝚕𝚊 𝚜𝚘𝚕𝚒𝚌𝚒𝚝𝚞𝚍 𝚚𝚞𝚎𝚍𝚊 𝚛𝚎𝚌𝚑𝚊𝚣𝚊𝚍𝚊 𝚊𝚞𝚝𝚘𝚖𝚊́𝚝𝚒𝚌𝚊𝚖𝚎𝚗𝚝𝚎 ⚠"
            )
            bot.send_message(message.chat.id, respuesta)

            # Reenviar al hilo correspondiente del grupo (opcional)
            reenviar_mensaje(message)
        else:
            bot.send_message(message.chat.id, "❗ Usa el comando así: /bamv 999999999 (9 dígitos)")
    except Exception as e:
        print(f"Error en /bamv: {e}")
        
# Comando /sub
@bot.message_handler(commands=['sub'])
def cmd_sub(message):
    user_id = message.from_user.id

    # Verificar si el usuario es el admin o un seller
    if user_id != ADMIN_USER_ID and user_id not in sellers:
        bot.reply_to(message, "🚫 No estás autorizado para usar este comando.")
        return

    try:
        # Intentar dividir el mensaje en 3 partes (comando /sub, ID, cantidad)
        _, user_id_str, cantidad_str = message.text.split()

        # Validar que el user_id es un número válido (asegurándonos de que es un string de ID)
        user_id = str(user_id_str)

        # Validar que la cantidad sea un número entero positivo
        cantidad = int(cantidad_str)
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser un número positivo.")

        # Agregar créditos al usuario
        creditos_usuarios[user_id] = creditos_usuarios.get(user_id, 0) + cantidad
        guardar_creditos()

        # Confirmación de la acción
        bot.reply_to(message, f"✅ Se han agregado {cantidad} créditos al usuario {user_id}. Total: {creditos_usuarios[user_id]}")

    except ValueError as ve:
        bot.reply_to(message, f"⚠️ Error en el formato o valor del comando. {str(ve)}")
    except IndexError:
        bot.reply_to(message, "⚠️ Error: Formato incorrecto. Uso correcto: /sub ID CANTIDAD")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error desconocido: {str(e)}")


@bot.message_handler(commands=['unsub'])
def cmd_sub(message):
    user_id = message.from_user.id

    # Verificar si el usuario es el admin o un seller
    if user_id != ADMIN_USER_ID and user_id not in sellers:
        bot.reply_to(message, "🚫 No estás autorizado para usar este comando.")
        return

    try:
        # Intentar dividir el mensaje en 3 partes
        _, user_id_str, cantidad_str = message.text.split()
        
        # Validar que el user_id es un número válido
        user_id = str(user_id_str)
        
        # Validar que la cantidad sea un número entero positivo
        cantidad = int(cantidad_str)
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser un número positivo.")

        # Descontar créditos al usuario (no permitiendo que el saldo sea negativo)
        creditos_usuarios[user_id] = max(0, creditos_usuarios.get(user_id, 0) - cantidad)
        guardar_creditos()

        # Confirmación de la acción
        bot.reply_to(message, f"✅ Se han descontado {cantidad} créditos al usuario {user_id}. Total: {creditos_usuarios[user_id]}")

    except ValueError as ve:
        bot.reply_to(message, f"⚠️ Error en el formato o valor del comando. {str(ve)}")
    except IndexError:
        bot.reply_to(message, "⚠️ Error: Formato incorrecto. Uso correcto: /unsub ID CANTIDAD")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error desconocido: {str(e)}")


@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    user_mention = f"[{user.first_name}](tg://user?id={user.id})"

    texto = (
        f"🎉 𝐁𝐈𝐄𝐍𝐕𝐄𝐍𝐈𝐃𝐎, {user_mention}\n\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚  ► 𝐏𝐇𝐎𝐍𝐄 𝐁𝐋𝐎𝐂𝐊𝐈𝐍𝐆 ◄\n\n"
        "🔎 𝐆𝐔𝐈𝐀\n\n"
        "➣ /register — 𝐂𝐫𝐞𝐚 𝐭𝐮 𝐢𝐝𝐞𝐧𝐭𝐢𝐝𝐚𝐝 𝐞𝐧 𝐧𝐮𝐞𝐬𝐭𝐫𝐚 𝐜𝐨𝐦𝐮𝐧𝐢𝐝𝐚𝐝\n"
        "➣ /cmds — 𝐀𝐜𝐜𝐞𝐝𝐞 𝐚 𝐥𝐨𝐬 𝐜𝐨𝐦𝐚𝐧𝐝𝐨𝐬 𝐝𝐢𝐬𝐩𝐨𝐧𝐢𝐛𝐥𝐞𝐬\n"
        "➣ /me — 𝐓𝐮𝐬 𝐝𝐚𝐭𝐨𝐬 𝐞 𝐢𝐧𝐟𝐨𝐫𝐦𝐚𝐜𝐢𝐨́𝐧 𝐩𝐞𝐫𝐬𝐨𝐧𝐚𝐥\n"
        "➣ /buy — 𝐂𝐨𝐦𝐩𝐫𝐚 𝐭𝐮𝐬 𝐜𝐫𝐞𝐝𝐢𝐭𝐨𝐬\n"
        "➣ /planes — 𝐀𝐜𝐜𝐞𝐝𝐞 𝐚 𝐥𝐨𝐬 𝐩𝐫𝐞𝐜𝐢𝐨𝐬\n\n"
        "➣ 𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐀𝐃𝐎𝐑 𝐎𝐅𝐂: @SERVICIOSALBERTPE"
    )

    # Enlace directo de la imagen (debe ser imagen válida terminada en .jpg/.png)
    foto_url = "https://ibb.co/BVwh22Lj"

    bot.send_photo(chat_id=message.chat.id, photo=foto_url, caption=texto, parse_mode='Markdown')

@bot.message_handler(commands=['vendedores'])
def cmd_vendedores(message):
    try:
        with open("sellers.json", "r") as f:
            sellers_data = json.load(f)
            lista_sellers = sellers_data.get("sellers", [])

        if not lista_sellers:
            bot.send_message(message.chat.id, "⚠️ No hay vendedores registrados actualmente.")
            return

        texto = "👨‍💼 *LISTA DE VENDEDORES ACTIVOS:*\n\n"
        for seller_id in lista_sellers:
            try:
                user_info = bot.get_chat(int(seller_id))
                nombre = user_info.first_name or "Sin nombre"
                if hasattr(user_info, 'last_name') and user_info.last_name:
                    nombre += f" {user_info.last_name}"
                enlace = f"[{nombre}](tg://user?id={seller_id})"
                texto += f"🔹 {enlace}\n"
            except Exception:
                texto += f"🔹 ID: `{seller_id}` (no se pudo obtener el nombre)\n"

        bot.send_message(message.chat.id, texto, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['seller'])
def cmd_seller(message):
    ADMIN_ID = 7819787342  # Reemplaza por tu ID de Telegram, sin comillas

    # Verifica si el usuario es el administrador
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ No tienes permiso para usar este comando.")
        return

    try:
        parts = message.text.split()
        
        # Asegurarse de que el comando está correctamente escrito
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❗ Usa el comando así: /seller <user_id>")
            return

        seller_id = int(parts[1])  # Convierte el ID del vendedor a entero

        # Obtener información del usuario
        try:
            user_info = bot.get_chat(seller_id)
            full_name = user_info.first_name
            if user_info.last_name:
                full_name += f" {user_info.last_name}"
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error al obtener información del usuario: {e}")
            return

        # Cargar y actualizar sellers.json
        try:
            with open("sellers.json", "r") as f:
                sellers = json.load(f)
        except FileNotFoundError:
            sellers = {"sellers": []}  # Crear la estructura si el archivo no existe

        # Verificar si el vendedor ya está en la lista
        if seller_id not in sellers["sellers"]:
            sellers["sellers"].append(seller_id)
            with open("sellers.json", "w") as f:
                json.dump(sellers, f, indent=4)

            bot.send_message(message.chat.id, f"✅ El usuario *{full_name}* ha sido promovido al rango de *SELLER*.", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"⚠️ El usuario *{full_name}* ya es un SELLER.", parse_mode="Markdown")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")
        
@bot.message_handler(commands=['unseller'])
def cmd_unseller(message):
    ADMIN_ID = 7819787342  # Reemplaza por tu ID de Telegram

    # Verifica si el usuario es el administrador
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ No tienes permiso para usar este comando.")
        return

    try:
        parts = message.text.split()
        
        # Asegurarse de que el comando está correctamente escrito
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❗ Usa el comando así: /unseller <user_id>")
            return

        seller_id = int(parts[1])  # Convierte el ID a entero

        # Obtener nombre del usuario
        try:
            user_info = bot.get_chat(seller_id)
            full_name = user_info.first_name
            if user_info.last_name:
                full_name += f" {user_info.last_name}"
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error al obtener información del usuario: {e}")
            return

        # Cargar y modificar sellers.json
        try:
            with open("sellers.json", "r") as f:
                sellers = json.load(f)
        except FileNotFoundError:
            bot.send_message(message.chat.id, "⚠️ El archivo de sellers no existe.")
            return

        if seller_id in sellers.get("sellers", []):
            sellers["sellers"].remove(seller_id)

            with open("sellers.json", "w") as f:
                json.dump(sellers, f, indent=4)

            bot.send_message(message.chat.id, f"✅ El usuario *{full_name}* ha sido removido del rango *SELLER*.", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"⚠️ El usuario *{full_name}* no es un SELLER.", parse_mode="Markdown")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")


@bot.message_handler(func=lambda message: True)
def mensaje(message):
    reenviar_mensaje(message)

# Iniciar el bot asegurándose de no tener instancias duplicadas
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)











