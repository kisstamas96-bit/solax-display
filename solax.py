import os
import requests
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# 1. Beállítások & Környezeti változók
# ---------------------------------------------------------------------------
SOLAX_TOKEN = os.environ.get("SOLAX_TOKEN")
SOLAX_SN = os.environ.get("SOLAX_SN")
GEEKMAGIC_IP = os.environ.get("GEEKMAGIC_IP")

SOLAX_URL = f"https://global.solaxcloud.com/proxy/api/getRealtimeInfo.do?tokenId={SOLAX_TOKEN}&sn={SOLAX_SN}"

# ---------------------------------------------------------------------------
# 2. SolaX Adatok Lekérése
# ---------------------------------------------------------------------------
def fetch_solax_data():
    try:
        r = requests.get(SOLAX_URL, timeout=10)
        data = r.json()
        if data.get("success"):
            result = data.get("result", {})
            return {
                "acpower": result.get("acpower", 0),       # Termelés / Hálózati teljesítmény (W)
                "yieldtoday": result.get("yieldtoday", 0), # Mai termelés (kWh)
                "uploadTime": result.get("uploadTime", "")
            }
        else:
            print("SolaX API válasz hiba:", data)
            return None
    except Exception as e:
        print(f"Hiba a SolaX lekéréskor: {e}")
        return None

# ---------------------------------------------------------------------------
# 3. Kép Generálása (240x240 pixel a GeekMagic-hez)
# ---------------------------------------------------------------------------
def create_display_image(data):
    # Fekete háttér
    img = Image.new("RGB", (240, 240), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Alapértelmezett betűtípus használata
    try:
        font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        font_med = ImageFont.truetype("DejaVuSans.ttf", 22)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Fejléc
    draw.text((10, 10), "SOLAX SOLAR", fill=(255, 200, 0), font=font_med)
    draw.line([(10, 38), (230, 38)], fill=(100, 100, 100), width=1)

    if data:
        power = data["acpower"]
        yield_today = data["yieldtoday"]

        # Aktuális teljesítmény
        draw.text((10, 50), "NOW:", fill=(200, 200, 200), font=font_small)
        draw.text((10, 70), f"{power} W", fill=(0, 255, 128), font=font_large)

        # Mai termelés
        draw.text((10, 130), "TODAY:", fill=(200, 200, 200), font=font_small)
        draw.text((10, 150), f"{yield_today} kWh", fill=(0, 200, 255), font=font_med)

        # Időbélyeg
        time_str = data["uploadTime"].split(" ")[-1] if " " in data["uploadTime"] else data["uploadTime"]
        draw.text((10, 210), f"Updated: {time_str}", fill=(120, 120, 120), font=font_small)
    else:
        draw.text((10, 100), "API ERROR", fill=(255, 50, 50), font=font_med)

    img.save("solax_now.jpg", "JPEG", quality=90)
    print("Kép sikeresen legyártva: solax_now.jpg")

# ---------------------------------------------------------------------------
# 4. Feltöltés a GeekMagic Kijelzőre (Cloudflare Alagúton Át)
# ---------------------------------------------------------------------------
def upload_to_geekmagic():
    if not GEEKMAGIC_IP:
        print("HIBA: Nincs megadva GEEKMAGIC_IP Secret!")
        return

    # Cím megtisztítása az esetleges előtagoktól
    raw_ip = GEEKMAGIC_IP.strip()
    raw_ip = raw_ip.replace("https://", "").replace("http://", "").rstrip("/")
    
    # A kijelző webes felületének pontos feltöltési címe:
    target_url = f"https://{raw_ip}/doUpload?dir=/image/"
    
    print(f"Kép feltöltése a következő címre: {target_url}")
    try:
        with open("solax_now.jpg", "rb") as f:
            # A kijelző a 'file' mezőnevet várja
            files = {"file": ("solax_now.jpg", f, "image/jpeg")}
            r = requests.post(target_url, files=files, timeout=15)
            print("Válasz a kijelzőtől:", r.status_code, r.text)
    except Exception as e:
        print(f"Feltöltési hiba: {e}")

# ---------------------------------------------------------------------------
# Főprogram
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    solax_data = fetch_solax_data()
    create_display_image(solax_data)
    upload_to_geekmagic()
