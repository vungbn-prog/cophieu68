

import gspread
import gspread_dataframe as gd
import requests
from PIL import Image
from io import BytesIO
import socket
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import telegram
from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio
import os
import json
from google.oauth2.service_account import Credentials

print("Start")
# === CONFIG ===
droomid = "-869106170"
token = "7985230502:AAEPzSZtJqMeyfNjWXTI_NvIKiQR6dRhMA4"
# === Xử lý ngày tháng ===
today = datetime.now()
past_date = today - timedelta(days=1500)
fromdate = past_date.strftime("%Y-%m-%d")  # hoặc định dạng bạn cần

past_date2 = today - timedelta(days=100)
fromdate2 = past_date2.strftime("%Y-%m-%d")
todate = today.strftime("%Y-%m-%d")

minqty = today.hour * 60 + today.minute
weekday = today.weekday()  # Thứ hai = 0, Chủ nhật = 6
picturepath = r"D:\python3"
# Giả sử bạn đã có các biến fromdate, fromdate2, todate, minqty như đã chuyển trước đó
print(fromdate)
print(fromdate2)
# === Tạo các đường dẫn biểu đồ ===
chartlinklong = (
    "https://www.cophieu68.vn/chartold/chartsymbol_chart.php?screenwidth=720"
    f"&s={fromdate}&e={todate}&page=0&m=candle&chartsize=100&dateby=1"
    "&extend_height=1&extend_weight=1&data_type1=1&bollinger=1&sma=1"
    "&sma_day=20&sma2_day=50&sma3_day=200&showvolume=1&ichimoku=1"
    "&tenkan_sen=9&kijun_sen=26&senkou_span=26&chartsize=1&id="
)

chartlink = (
    "https://www.cophieu68.vn/chartold/chartsymbol_chart.php?screenwidth=720"
    f"&s={fromdate2}&e={todate}&page=0&m=candle&chartsize=100&dateby=1"
    "&extend_height=1&extend_weight=1&data_type1=1&bollinger=1&sma=1"
    "&sma_day=20&sma2_day=50&sma3_day=200&showvolume=1&ichimoku=1"
    "&tenkan_sen=9&kijun_sen=26&senkou_span=26&chartsize=1&id="
)

macdlink = (
    "https://www.cophieu68.vn/chartold/chartsymbol_chart.php?screenwidth=720"
    f"&s={fromdate2}&e={todate}&page=0&m=macd&chartsize=1"
    "&day_1=9&day_2=26&day_3=12&id="
)

stochlink = (
    "https://www.cophieu68.vn/chartold/chartsymbol_chart.php?screenwidth=720"
    f"&s={fromdate2}&e={todate}&page=0&m=stochastic&chartsize=1"
    "&stochastic_day=14&stochastic_ma=5&id="
)

endlink = f"&time={minqty}"

# --- Kết nối Google Sheets ---
# === Tạo credentials từ biến môi trường ===
json_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(json_creds, scopes=scopes)
# === Kết nối gspread ===
gc = gspread.authorize(credentials)
# === Truy cập các worksheet ===
FILTER = gc.open("Todolist").worksheet("Hvuot20")
LNST = gc.open("Todolist").worksheet("LNST")
LISTCP = gc.open("Todolist").worksheet("DM")


