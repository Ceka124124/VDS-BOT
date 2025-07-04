import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import telebot
except ImportError:
    install("pyTelegramBotAPI")
    import telebot

import json
import os
import subprocess as sp
import threading
import uuid
from telebot import types

TOKEN = "7986443991:AAFqznq5DvdOI8lvXXRln7cQ4wMyhxAQ4ds"
bot = telebot.TeleBot(TOKEN)
DATA_FILE = "user.json"
KODLAR_KLASORU = "kodlar"
TEHLIKELI_KODLAR = [""]

ADMIN_ID = "7755042636"  # Admin ID
ADMIN_REF = 999999       # Admin için başlangıç ref değeri

os.makedirs(KODLAR_KLASORU, exist_ok=True)
active_processes = {}

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_ref_link(uid):
    return f"https://t.me/TeazerHostingBot?start={uid}"

def get_vds_turu(ref):
    if ref >= 40: return "Premium Pro VDS"
    elif ref >= 20: return "Perfect VDS"
    elif ref >= 10: return "Very Nice VDS"
    elif ref >= 5: return "Nice VDS"
    else: return "Free VDS"

def botu_baslat(uid, bot_id, path):
    def calistir():
        try:
            proc = sp.Popen(["python3", path])
            active_processes[f"{uid}_{bot_id}"] = proc
            proc.wait()
        except Exception as e:
            print(f"Hata: {e}")
    t = threading.Thread(target=calistir)
    t.start()

@bot.message_handler(commands=["start"])
def start_cmd(message):
    uid = str(message.from_user.id)
    args = message.text.split()
    data = load_data()
    if uid not in data:
        is_admin = (uid == ADMIN_ID)
        data[uid] = {
            "ref": ADMIN_REF if is_admin else 0,
            "bots": [],
            "active": [],
            "refby": "",
            "username": message.from_user.username or "N/A",
            "admin": is_admin
        }
        if len(args) > 1:
            ref_uid = args[1]
            if ref_uid != uid and ref_uid in data:
                data[ref_uid]["ref"] += 2
                data[uid]["refby"] = ref_uid
        save_data(data)
        bot.reply_to(message, f"""✅ Kayıt oldun, {'Admin olarak Free VDS verildi.' if is_admin else 'Free VDS verildi.'}

Komutlar:
/vds - Yeni VDS Satın Al (Referans ile)
/Benim - Kendi Botlarını ve ID'lerini gösterir. Aktif veya Pasif edebilirsin.
/.py Dosyası Atarak Botunu Aktif Edebilirsin!""")
    else:
        bot.reply_to(message, """✅ Zaten kayıtlısın.

Komutlar:
/vds - Yeni VDS Satın Al (Referans ile)
/Benim - Kendi Botlarını ve ID'lerini gösterir. Aktif veya Pasif edebilirsin.
/.py Dosyası Atarak Botunu Aktif Edebilirsin!""")

@bot.message_handler(commands=["vds"])
def vds_list(message):
    text = """💻 VDS Seçenekleri:

1️⃣ Free VDS - 1 Bot  
2️⃣ Nice VDS - 3 Bot [5 Ref]  
3️⃣ Very Nice VDS - 6 Bot [10 Ref]  
4️⃣ Perfect VDS - 10 Bot [20 Ref]  
5️⃣ Premium Pro VDS - Sınırsız Bot [40 Ref]"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📊 Hesabım", callback_data="hesabim"),
        types.InlineKeyboardButton("🔗 Referans Linkim", callback_data="referans")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["hesabim", "referans"])
def handle_callback(call):
    uid = str(call.from_user.id)
    data = load_data()
    if uid not in data:
        bot.answer_callback_query(call.id, "❌ /start ile kayıt ol.")
        return
    user = data[uid]
    if call.data == "hesabim":
        vds = get_vds_turu(user["ref"])
        text = f"""👤 Kullanıcı: @{user["username"]}
📌 VDS Türü: {vds}
💳 Referans: {user["ref"]}"""
        bot.send_message(call.message.chat.id, text)
    elif call.data == "referans":
        ref_link = get_ref_link(uid)
        bot.send_message(call.message.chat.id, f"🔗 Referans Linkin:\n{ref_link}")

@bot.message_handler(commands=["hesabım"])
def hesap_bilgi(message):
    uid = str(message.from_user.id)
    data = load_data()
    if uid in data:
        user = data[uid]
        vds = get_vds_turu(user["ref"])
        text = f"""👤 Kullanıcı: @{user["username"]}
