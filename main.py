import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from otp_fetcher import fetch_otp_with_credentials
from flask import Flask
from threading import Thread

# 🔐 โหลดค่า ENV
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# 🎯 ตั้งค่า Bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# 🧾 ฟอร์มกรอกข้อมูล Email & Password
class LoginModal(discord.ui.Modal, title="📨 รับ OTP จาก ROCKSTAR ✅"):
    email = discord.ui.TextInput(
        label='📧 Rockstar Email',
        placeholder='กรอกอีเมลของคุณที่ใช้กับ Rockstar',
        required=True
    )
    password = discord.ui.TextInput(
        label='🔒 Rockstar Password',
        placeholder='กรอกรหัสผ่านของคุณ',
        required=True
    )

    # 📥 เมื่อผู้ใช้ส่งฟอร์ม
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        otp = fetch_otp_with_credentials(self.email.value, self.password.value)

        if otp:
            await interaction.followup.send(f"🟢 รหัส OTP ของคุณคือ: **{otp}**", ephemeral=True)
        else:
            await interaction.followup.send("🔴 ไม่สามารถดึง OTP ได้ กรุณาตรวจสอบข้อมูลอีกครั้ง", ephemeral=True)

# 🖱️ ปุ่มเปิด Modal
class LoginButton(discord.ui.View):
    @discord.ui.button(
        label="👉🏻 กดปุ่มเพื่อรับ OTP",
        style=discord.ButtonStyle.primary,
        custom_id="login_button"
    )
    async def login(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LoginModal())

# ⚡ เมื่อ Bot พร้อมใช้งาน
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}!')

    channel = bot.get_channel(CHANNEL_ID)

    # 💬 Embed + Button
    embed = discord.Embed(
        title="🎟️ CODE FROM ROCKSTAR SUPPORT",
        description=( 
            "```📌 ระบบรับรหัส OTP 6 หลักจาก Rockstar\n"
            "📧 กดปุ่มเพื่อกรอกอีเมลและรหัสผ่านของคุณ\n"
            "🔢 รับรหัส OTP ทันทีภายในไม่กี่วินาที\n"
            "⚡ ปลอดภัย เข้ารหัสแบบ Secure\n"
            "\n📮 รองรับเฉพาะอีเมล Rambler.ru เท่านั้น\n"
            "\n📖 **วิธีใช้งาน:**\n"
            "1️⃣ กดปุ่มด้านล่าง\n"
            "2️⃣ กรอกอีเมลและรหัสผ่าน\n"
            "3️⃣ รับรหัส OTP จากระบบ ```"
        ),
        color=0x0e89ff
    )
    embed.set_image(url="https://i.pinimg.com/originals/00/44/0a/00440aa746a76f99c8990800a91926c1.gif")

    await channel.send(embed=embed, view=LoginButton())

# 🧠 เริ่มรัน Bot
def run_bot():
    bot.run(TOKEN)

# 🔥 Start Flask app to keep the bot running
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Function to start Flask app in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Run both Flask and Discord bot
if __name__ == "__main__":
    # Start the Flask app in a separate thread to keep the bot alive
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Start the Discord bot
    run_bot()
