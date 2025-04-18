import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from otp_fetcher import fetch_otp_with_credentials

from flask import Flask
from threading import Thread

# Load .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Flask app for Render keep-alive
app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Bot is running on Render!"

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

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

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        otp = fetch_otp_with_credentials(self.email.value, self.password.value)
        if otp:
            await interaction.followup.send(f"🟢 รหัส OTP ของคุณคือ: **{otp}**", ephemeral=True)
        else:
            await interaction.followup.send("🔴 ไม่สามารถดึง OTP ได้ กรุณาตรวจสอบข้อมูลอีกครั้ง", ephemeral=True)

class LoginButton(discord.ui.View):
    @discord.ui.button(label="👉🏻 กดปุ่มเพื่อรับ OTP", style=discord.ButtonStyle.primary)
    async def login(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LoginModal())

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
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

# Run Flask + Bot
if __name__ == '__main__':
    Thread(target=run_flask).start()
    bot.run(TOKEN)
