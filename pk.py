#!/usr/bin/env python3
"""
Stripe SK Bot - Complete Standalone Telegram Bot
Handles: SK lookup, checkout generation, payment links, key testing
Author: @NotYoursNaruto
"""

import asyncio
import concurrent.futures
import json
import os
import re
import time
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

import httpx
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
TOKEN = "8901668516:AAGrIt__UkH6gEGLQos6iHxv13yp6AVkFkw"  # <── REPLACE THIS

# ── Premium Emoji IDs ──────────────────────────────────────────────────────
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

def pe(emoji_id: str) -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">⚡</tg-emoji>'

def bold(text: str) -> str:
    _BOLD_MAP = {}
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        _BOLD_MAP[c] = chr(0x1D5D4 + i)
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        _BOLD_MAP[c] = chr(0x1D5EE + i)
    for i, c in enumerate("0123456789"):
        _BOLD_MAP[c] = chr(0x1D7EC + i)
    return "".join(_BOLD_MAP.get(c, c) for c in text)

# ── Thread pool ─────────────────────────────────────────────────────────────
CHECKER_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=50)

# ── Constants ──────────────────────────────────────────────────────────────
DEFAULT_CURRENCY = "usd"
DEFAULT_AMOUNT = 100

# ── Key Patterns ──────────────────────────────────────────────────────────
SK_PATTERN = re.compile(r"(sk_(?:live|test)_[A-Za-z0-9_\-]+)")
PK_PATTERN = re.compile(r"(pk_(?:live|test)_[A-Za-z0-9_\-]+)")


# ═══════════════════════════════════════════════════════════════════════════
#  CORE FUNCTIONS - FIXED FOR ALL STRIPE API VERSIONS
# ═══════════════════════════════════════════════════════════════════════════

def extract_sk_from_text(text: str) -> Optional[str]:
    """Extract Stripe secret key from text."""
    if not text:
        return None
    # Check each word
    for word in text.split():
        word = word.strip()
        if word.startswith("sk_live") or word.startswith("sk_test"):
            return word
    # Fallback to regex
    match = SK_PATTERN.search(text)
    return match.group(1) if match else None

def validate_sk(sk: str) -> bool:
    return bool(sk and sk.startswith("sk_") and len(sk) > 10)

def mask_key(key: str) -> str:
    if len(key) <= 16:
        return key[:8] + "…" + key[-4:]
    return key[:12] + "…" + key[-6:]

def get_key_type(sk: str) -> str:
    return "live" if "sk_live" in sk else "test"


# ── CHECKOUT SESSION GENERATION (FIXED) ──────────────────────────────────

def generate_checkout_session(
    sk: str,
    amount: int = DEFAULT_AMOUNT,
    currency: str = DEFAULT_CURRENCY,
    product_name: str = "Bot Generated Product",
) -> Dict[str, Any]:
    """Generate a Stripe Checkout Session."""
    try:
        # Use legacy stripe module for compatibility
        import stripe as stripe_lib
        stripe_lib.api_key = sk
        
        # Create product
        product = stripe_lib.Product.create(name=product_name)
        
        # Create price
        price = stripe_lib.Price.create(
            unit_amount=amount,
            currency=currency.lower(),
            product=product.id,
        )
        
        # Create checkout session
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


# ── PAYMENT LINK GENERATION (FIXED) ──────────────────────────────────────

def generate_payment_link(
    sk: str,
    amount: int = DEFAULT_AMOUNT,
    currency: str = DEFAULT_CURRENCY,
    product_name: str = "Bot Generated Product",
) -> Dict[str, Any]:
    """Generate a Stripe Payment Link."""
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


# ── KEY LOOKUP (FIXED) ────────────────────────────────────────────────────

def lookup_key_info(sk: str) -> Dict[str, Any]:
    """Look up information about a Stripe secret key."""
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
        
        # ── Get balance ──
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
        
        # ── Get account info ──
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
        
        # ── Get transactions ──
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