def is_connected(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def reconnect_gsheet():
    global gc, FILTER, LNST, LISTCP
    if is_connected():
        try:
            gc = gspread.service_account(filename="credentials.json")
            FILTER = gc.open("Todolist").worksheet("Hvuot20")
            LNST = gc.open("Todolist").worksheet("LNST")
            LISTCP = gc.open("Todolist").worksheet("DM")
            print("Đã kết nối lại với Google Sheets.")
        except Exception as e:
            print("Lỗi khi kết nối lại:", e)
    else:
        print("Mất kết nối mạng, đang khắc phục...")
    time.sleep(5)

def read_gsheet_list(sheet):
    while True:
        try:
            df = gd.get_as_dataframe(sheet, evaluate_formulas=True, usecols=[0], names=['code']).dropna()
            return df['code'].astype(str).str.strip().tolist()[1:]
        except:
            reconnect_gsheet()

def get_fa_info(stick):
    for line in read_gsheet_list(LNST):
        if stick in line:
            return line.strip()
    return ""

# === Tải ảnh từ URL ===

def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except (requests.RequestException, UnidentifiedImageError) as e:
        print(f"❌ Không thể tải ảnh từ URL: {url} — {e}")
        return None

def generate_chart_image(stick):
    try:
        img1 = download_image(chartlinklong + stick + endlink)
        img2 = download_image(chartlink + stick + endlink)
        img3 = download_image(macdlink + stick + endlink)
        img4 = download_image(stochlink + stick + endlink)
        # === Ghép ảnh theo chiều dọc ===
        width = max(img1.width, img2.width, img3.width, img4.width)
        height = img1.height + img2.height + img3.height + img4.height
    
        combined_img = Image.new("RGB", (width, height), (255, 255, 255))
        y_offset = 0
        for img in [img1, img2, img3, img4]:
            combined_img.paste(img, (0, y_offset))
            y_offset += img.height
        combined_img.save("combined_chart.png")
    
        draw = ImageDraw.Draw(combined_img)
        font = ImageFont.load_default()
        draw.text((60, 60), get_fa_info(stick), fill='black', font=font)
        img_path = f"{picturepath}\\Dchart.png"
        combined_img.save(img_path)
        return img_path
    except:
        img_path = f"{picturepath}\\Dchart.png"
        return img_path


async def send_chart(stick, chat_id, bot):
    img_path = generate_chart_image(stick)
    if img_path:
        link = f"https://24hmoney.vn/phan-tich-ky-thuat?symbol={stick}&object-type=symbol"
        try:
            await bot.send_photo(chat_id, open(img_path, 'rb'), caption=f'<a href="{link}">Xem biểu đồ</a> /{stick}', parse_mode='HTML')
            print(stick)
        except Exception as e:
            print(f"Lỗi gửi ảnh: {e}")

# --- Tự động gửi biểu đồ ---
async def autorun(application):
    sent = False
    while True:
        now = datetime.now()
        m = now.hour * 60 + now.minute
        hientai = f" lúc {now.hour}:{now.minute}"
        bot = application.bot
        if now.weekday() < 5:
            if 540 <= m < 885:
                for s in read_gsheet_list(FILTER):
                    await send_chart(s.replace('/', '').strip(), "-869106170", bot)
                sent = False
            elif m == 1020 and not sent:
                for s in read_gsheet_list(LISTCP):
                    await send_chart(s.replace('/', '').strip(), "-869106170", bot)
                sent = True
        await asyncio.sleep(5)

# --- Handler cho Telegram ---
async def start(update, context):
    await update.message.reply_text("Bot đã khởi động!")

async def handle_command(update, context):
    if update.message.text.strip() == "/go":
        now = datetime.now()
        hientai = f" lúc {now.hour}:{now.minute}"
        await context.bot.send_message("-869106170", "AllCP Start" + hientai)
        print("AllCP Start" + hientai)
        for stick in read_gsheet_list(LISTCP):
            await send_chart(stick.replace('/', '').strip(), "-869106170", context.bot)

# --- Hàm khởi động bot và autorun ---
async def on_startup(application):
    await application.bot.send_message("-869106170", text="✅ Bot đã sẵn sàng!")
    asyncio.create_task(autorun(application))

application = ApplicationBuilder() \
    .token(token) \
    .post_init(on_startup) \
    .build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("go", handle_command))





import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running.")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

import asyncio

# --- Hàm main ---
async def main():
    application = (
        ApplicationBuilder()
        .token(token)
        .post_init(on_startup)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("go", handle_command))

    await application.initialize()
    await application.start()
    await application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        webhook_url="https://cophieu68.onrender.com/webhook"
    )
    await application.stop()
    await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())





