import requests
from PIL import Image
from io import BytesIO
import telegram
import asyncio

# Các link ảnh
image_urls = [
    "https://www.cophieu68.vn/chartold/chartsymbol_chart.php?screenwidth=1024&csc=1759338000&s=2024-10-07&e=2025-10-02&page=0&m=candle&dateby=1&extend_height=1&extend_weight=1&data_type1=1&data_type2=&sma=1&sma_day=10&sma2_day=&sma3_day=&sma4_day=&ema=1&ema_day=30&ema2_day=&ema3_day=&ema4_day=&ichimoku=1&tenkan_sen=9&kijun_sen=26&senkou_span=26&chartsize=1&id=^vnindex&time=1759411924",
    "https://www.cophieu68.vn/chartold/chartsymbol_chart.php?screenwidth=1024&csc=1759338000&s=2024-10-07&e=2025-10-02&page=0&m=candle&dateby=1&extend_height=1&extend_weight=1&data_type1=1&data_type2=&sma=1&sma_day=10&sma2_day=&sma3_day=&sma4_day=&ema=1&ema_day=30&ema2_day=&ema3_day=&ema4_day=&ichimoku=1&tenkan_sen=9&kijun_sen=26&senkou_span=26&chartsize=1&id=^vnindex&time=1759411924",
    "https://www.cophieu68.vn/chartold/chartsymbol_chart.php?screenwidth=1024&csc=1759338000&s=2024-10-07&e=2025-10-02&page=0&m=candle&dateby=1&extend_height=1&extend_weight=1&data_type1=1&data_type2=&sma=1&sma_day=10&sma2_day=&sma3_day=&sma4_day=&ema=1&ema_day=30&ema2_day=&ema3_day=&ema4_day=&ichimoku=1&tenkan_sen=9&kijun_sen=26&senkou_span=26&chartsize=1&id=^vnindex&time=1759411924"
]

# Tải ảnh
images = []
for url in image_urls:
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    images.append(img)

# Ghép ảnh theo chiều dọc
width = max(img.width for img in images)
height = sum(img.height for img in images)
combined = Image.new('RGB', (width, height))

y_offset = 0
for img in images:
    combined.paste(img, (0, y_offset))
    y_offset += img.height

# Lưu ảnh
combined.save("combined.jpg")

# Gửi vào Telegram
async def send_image():
    bot = telegram.Bot(token="BOT_TOKEN")
    chat_id = "CHAT_ID"
    with open("combined.jpg", "rb") as photo:
        await bot.send_photo(chat_id=chat_id, photo=photo)

# Gọi hàm async
asyncio.run(send_image())

