import os
import sys
import json
import time
import asyncio
import requests
from pathlib import Path
from datetime import datetime, timezone

# ─── Konfigurasi ────────────────────────────────────────────────────────────────
DASHBOARD_URL    = os.environ.get("DASHBOARD_URL", "https://deprescan-dashboard.streamlit.app/")
DISCORD_WEBHOOK  = os.environ.get("DISCORD_WEBHOOK", "")
DISCORD_TOKEN    = os.environ.get("DISCORD_TOKEN", "")    # Bot token untuk DELETE pesan lama
                                                           # (webhook saja tidak bisa delete)

PAGE_LOAD_TIMEOUT = 60_000   # ms
RENDER_WAIT       = 10_000   # ms — tunggu Streamlit selesai render

SCREENSHOT_PATH   = Path("dashboard_snapshot.png")
MESSAGE_ID_FILE   = Path(".last_message_id.json")

# Indikator sleep Streamlit
SLEEP_INDICATORS = [
    "This app has gone to sleep",
    "app has gone to sleep",
    "app-sleeping",
    "Zzzz",
]


# ─── Waktu WIB ──────────────────────────────────────────────────────────────────

def get_wib_time() -> str:
    ts = datetime.now(timezone.utc).timestamp() + 7 * 3600
    return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S WIB")


# ─── Simpan / baca message_id ───────────────────────────────────────────────────

def load_last_message() -> dict | None:
    if not MESSAGE_ID_FILE.exists():
        return None
    try:
        return json.loads(MESSAGE_ID_FILE.read_text())
    except Exception:
        return None


def save_last_message(message_id: str, channel_id: str):
    MESSAGE_ID_FILE.write_text(json.dumps({
        "message_id": message_id,
        "channel_id": channel_id,
    }, indent=2))
    print(f"  [MSG] Tersimpan message_id={message_id}")


# ─── Discord API ────────────────────────────────────────────────────────────────

def delete_old_message(message_id: str, channel_id: str) -> bool:
    """
    Hapus pesan Discord lama via Bot API.
    Butuh DISCORD_TOKEN (bot token) dan bot harus ada di channel tsb.
    """
    if not DISCORD_TOKEN:
        print("  [DISCORD] DISCORD_TOKEN tidak diset, skip delete pesan lama.")
        return False
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}"
    try:
        r = requests.delete(
            url,
            headers={"Authorization": f"Bot {DISCORD_TOKEN}"},
            timeout=10,
        )
        if r.status_code == 204:
            print(f"  [DISCORD] Pesan lama {message_id} berhasil dihapus.")
            return True
        else:
            print(f"  [DISCORD] Gagal hapus pesan: HTTP {r.status_code} {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  [DISCORD] Exception saat hapus pesan: {e}")
        return False


def send_screenshot_to_discord(
    screenshot_path: Path,
    status: str,
    timestamp: str,
    elapsed: float,
    is_sleeping: bool = False,
    error_msg: str = "",
) -> tuple[str, str] | None:
    """
    Kirim screenshot sebagai attachment ke Discord webhook.
    Return: (message_id, channel_id) atau None jika gagal.
    """
    if not DISCORD_WEBHOOK:
        print("  [DISCORD] DISCORD_WEBHOOK tidak diset, skip kirim.")
        return None

    # Build embed
    color_map = {
        "OK":      0x2ECC71,
        "SLEEPING": 0xF39C12,
        "ERROR":   0xE74C3C,
    }
    emoji_map = {
        "OK":      "✅",
        "SLEEPING": "😴",
        "ERROR":   "🔴",
    }
    label_map = {
        "OK":      "Dashboard AKTIF",
        "SLEEPING": "Dashboard TIDUR / HIBERNATE",
        "ERROR":   "Dashboard ERROR",
    }

    embed = {
        "title":       f"{emoji_map.get(status, '❓')} DepreScan | {label_map.get(status, status)}",
        "description": "Snapshot monitoring otomatis dashboard **DepreScan**.",
        "color":       color_map.get(status, 0x95A5A6),
        "image":       {"url": "attachment://snapshot.png"},
        "fields": [
            {"name": "🕐 Waktu",         "value": timestamp,         "inline": True},
            {"name": "⚡ Load Time",     "value": f"{elapsed:.1f}s", "inline": True},
            {"name": "🔗 URL",           "value": DASHBOARD_URL,     "inline": False},
        ],
        "footer": {"text": "DepreScan Monitoring • Capstone Coding Camp 2026"},
    }

    if error_msg:
        embed["fields"].append({
            "name": "❌ Error", "value": f"```{error_msg[:500]}```", "inline": False
        })

    payload = {"embeds": [embed]}

    try:
        with open(screenshot_path, "rb") as img:
            r = requests.post(
                DISCORD_WEBHOOK + "?wait=true",   # wait=true agar dapat message_id
                data={"payload_json": json.dumps(payload)},
                files={"files[0]": ("snapshot.png", img, "image/png")},
                timeout=30,
            )

        if r.status_code in (200, 204):
            data       = r.json()
            message_id = data.get("id", "")
            channel_id = data.get("channel_id", "")
            print(f"  [DISCORD] Screenshot terkirim (msg_id={message_id})")
            return message_id, channel_id
        else:
            print(f"  [DISCORD] Gagal kirim: HTTP {r.status_code} {r.text[:300]}")
            return None

    except Exception as e:
        print(f"  [DISCORD] Exception: {e}")
        return None