# ── TEST CHARGE (FIXED: uses legacy API) ─────────────────────────────────

def test_charge(sk: str, amount: int = 100, currency: str = "usd") -> Dict[str, Any]:
    """Test a Stripe key by attempting to create a payment intent."""
    try:
        import stripe as stripe_lib
        stripe_lib.api_key = sk
        
        # ── Try to create a payment intent ──
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
            "message": "✅ Key is active and can create payment intents",
        }
        
    except stripe.error.AuthenticationError as e:
        return {"success": False, "error": f"❌ Invalid SK: {str(e)}"}
    except stripe.error.PermissionError as e:
        return {"success": False, "error": f"❌ Permission denied: {str(e)}"}
    except stripe.error.InvalidRequestError as e:
        if "missing" in str(e).lower():
            return {
                "success": True,
                "key_type": get_key_type(sk),
                "masked_key": mask_key(sk),
                "message": "⚠️ Key is active but needs additional parameters",
                "error_detail": str(e)[:200],
            }
        return {"success": False, "error": f"❌ Invalid request: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"❌ Unexpected error: {str(e)}"}


# ── SESSION LOOKUP ────────────────────────────────────────────────────────

def lookup_checkout_session(sk: str, session_id: str) -> Dict[str, Any]:
    """Look up a Stripe Checkout Session by ID."""
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
    """List recent payment intents."""
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


# ── FORMATTING FUNCTIONS ──────────────────────────────────────────────────

def format_lookup_result(data: Dict[str, Any]) -> str:
    if not data.get("success"):
        return f"{pe(E['cross'])} {bold('Error:')} {data.get('error', 'Unknown')}"
    
    lines = [
        f"{pe(E['bank'])} {bold('Stripe SK Info')}",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🔑 {bold('Key:')} {bold(data.get('masked_key', 'N/A'))}",
        f"📊 {bold('Type:')} {bold(data.get('key_type', 'Unknown'))}",
    ]
    
    acc = data.get("account", {})
    if acc:
        lines.append("")
        lines.append(f"📧 {bold('Email:')} {acc.get('email', 'N/A')}")
        lines.append(f"🏢 {bold('Business:')} {acc.get('business_name', 'N/A')}")
        lines.append(f"🌍 {bold('Country:')} {acc.get('country', 'Unknown')}")
        lines.append(f"✅ {bold('Charges:')} {'✅ Enabled' if acc.get('charges_enabled') else '❌ Disabled'}")
        lines.append(f"💸 {bold('Payouts:')} {'✅ Enabled' if acc.get('payouts_enabled') else '❌ Disabled'}")
    
    bal = data.get("balance", {})
    if bal:
        lines.append("")
        avail = ", ".join(bal.get("available", [])) or "0.00"
        pend = ", ".join(bal.get("pending", [])) or "0.00"
        lines.append(f"💰 {bold('Available:')} {avail}")
        lines.append(f"⏳ {bold('Pending:')} {pend}")
    
    txs = data.get("transactions", [])
    if txs:
        lines.append("")
        lines.append(f"{pe(E['bolt'])} {bold('Recent:')}")
        for t in txs[:3]:
            lines.append(f"  • {t['amount']} — {t['type']} ({t['status']})")
    
    return "\n".join(lines)

def format_session_result(data: Dict[str, Any]) -> str:
    if not data.get("success"):
        return f"{pe(E['cross'])} {bold('Error:')} {data.get('error', 'Unknown')}"
    
    return "\n".join([
        f"{pe(E['gem'])} {bold('✅ Checkout Generated!')}",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🔗 {bold('URL:')} <a href='{data.get('checkout_url', '#')}'>{data.get('checkout_url', 'N/A')}</a>",
        f"📋 {bold('ID:')} <code>{data.get('session_id', 'N/A')}</code>",
        f"💰 {bold('Amount:')} {data.get('amount_total', 0)/100:.2f} {data.get('currency', 'usd').upper()}",
        f"📊 {bold('Status:')} {data.get('payment_status', 'N/A')}",
        f"🔑 {bold('Key:')} {data.get('masked_key', 'N/A')}",
    ])

def format_payment_link_result(data: Dict[str, Any]) -> str:
    if not data.get("success"):
        return f"{pe(E['cross'])} {bold('Error:')} {data.get('error', 'Unknown')}"
    
    amount = data.get('amount', 100)
    currency = data.get('currency', 'usd')
    
    return "\n".join([
        f"{pe(E['gem'])} {bold('✅ Payment Link Generated!')}",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🔗 {bold('URL:')} <a href='{data.get('payment_link_url', '#')}'>{data.get('payment_link_url', 'N/A')}</a>",
        f"📋 {bold('ID:')} <code>{data.get('payment_link_id', 'N/A')}</code>",
        f"💰 {bold('Amount:')} {amount/100:.2f} {currency.upper()}",
        f"🔑 {bold('Key:')} {data.get('masked_key', 'N/A')}",
    ])

def format_test_result(data: Dict[str, Any]) -> str:
    if not data.get("success"):
        return f"{pe(E['cross'])} {bold('Key Test Failed!')}\n{data.get('error', 'Unknown error')}"
    
    lines = [
        f"{pe(E['check'])} {bold('✅ Key Test Results')}",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🔑 {bold('Key:')} {bold(data.get('masked_key', 'N/A'))}",
        f"📊 {bold('Type:')} {bold(data.get('key_type', 'Unknown'))}",
        f"💬 {data.get('message', 'Key is operational')}",
    ]
    if data.get("payment_intent_id"):
        lines.append(f"📋 {bold('Intent:')} <code>{data.get('payment_intent_id')}</code>")
        lines.append(f"📊 {bold('Status:')} {data.get('status', 'N/A')}")
        lines.append(f"💰 {bold('Amount:')} {data.get('amount', 'N/A')}")
    if data.get("error_detail"):
        lines.append(f"\n⚠️ {bold('Detail:')} {data.get('error_detail')}")
    return "\n".join(lines)


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


def menu_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "🛒 Checkout", "callback_data": "menu_checkout"},
             {"text": "🔗 Payment Link", "callback_data": "menu_paylink"}],
            [{"text": "🔍 Lookup SK", "callback_data": "menu_lookup"},
             {"text": "🧪 Test SK", "callback_data": "menu_test"}],
            [{"text": "📋 Commands", "callback_data": "menu_cmds"},
             {"text": "📊 Intents", "callback_data": "menu_intents"}],
        ]
    }

