import os
import requests
from PIL import Image, ImageDraw

SOLAX_TOKEN = os.getenv("SOLAX_TOKEN")
SOLAX_SN = os.getenv("SOLAX_SN")
GEEKMAGIC_IP = os.getenv("GEEKMAGIC_IP")

def get_solax_data():
    url = f"https://global.solaxcloud.com/proxyApp/proxy/api/getRealtimeInfo.do?tokenId={SOLAX_TOKEN}&sn={SOLAX_SN}"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get("success"):
            data = res["result"]
            yield_today = data.get("yieldtoday", 0)
            feedin_power = data.get("feedinpower", 0)
            soc = data.get("soc", 0)
            return yield_today, feedin_power, soc
    except Exception as e:
        print(f"Hiba a SolaX lekérésnél: {e}")
    return 0, 0, 0

def create_image(yield_today, power_w, soc):
    img = Image.new("RGB", (240, 240), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    draw.text((20, 15), "SOLAX NAPELEM", fill=(255, 255, 255))
    draw.line([(20, 40), (220, 40)], fill=(51, 65, 85), width=2)
    
    power_kw = round(power_w / 1000.0, 2) if power_w else 0
    draw.text((20, 55), "Termeles (kW):", fill=(148, 163, 184))
    draw.text((20, 75), f"{power_kw} kW", fill=(52, 211, 153))

    draw.text((20, 120), "Mai napi (kWh):", fill=(148, 163, 184))
    draw.text((20, 140), f"{yield_today} kWh", fill=(250, 204, 21))

    draw.text((20, 185), f"Akku: {soc}%", fill=(96, 165, 250))

    img.save("solax_now.jpg", "JPEG")

def upload_to_geekmagic():
    target_url = f"http://{GEEKMAGIC_IP}/upload"
    try:
        with open("solax_now.jpg", "rb") as f:
            files = {"file": ("solax_now.jpg", f, "image/jpeg")}
            r = requests.post(target_url, files=files, timeout=15)
            print("Kép feltöltve a kijelzőre! Státusz:", r.status_code)
    except Exception as e:
        print(f"Feltöltési hiba: {e}")

if __name__ == "__main__":
    yt, p, soc = get_solax_data()
    create_image(yt, p, soc)
    upload_to_geekmagic()