💳 Referansın: {user["ref"]}
📡 VDS Türün: {vds}
🔗 Referans Linkin: {get_ref_link(uid)}"""
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "❌ Kayıtlı değilsin. /start yaz.")

@bot.message_handler(commands=["Benim"])
def benim_bots(message):
    uid = str(message.from_user.id)
    data = load_data()
    if uid not in data or not data[uid]["bots"]:
        bot.reply_to(message, "📂 Botun yok.")
        return
    for bot_item in data[uid]["bots"]:
        bot_id = bot_item["id"]
        name = bot_item["name"]
        aktif = "✅" if bot_id in data[uid]["active"] else "❌"
        durum = f"{name} - aktif: {aktif} | id: {bot_id}"
        markup = types.InlineKeyboardMarkup()
        if bot_id in data[uid]["active"]:
            markup.add(types.InlineKeyboardButton("🛑 Pasifleştir", callback_data=f"deaktif_{bot_id}"))
        else:
            markup.add(types.InlineKeyboardButton("✅ Aktif Et", callback_data=f"aktif_{bot_id}"))
        bot.send_message(message.chat.id, durum, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("aktif_") or call.data.startswith("deaktif_"))
def bot_durum_degisiklik(call):
    uid = str(call.from_user.id)
    data = load_data()
    user = data.get(uid)
    if not user:
        bot.answer_callback_query(call.id, "❌ Kayıt yok.")
        return
    cmd, bot_id_str = call.data.split("_")
    bot_id = int(bot_id_str)
    hedef = next((b for b in user["bots"] if b["id"] == bot_id), None)
    if not hedef:
        bot.answer_callback_query(call.id, "❌ Bot yok.")
        return
    if cmd == "aktif":
        vds = get_vds_turu(user["ref"])
        limit = {"Free VDS": 1, "Nice VDS": 3, "Very Nice VDS": 6, "Perfect VDS": 10, "Premium Pro VDS": 9999}[vds]
        if len(user["active"]) >= limit:
            bot.answer_callback_query(call.id, f"⚠️ En fazla {limit} bot.")
            return
        if bot_id not in user["active"]:
            user["active"].append(bot_id)
            save_data(data)
            botu_baslat(uid, bot_id, hedef["path"])
            bot.answer_callback_query(call.id, "✅ Bot aktif.")
    else:
        if bot_id in user["active"]:
            user["active"].remove(bot_id)
            save_data(data)
            pid_key = f"{uid}_{bot_id}"
            if pid_key in active_processes:
                try:
                    active_processes[pid_key].terminate()
                    del active_processes[pid_key]
                except:
                    pass
            bot.answer_callback_query(call.id, "🛑 Bot durduruldu.")
    yeni_durum = "✅" if bot_id in user["active"] else "❌"
    yeni_text = f"{hedef['name']} - aktif: {yeni_durum} | id: {bot_id}"
    yeni_button = types.InlineKeyboardMarkup()
    if bot_id in user["active"]:
        yeni_button.add(types.InlineKeyboardButton("🛑 Pasifleştir", callback_data=f"deaktif_{bot_id}"))
    else:
        yeni_button.add(types.InlineKeyboardButton("✅ Aktif Et", callback_data=f"aktif_{bot_id}"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=yeni_text, reply_markup=yeni_button)

@bot.message_handler(content_types=['document'])
def handle_py_file(message):
    uid = str(message.from_user.id)
    data = load_data()
    if uid not in data:
        bot.reply_to(message, "❌ Önce /start yaz.")
        return
    doc = message.document
    if not doc.file_name.endswith(".py"):
        bot.reply_to(message, "❗ Sadece .py kabul.")
        return
    file_info = bot.get_file(doc.file_id)
    downloaded = bot.download_file(file_info.file_path)
    new_id = int(str(uuid.uuid4().int)[-4:])
    path = f"{KODLAR_KLASORU}/{new_id}_{doc.file_name}"
    with open(path, 'wb') as f:
        f.write(downloaded)
    with open(path, 'r') as f:
        content = f.read()
    for tehlike in TEHLIKELI_KODLAR:
        if tehlike in content:
            os.remove(path)
            bot.reply_to(message, f"🚫 Zararlı komut: `{tehlike}`")
            return
    data[uid]["bots"].append({"id": new_id, "name": doc.file_name, "path": path})
    save_data(data)
    bot.reply_to(message, f"✅ {doc.file_name} kaydedildi.\n🆔 ID: {new_id}")

bot.infinity_polling()