def back_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "🔙 Back", "callback_data": "menu_back"}]
        ]
    }

WELCOME_MSG = (
    f"{pe(E['gem'])} {bold('Stripe SK Bot')}\n\n"
    f"{pe(E['bolt'])} {bold('Generate Checkout Sessions')}\n"
    f"{pe(E['check'])} {bold('Look up SK information')}\n"
    f"{pe(E['globe'])} {bold('Test and verify Stripe keys')}\n\n"
    f"{pe(E['star'])} {bold('Use the menu below:')}"
)


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
    text = (
        f"{pe(E['gem'])} {bold('Stripe SK Bot Commands')}\n\n"
        f"{pe(E['bolt'])} /gen sk_xxx [amount] [currency] — {bold('Generate Checkout')}\n"
        f"{pe(E['link'])} /pay sk_xxx [amount] [currency] — {bold('Payment Link')}\n"
        f"{pe(E['bank'])} /lookup sk_xxx — {bold('Look up SK')}\n"
        f"{pe(E['check'])} /test sk_xxx — {bold('Test SK')}\n"
        f"{pe(E['bolt'])} /session sk_xxx session_id — {bold('Lookup Session')}\n"
        f"{pe(E['bolt'])} /intents sk_xxx [limit] — {bold('List Intents')}\n\n"
        f"{pe(E['star'])} {bold('Examples:')}\n"
        f"/gen sk_live_xxx 100 usd\n"
        f"/lookup sk_test_xxx"
    )
    await message.reply(text, reply_markup=back_keyboard())


