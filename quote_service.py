import json
import os
import requests
from datetime import date

def _get_history_file_path() -> str:
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    app_folder = os.path.join(appdata, "DeskPetReminder")
    os.makedirs(app_folder, exist_ok=True)
    return os.path.join(app_folder, "shown_quotes.json")


HISTORY_FILE = _get_history_file_path()

FALLBACK_QUOTES = [
    {"q": "Nghỉ ngơi không phải là lười biếng, mà là để đi xa hơn.", "a": "DeskPet"},
    {"q": "Sức khỏe là nền tảng của mọi thành công.", "a": "DeskPet"},
    {"q": "Một phút nghỉ ngơi hôm nay, một ngày làm việc hiệu quả mai sau.", "a": "DeskPet"},
]


def _load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_history(history: dict):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def get_daily_quote() -> str:
    """
    Lấy quote của ngày hôm nay.
    - Nếu hôm nay đã lấy quote rồi (đã lưu trong history) -> trả lại quote đó, không gọi API nữa.
    - Nếu chưa -> gọi ZenQuotes API để lấy quote mới, lưu vào history theo ngày.
    - Nếu gọi API lỗi (mất mạng...) -> dùng quote fallback offline, không lặp lại 2 ngày liên tiếp.
    """
    today = date.today().isoformat()
    history = _load_history()

    # Nếu hôm nay đã có sẵn quote rồi thì dùng lại, tránh gọi API nhiều lần trong ngày
    if today in history:
        return history[today]["text"]

    quote_text = None
    try:
        resp = requests.get("https://zenquotes.io/api/today", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            q = data[0].get("q", "").strip()
            a = data[0].get("a", "").strip()
            if q:
                quote_text = f'"{q}" — {a}'
    except (requests.RequestException, ValueError, KeyError):
        quote_text = None

    if not quote_text:
        # Fallback: chọn câu chưa dùng gần đây nhất trong danh sách offline
        used_texts = {v["text"] for v in history.values()}
        for item in FALLBACK_QUOTES:
            candidate = f'"{item["q"]}" — {item["a"]}'
            if candidate not in used_texts:
                quote_text = candidate
                break
        if not quote_text:
            quote_text = f'"{FALLBACK_QUOTES[0]["q"]}" — {FALLBACK_QUOTES[0]["a"]}'

    history[today] = {"text": quote_text}
    _save_history(history)
    return quote_text