def send_error_embed(timestamp: str, error_msg: str):
    """Kirim embed error ringan (tanpa screenshot) jika browser gagal total."""
    if not DISCORD_WEBHOOK:
        return
    embed = {
        "title":       "🔴 DepreScan | Dashboard ERROR",
        "description": "Monitoring gagal — tidak dapat mengambil screenshot.",
        "color":       0xE74C3C,
        "fields": [
            {"name": "🕐 Waktu",  "value": timestamp,            "inline": True},
            {"name": "❌ Error", "value": f"```{error_msg[:500]}```", "inline": False},
        ],
        "footer": {"text": "DepreScan Monitoring • Capstone Coding Camp 2026"},
    }
    try:
        r = requests.post(
            DISCORD_WEBHOOK + "?wait=true",
            json={"embeds": [embed]},
            timeout=15,
        )
        if r.status_code in (200, 204):
            data = r.json()
            save_last_message(data.get("id", ""), data.get("channel_id", ""))
    except Exception as e:
        print(f"  [DISCORD] Gagal kirim error embed: {e}")


# ─── Playwright ─────────────────────────────────────────────────────────────────

async def take_screenshot() -> tuple[str, float, str]:
    """
    Buka dashboard, tunggu render, ambil screenshot.
    Return: (status, elapsed_sec, error_msg)
      status: "OK" | "SLEEPING" | "ERROR"
    """
    from playwright.async_api import async_playwright, TimeoutError as PWTimeout

    start     = time.time()
    status    = "ERROR"
    error_msg = ""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = await context.new_page()

        try:
            print(f"  [PW] Membuka {DASHBOARD_URL} ...")
            await page.goto(
                DASHBOARD_URL,
                timeout=PAGE_LOAD_TIMEOUT,
                wait_until="domcontentloaded",
            )

            # Tunggu networkidle (best effort)
            try:
                await page.wait_for_load_state("networkidle", timeout=PAGE_LOAD_TIMEOUT)
            except PWTimeout:
                print("  [PW] networkidle timeout, lanjut...")

            # Tunggu elemen Streamlit muncul di DOM
            print("  [PW] Menunggu render Streamlit...")
            try:
                await page.wait_for_selector(
                    "[data-testid='stSidebar'], [data-testid='stApp'], .stApp",
                    timeout=RENDER_WAIT,
                )
                print("  [PW] Elemen Streamlit terdeteksi.")
                # Tambahan jeda agar chart & komponen lain selesai render
                await page.wait_for_timeout(3_000)
            except PWTimeout:
                print("  [PW] Streamlit selector timeout, lanjut fixed wait...")
                await page.wait_for_timeout(RENDER_WAIT)

            elapsed = time.time() - start

            # Cek apakah sedang tidur via HTML content
            html = await page.content()
            lower = html.lower()
            if any(ind.lower() in lower for ind in SLEEP_INDICATORS):
                print("  [PW] Dashboard terdeteksi TIDUR")
                status = "SLEEPING"
            else:
                status = "OK"

            # Ambil screenshot (apapun statusnya — biar kelihatan kondisi aslinya)
            print(f"  [PW] Mengambil screenshot (status={status})...")
            await page.screenshot(
                path=str(SCREENSHOT_PATH),
                full_page=False,      # viewport saja — lebih rapi, sidebar keliatan
                type="png",
            )
            print(f"  [PW] Screenshot tersimpan: {SCREENSHOT_PATH}")

        except PWTimeout:
            elapsed   = time.time() - start
            error_msg = f"Playwright timeout setelah {PAGE_LOAD_TIMEOUT // 1000}s"
            status    = "ERROR"
            print(f"  [PW] {error_msg}")

        except Exception as exc:
            elapsed   = time.time() - start
            error_msg = str(exc)
            status    = "ERROR"
            print(f"  [PW] Exception: {error_msg}")

        finally:
            await browser.close()

    return status, elapsed, error_msg


# ─── Main ───────────────────────────────────────────────────────────────────────

async def main() -> int:
    timestamp = get_wib_time()
    print(f"\n{'='*60}")
    print(f"  DepreScan Monitoring — {timestamp}")
    print(f"  URL: {DASHBOARD_URL}")
    print(f"{'='*60}\n")

    # ── Step 1: Ambil screenshot via Playwright ────────────────────
    print("[1/3] Menjalankan Playwright headless browser...")
    status, elapsed, error_msg = await take_screenshot()

    # ── Step 2: Hapus pesan Discord lama ──────────────────────────
    print("\n[2/3] Mengecek pesan Discord lama...")
    last = load_last_message()
    if last:
        print(f"      Ditemukan pesan lama (id={last['message_id']}), menghapus...")
        delete_old_message(last["message_id"], last["channel_id"])
    else:
        print("      Tidak ada pesan lama.")

    # ── Step 3: Kirim screenshot baru ke Discord ───────────────────
    print("\n[3/3] Mengirim snapshot ke Discord...")

    if status == "ERROR" or not SCREENSHOT_PATH.exists():
        send_error_embed(timestamp, error_msg)
        print(f"\n{'='*60}")
        print("  Monitoring selesai — Status: ERROR")
        print(f"{'='*60}\n")
        return 1

    result = send_screenshot_to_discord(
        screenshot_path = SCREENSHOT_PATH,
        status          = status,
        timestamp       = timestamp,
        elapsed         = elapsed,
        error_msg       = error_msg,
    )

    exit_code = 0
    if result:
        message_id, channel_id = result
        if message_id and channel_id:
            save_last_message(message_id, channel_id)
    else:
        exit_code = 1

    if status != "OK":
        exit_code = 1

    print(f"\n{'='*60}")
    print(f"  Monitoring selesai — Status: {status}")
    print(f"{'='*60}\n")
    return exit_code


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