# ── CALLBACKS ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_back")
async def cb_back(callback: types.CallbackQuery):
    await callback.answer()
    await safe_edit(callback.message, WELCOME_MSG, reply_markup=menu_keyboard())

@router.callback_query(F.data == "menu_cmds")
async def cb_cmds(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        f"{pe(E['gem'])} {bold('SK Bot Commands')}\n\n"
        f"/gen sk [amount] [currency] — {bold('Checkout')}\n"
        f"/pay sk [amount] [currency] — {bold('Payment Link')}\n"
        f"/lookup sk — {bold('Lookup SK')}\n"
        f"/test sk — {bold('Test SK')}\n"
        f"/session sk session_id — {bold('Lookup Session')}\n"
        f"/intents sk [limit] — {bold('List Intents')}"
    )
    await safe_edit(callback.message, text, reply_markup=back_keyboard())

@router.callback_query(F.data == "menu_checkout")
async def cb_checkout(callback: types.CallbackQuery):
    await callback.answer()
    text = f"{pe(E['gem'])} {bold('Checkout')}\n\n/gen sk_live_xxx 100 usd"
    await safe_edit(callback.message, text, reply_markup=back_keyboard())

@router.callback_query(F.data == "menu_paylink")
async def cb_paylink(callback: types.CallbackQuery):
    await callback.answer()
    text = f"{pe(E['link'])} {bold('Payment Link')}\n\n/pay sk_live_xxx 100 usd"
    await safe_edit(callback.message, text, reply_markup=back_keyboard())

@router.callback_query(F.data == "menu_lookup")
async def cb_lookup(callback: types.CallbackQuery):
    await callback.answer()
    text = f"{pe(E['bank'])} {bold('Lookup SK')}\n\n/lookup sk_live_xxx"
    await safe_edit(callback.message, text, reply_markup=back_keyboard())

@router.callback_query(F.data == "menu_test")
async def cb_test(callback: types.CallbackQuery):
    await callback.answer()
    text = f"{pe(E['check'])} {bold('Test SK')}\n\n/test sk_live_xxx 100 usd"
    await safe_edit(callback.message, text, reply_markup=back_keyboard())

@router.callback_query(F.data == "menu_intents")
async def cb_intents(callback: types.CallbackQuery):
    await callback.answer()
    text = f"{pe(E['bolt'])} {bold('List Intents')}\n\n/intents sk_live_xxx 10"
    await safe_edit(callback.message, text, reply_markup=back_keyboard())


# ── COMMAND HANDLERS ──────────────────────────────────────────────────────

@router.message(Command("gen"))
async def cmd_gen(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(f"{pe(E['warn'])} /gen sk_xxx [amount] [currency]")
        return
    
    text = args[1].strip()
    sk = extract_sk_from_text(text)
    if not sk:
        await message.reply(f"{pe(E['cross'])} No Stripe SK found!")
        return
    
    if not validate_sk(sk):
        await message.reply(f"{pe(E['cross'])} Invalid SK format!")
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
    
    loading = await message.reply(f"{pe(E['loading'])} Generating checkout...")
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, generate_checkout_session, sk, amount, currency
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} Error: {str(e)}")
        return
    
    if result.get("success"):
        await safe_edit(loading, format_session_result(result))
    else:
        await safe_edit(loading, f"{pe(E['cross'])} {result.get('error', 'Unknown error')}")


@router.message(Command("pay"))
async def cmd_pay(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(f"{pe(E['warn'])} /pay sk_xxx [amount] [currency]")
        return
    
    text = args[1].strip()
    sk = extract_sk_from_text(text)
    if not sk:
        await message.reply(f"{pe(E['cross'])} No Stripe SK found!")
        return
    
    if not validate_sk(sk):
        await message.reply(f"{pe(E['cross'])} Invalid SK format!")
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
    
    loading = await message.reply(f"{pe(E['loading'])} Generating payment link...")
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, generate_payment_link, sk, amount, currency
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} Error: {str(e)}")
        return
    
    if result.get("success"):
        await safe_edit(loading, format_payment_link_result(result))
    else:
        await safe_edit(loading, f"{pe(E['cross'])} {result.get('error', 'Unknown error')}")


@router.message(Command("lookup"))
async def cmd_lookup(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(f"{pe(E['warn'])} /lookup sk_xxx")
        return
    
    text = args[1].strip()
    sk = extract_sk_from_text(text)
    if not sk and message.reply_to_message:
        reply = message.reply_to_message.text or ""
        sk = extract_sk_from_text(reply)
    
    if not sk:
        await message.reply(f"{pe(E['cross'])} No Stripe SK found!")
        return
    
    if not validate_sk(sk):
        await message.reply(f"{pe(E['cross'])} Invalid SK format!")
        return
    
    loading = await message.reply(f"{pe(E['loading'])} Looking up key...")
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, lookup_key_info, sk
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} Error: {str(e)}")
        return
    
    await safe_edit(loading, format_lookup_result(result))


@router.message(Command("test"))
async def cmd_test(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(f"{pe(E['warn'])} /test sk_xxx [amount] [currency]")
        return
    
    text = args[1].strip()
    sk = extract_sk_from_text(text)
    if not sk:
        await message.reply(f"{pe(E['cross'])} No Stripe SK found!")
        return
    
    if not validate_sk(sk):
        await message.reply(f"{pe(E['cross'])} Invalid SK format!")
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
    
    loading = await message.reply(f"{pe(E['loading'])} Testing key...")
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, test_charge, sk, amount, currency
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} Error: {str(e)}")
        return
    
    await safe_edit(loading, format_test_result(result))


@router.message(Command("session"))
async def cmd_session(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(f"{pe(E['warn'])} /session sk_xxx session_id")
        return
    
    parts = args[1].split()
    if len(parts) < 2:
        await message.reply(f"{pe(E['warn'])} /session sk_xxx session_id")
        return
    
    sk = extract_sk_from_text(parts[0])
    if not sk:
        await message.reply(f"{pe(E['cross'])} No Stripe SK found!")
        return
    
    session_id = parts[1].strip()
    loading = await message.reply(f"{pe(E['loading'])} Looking up session...")
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, lookup_checkout_session, sk, session_id
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} Error: {str(e)}")
        return
    
    if result.get("success"):
        await safe_edit(loading, format_session_result(result))
    else:
        await safe_edit(loading, f"{pe(E['cross'])} {result.get('error', 'Unknown error')}")


@router.message(Command("intents"))
async def cmd_intents(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(f"{pe(E['warn'])} /intents sk_xxx [limit]")
        return
    
    parts = args[1].split()
    sk = extract_sk_from_text(parts[0])
    if not sk:
        await message.reply(f"{pe(E['cross'])} No Stripe SK found!")
        return
    
    limit = 10
    if len(parts) >= 2:
        try: limit = int(parts[1])
        except: pass
    
    loading = await message.reply(f"{pe(E['loading'])} Listing intents...")
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL, list_payment_intents, sk, limit
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} Error: {str(e)}")
        return
    
    if result.get("success"):
        lines = [
            f"{pe(E['bolt'])} {bold('Payment Intents')} ({result.get('count', 0)})",
            "━━━━━━━━━━━━━━━━━━━━",
        ]
        for intent in result.get("intents", []):
            lines.append(f"  • {intent['amount']} — {intent['status']} ({intent['created']})")
        if not result.get("intents"):
            lines.append("No payment intents found.")
        await safe_edit(loading, "\n".join(lines))
    else:
        await safe_edit(loading, f"{pe(E['cross'])} {result.get('error', 'Unknown error')}")


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    me = await bot.get_me()
    log.info(f"⚡ SK Bot @{me.username} is running...")
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