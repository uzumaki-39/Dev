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
from aiogram.filters import Command, CommandStart  # <── FIXED: Added CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest
from stripe import StripeClient

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("sk_bot")

# ── Config ──────────────────────────────────────────────────────────────────
TOKEN = "8901668516:AAGrIt__UkH6gEGLQos6iHxv13yp6AVkFkw"  # <── REPLACE THIS

# ── Premium Emoji IDs (same as your bot.py) ──────────────────────────────
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

# ── Result emojis ───────────────────────────────────────────────────────────
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

# ── Thread pool for sync operations ───────────────────────────────────────
CHECKER_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=50)

# ── SK Tool Constants ──────────────────────────────────────────────────────
STRIPE_API_BASE = "https://api.stripe.com/v1"
DEFAULT_CURRENCY = "usd"
DEFAULT_AMOUNT = 100  # $1.00 in cents

# ── Key Validation Patterns ──────────────────────────────────────────────
SK_PATTERN = re.compile(r"^(sk_(?:live|test)_[A-Za-z0-9_\-]+)$")
PK_PATTERN = re.compile(r"^(pk_(?:live|test)_[A-Za-z0-9_\-]+)$")

# ── Session Response Patterns ────────────────────────────────────────────
CHECKOUT_URL_PATTERN = re.compile(r"https://checkout\.stripe\.com/c/pay/[a-zA-Z0-9_\-]+")
BILLING_URL_PATTERN = re.compile(r"https://billing\.stripe\.com/p/session/[a-zA-Z0-9_\-]+")
INVOICE_URL_PATTERN = re.compile(r"https://invoice\.stripe\.com/i/[a-zA-Z0-9_\-]+")
PAYMENT_LINK_PATTERN = re.compile(r"https://buy\.stripe\.com/[a-zA-Z0-9_\-]+")


# ═══════════════════════════════════════════════════════════════════════════
#  SK TOOL CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def validate_sk(sk: str) -> bool:
    """Validate Stripe secret key format."""
    return bool(SK_PATTERN.match(sk.strip()))

def validate_pk(pk: str) -> bool:
    """Validate Stripe publishable key format."""
    return bool(PK_PATTERN.match(pk.strip()))

def get_key_type(sk: str) -> str:
    """Return 'live' or 'test' for a Stripe key."""
    return "live" if "sk_live" in sk else "test"

def mask_key(key: str) -> str:
    """Mask a Stripe key for safe display."""
    if len(key) <= 16:
        return key[:8] + "…" + key[-4:]
    return key[:12] + "…" + key[-6:]

def get_stripe_client(sk: str) -> StripeClient:
    """Create a Stripe client from a secret key."""
    return StripeClient(sk)

def extract_sk_from_text(text: str) -> Optional[str]:
    """Extract Stripe secret key from text."""
    match = SK_PATTERN.search(text)
    return match.group(1) if match else None

def extract_pk_from_text(text: str) -> Optional[str]:
    """Extract Stripe publishable key from text."""
    match = PK_PATTERN.search(text)
    return match.group(1) if match else None

def extract_checkout_url(text: str) -> Optional[str]:
    """Extract Stripe checkout URL from text."""
    for pattern in [CHECKOUT_URL_PATTERN, BILLING_URL_PATTERN, INVOICE_URL_PATTERN, PAYMENT_LINK_PATTERN]:
        match = pattern.search(text)
        if match:
            return match.group(0)
    return None


# ── Checkout Session Generation ──────────────────────────────────────────

def generate_checkout_session(
    sk: str,
    amount: int = DEFAULT_AMOUNT,
    currency: str = DEFAULT_CURRENCY,
    product_name: str = "Bot Generated Product",
    success_url: str = "https://example.com/success",
    cancel_url: str = "https://example.com/cancel",
    customer_email: Optional[str] = None,
    metadata: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Generate a Stripe Checkout Session using a secret key."""
    try:
        client = get_stripe_client(sk)
        
        # ── Create a product ──
        product = client.products.create(
            name=product_name,
            metadata=metadata or {},
        )
        
        # ── Create a price ──
        price = client.prices.create(
            unit_amount=amount,
            currency=currency.lower(),
            product=product.id,
        )
        
        # ── Create checkout session ──
        session_params = {
            "line_items": [{"price": price.id, "quantity": 1}],
            "mode": "payment",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "payment_method_types": ["card"],
        }
        
        if customer_email:
            session_params["customer_email"] = customer_email
        
        if metadata:
            session_params["metadata"] = metadata
        
        session = client.checkout.sessions.create(**session_params)
        
        return {
            "success": True,
            "session_id": session.id,
            "checkout_url": session.url,
            "product_id": product.id,
            "price_id": price.id,
            "mode": session.mode,
            "currency": session.currency,
            "amount_total": session.amount_total,
            "customer_email": getattr(session, "customer_email", None),
            "customer": getattr(session, "customer", None),
            "payment_status": session.payment_status,
            "status": session.status,
            "created": session.created,
            "expires_at": session.expires_at,
            "key_type": get_key_type(sk),
            "masked_key": mask_key(sk),
        }
        
    except stripe.error.AuthenticationError as e:
        return {"success": False, "error": f"Invalid SK: {str(e)}", "code": "authentication_error"}
    except stripe.error.PermissionError as e:
        return {"success": False, "error": f"Permission denied: {str(e)}", "code": "permission_error"}
    except stripe.error.RateLimitError as e:
        return {"success": False, "error": f"Rate limited: {str(e)}", "code": "rate_limit"}
    except stripe.error.StripeError as e:
        return {"success": False, "error": f"Stripe error: {str(e)}", "code": "stripe_error"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}", "code": "unknown_error"}


def generate_payment_link(
    sk: str,
    amount: int = DEFAULT_AMOUNT,
    currency: str = DEFAULT_CURRENCY,
    product_name: str = "Bot Generated Product",
    metadata: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Generate a Stripe Payment Link (buy.stripe.com)."""
    try:
        client = get_stripe_client(sk)
        
        product = client.products.create(
            name=product_name,
            metadata=metadata or {},
        )
        
        price = client.prices.create(
            unit_amount=amount,
            currency=currency.lower(),
            product=product.id,
        )
        
        link = client.payment_links.create(
            line_items=[{"price": price.id, "quantity": 1}],
            metadata=metadata or {},
        )
        
        return {
            "success": True,
            "payment_link_id": link.id,
            "payment_link_url": link.url,
            "product_id": product.id,
            "price_id": price.id,
            "currency": link.currency,
            "amount": amount,
            "active": link.active,
            "created": link.created,
            "livemode": link.livemode,
            "key_type": get_key_type(sk),
            "masked_key": mask_key(sk),
        }
        
    except stripe.error.AuthenticationError as e:
        return {"success": False, "error": f"Invalid SK: {str(e)}", "code": "authentication_error"}
    except stripe.error.PermissionError as e:
        return {"success": False, "error": f"Permission denied: {str(e)}", "code": "permission_error"}
    except stripe.error.StripeError as e:
        return {"success": False, "error": f"Stripe error: {str(e)}", "code": "stripe_error"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}", "code": "unknown_error"}


# ── Key Lookup ────────────────────────────────────────────────────────────

def lookup_key_info(sk: str) -> Dict[str, Any]:
    """Look up information about a Stripe secret key."""
    try:
        client = get_stripe_client(sk)
        
        # ── Get account info ──
        try:
            account = client.accounts.retrieve()
        except stripe.error.InvalidRequestError:
            account = None
        
        # ── Get balance ──
        try:
            balance = client.balance.retrieve()
        except Exception:
            balance = None
        
        # ── Get balance transactions (last 5) ──
        try:
            transactions = client.balance_transactions.list(limit=5)
        except Exception:
            transactions = None
        
        result = {
            "success": True,
            "key_type": get_key_type(sk),
            "masked_key": mask_key(sk),
            "account": None,
            "balance": None,
            "transactions": [],
        }
        
        if account:
            result["account"] = {
                "id": account.id,
                "country": getattr(account, "country", "Unknown"),
                "email": getattr(account, "email", None),
                "business_name": getattr(account, "business_name", None),
                "business_type": getattr(account, "business_type", None),
                "charges_enabled": getattr(account, "charges_enabled", False),
                "payouts_enabled": getattr(account, "payouts_enabled", False),
                "default_currency": getattr(account, "default_currency", "usd"),
                "created": getattr(account, "created", None),
                "capabilities": getattr(account, "capabilities", {}),
            }
        
        if balance:
            result["balance"] = {
                "available": [
                    {"amount": b.amount, "currency": b.currency}
                    for b in getattr(balance, "available", [])
                ],
                "pending": [
                    {"amount": b.amount, "currency": b.currency}
                    for b in getattr(balance, "pending", [])
                ],
                "livemode": getattr(balance, "livemode", False),
            }
        
        if transactions:
            result["transactions"] = [
                {
                    "id": t.id,
                    "amount": t.amount,
                    "currency": t.currency,
                    "net": t.net,
                    "type": t.type,
                    "status": t.status,
                    "created": t.created,
                    "description": getattr(t, "description", ""),
                }
                for t in transactions
            ]
        
        return result
        
    except stripe.error.AuthenticationError as e:
        return {"success": False, "error": f"Invalid SK: {str(e)}", "code": "authentication_error"}
    except stripe.error.PermissionError as e:
        return {"success": False, "error": f"Permission denied: {str(e)}", "code": "permission_error"}
    except stripe.error.StripeError as e:
        return {"success": False, "error": f"Stripe error: {str(e)}", "code": "stripe_error"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}", "code": "unknown_error"}


def test_charge(sk: str, amount: int = 100, currency: str = "usd") -> Dict[str, Any]:
    """Test a Stripe key by attempting a payment intent creation."""
    try:
        client = get_stripe_client(sk)
        
        intent = client.payment_intents.create(
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
            "amount": intent.amount,
            "currency": intent.currency,
            "client_secret": intent.client_secret[:20] + "..." if intent.client_secret else None,
            "message": "Key is active and can create payment intents",
        }
        
    except stripe.error.AuthenticationError as e:
        return {"success": False, "error": f"Invalid SK: {str(e)}", "code": "authentication_error"}
    except stripe.error.PermissionError as e:
        return {"success": False, "error": f"Permission denied: {str(e)}", "code": "permission_error"}
    except stripe.error.InvalidRequestError as e:
        if "missing" in str(e).lower():
            return {
                "success": True,
                "key_type": get_key_type(sk),
                "masked_key": mask_key(sk),
                "message": "Key is active but needs additional parameters for charges",
                "error_detail": str(e)[:200],
            }
        return {"success": False, "error": f"Invalid request: {str(e)}", "code": "invalid_request"}
    except stripe.error.StripeError as e:
        return {"success": False, "error": f"Stripe error: {str(e)}", "code": "stripe_error"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}", "code": "unknown_error"}


def lookup_checkout_session(sk: str, session_id: str) -> Dict[str, Any]:
    """Look up a Stripe Checkout Session by ID."""
    try:
        client = get_stripe_client(sk)
        session = client.checkout.sessions.retrieve(session_id)
        
        return {
            "success": True,
            "session_id": session.id,
            "checkout_url": session.url,
            "mode": session.mode,
            "currency": session.currency,
            "amount_total": session.amount_total,
            "amount_subtotal": session.amount_subtotal,
            "customer": session.customer,
            "customer_email": session.customer_email,
            "payment_status": session.payment_status,
            "status": session.status,
            "expires_at": session.expires_at,
            "created": session.created,
            "livemode": session.livemode,
            "payment_intent": getattr(session, "payment_intent", None),
            "setup_intent": getattr(session, "setup_intent", None),
            "invoice": getattr(session, "invoice", None),
            "subscription": getattr(session, "subscription", None),
            "metadata": getattr(session, "metadata", {}),
        }
        
    except stripe.error.AuthenticationError as e:
        return {"success": False, "error": f"Invalid SK: {str(e)}", "code": "authentication_error"}
    except stripe.error.InvalidRequestError as e:
        return {"success": False, "error": f"Session not found: {str(e)}", "code": "not_found"}
    except stripe.error.StripeError as e:
        return {"success": False, "error": f"Stripe error: {str(e)}", "code": "stripe_error"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}", "code": "unknown_error"}


def list_payment_intents(sk: str, limit: int = 10) -> Dict[str, Any]:
    """List recent payment intents for the account."""
    try:
        client = get_stripe_client(sk)
        intents = client.payment_intents.list(limit=min(limit, 100))
        
        return {
            "success": True,
            "count": len(intents),
            "intents": [
                {
                    "id": i.id,
                    "amount": i.amount,
                    "currency": i.currency,
                    "status": i.status,
                    "created": i.created,
                    "payment_method": getattr(i, "payment_method", None),
                    "customer": getattr(i, "customer", None),
                }
                for i in intents
            ],
        }
        
    except stripe.error.AuthenticationError as e:
        return {"success": False, "error": f"Invalid SK: {str(e)}", "code": "authentication_error"}
    except stripe.error.PermissionError as e:
        return {"success": False, "error": f"Permission denied: {str(e)}", "code": "permission_error"}
    except stripe.error.StripeError as e:
        return {"success": False, "error": f"Stripe error: {str(e)}", "code": "stripe_error"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}", "code": "unknown_error"}


# ── Formatting Functions ──────────────────────────────────────────────────

def format_lookup_result(data: Dict[str, Any]) -> str:
    """Format lookup result for display."""
    if not data.get("success"):
        return f"{pe(E['cross'])} {bold('Error:')} {data.get('error', 'Unknown error')}"
    
    lines = [f"{pe(E['bank'])} {bold('Stripe SK Info')}"]
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"🔑 {bold('Key:')} {bold(data.get('masked_key', 'N/A'))}")
    lines.append(f"📊 {bold('Type:')} {bold(data.get('key_type', 'Unknown'))}")
    
    if data.get("account"):
        acc = data["account"]
        lines.append("")
        lines.append(f"📧 {bold('Email:')} {acc.get('email', 'N/A')}")
        lines.append(f"🏢 {bold('Business:')} {acc.get('business_name', 'N/A')}")
        lines.append(f"🌍 {bold('Country:')} {acc.get('country', 'N/A')}")
        lines.append(f"💰 {bold('Currency:')} {acc.get('default_currency', 'usd')}")
        lines.append(f"✅ {bold('Charges:')} {'Enabled' if acc.get('charges_enabled') else 'Disabled'}")
        lines.append(f"💸 {bold('Payouts:')} {'Enabled' if acc.get('payouts_enabled') else 'Disabled'}")
    
    if data.get("balance"):
        bal = data["balance"]
        available = []
        pending = []
        for b in bal.get("available", []):
            available.append(f"{b['amount']/100:.2f} {b['currency'].upper()}")
        for b in bal.get("pending", []):
            pending.append(f"{b['amount']/100:.2f} {b['currency'].upper()}")
        
        lines.append("")
        lines.append(f"💰 {bold('Balance (Available):')} {', '.join(available) or '0.00'}")
        lines.append(f"⏳ {bold('Balance (Pending):')} {', '.join(pending) or '0.00'}")
    
    if data.get("transactions"):
        lines.append("")
        lines.append(f"{pe(E['bolt'])} {bold('Recent Transactions:')}")
        for t in data["transactions"][:5]:
            amount = f"{t['amount']/100:.2f} {t['currency'].upper()}"
            lines.append(f"  • {t['type']} — {amount} — {t['status']}")
    
    return "\n".join(lines)


def format_session_result(data: Dict[str, Any]) -> str:
    """Format session generation result for display."""
    if not data.get("success"):
        return f"{pe(E['cross'])} {bold('Error:')} {data.get('error', 'Unknown error')}"
    
    lines = [
        f"{pe(E['gem'])} {bold('Checkout Session Generated!')}",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🔗 {bold('URL:')} <a href='{data.get('checkout_url', '#')}'>{data.get('checkout_url', 'N/A')[:50]}...</a>",
        f"📋 {bold('Session ID:')} <code>{data.get('session_id', 'N/A')}</code>",
        f"💰 {bold('Amount:')} {data.get('amount_total', 0)/100:.2f} {data.get('currency', 'usd').upper()}",
        f"📊 {bold('Status:')} {data.get('payment_status', 'N/A')}",
        f"⏰ {bold('Expires:')} {data.get('expires_at', 'N/A')}",
        f"🔑 {bold('Key Type:')} {data.get('key_type', 'test')}",
    ]
    
    if data.get("customer_email"):
        lines.append(f"📧 {bold('Customer:')} {data.get('customer_email')}")
    
    return "\n".join(lines)


def format_payment_link_result(data: Dict[str, Any]) -> str:
    """Format payment link result for display."""
    if not data.get("success"):
        return f"{pe(E['cross'])} {bold('Error:')} {data.get('error', 'Unknown error')}"
    
    amount = data.get('amount', DEFAULT_AMOUNT)
    currency = data.get('currency', 'usd')
    
    lines = [
        f"{pe(E['gem'])} {bold('Payment Link Generated!')}",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🔗 {bold('URL:')} <a href='{data.get('payment_link_url', '#')}'>{data.get('payment_link_url', 'N/A')}</a>",
        f"📋 {bold('Link ID:')} <code>{data.get('payment_link_id', 'N/A')}</code>",
        f"💰 {bold('Amount:')} {amount/100:.2f} {currency.upper()}",
        f"🔑 {bold('Key Type:')} {data.get('key_type', 'test')}",
    ]
    
    return "\n".join(lines)


def format_test_result(data: Dict[str, Any]) -> str:
    """Format test result for display."""
    if not data.get("success"):
        return f"{pe(E['cross'])} {bold('Key Test Failed!')}\n{data.get('error', 'Unknown error')}"
    
    lines = [
        f"{pe(E['check'])} {bold('Key Test Results')}",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🔑 {bold('Key:')} {bold(data.get('masked_key', 'N/A'))}",
        f"📊 {bold('Type:')} {bold(data.get('key_type', 'Unknown'))}",
        f"✅ {bold('Status:')} {bold('Active')}",
        f"💬 {data.get('message', 'Key is operational')}",
    ]
    if data.get("payment_intent_id"):
        lines.append(f"📋 {bold('Intent:')} <code>{data.get('payment_intent_id')}</code>")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
#  TELEGRAM BOT SETUP
# ═══════════════════════════════════════════════════════════════════════════

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ── Safe Edit ─────────────────────────────────────────────────────────────
async def safe_edit(msg: types.Message, text: str, **kwargs) -> bool:
    """Drop-in replacement for msg.edit_text() with flood-wait handling."""
    for attempt in range(3):
        try:
            await msg.edit_text(text, **kwargs)
            return True
        except TelegramRetryAfter as e:
            wait = min(e.retry_after + 1, 15)
            log.warning("FloodWait %ss on edit", wait)
            await asyncio.sleep(wait)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                return True
            log.error("safe_edit failed: %s", e)
            return False
        except Exception as e:
            log.error("safe_edit unexpected: %s", e)
            return False
    return False


# ── Menu Keyboard ─────────────────────────────────────────────────────────
def menu_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": f"{bold('Checkout')}", "callback_data": "menu_checkout", "style": "success"},
                {"text": f"{bold('Payment Link')}", "callback_data": "menu_paylink", "style": "success"},
            ],
            [
                {"text": f"{bold('Lookup SK')}", "callback_data": "menu_lookup", "style": "primary"},
                {"text": f"{bold('Test SK')}", "callback_data": "menu_test", "style": "primary"},
            ],
            [
                {"text": f"{bold('Commands')}", "callback_data": "menu_cmds", "style": "secondary"},
                {"text": f"{bold('Intents')}", "callback_data": "menu_intents", "style": "secondary"},  # <── ADDED
            ],
        ]
    }


def back_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": f"{bold('Back')}", "callback_data": "menu_back", "style": "primary"}]
        ]
    }


WELCOME_MSG = (
    f"{pe(E['gem'])} {bold('Stripe SK Bot')}\n\n"
    f"{pe(E['bolt'])} {bold('Generate Checkout Sessions')}\n"
    f"{pe(E['check'])} {bold('Look up SK information')}\n"
    f"{pe(E['globe'])} {bold('Test and verify Stripe keys')}\n\n"
    f"{pe(E['star'])} {bold('Use the menu below:')}"
)


# ── Start Command ──────────────────────────────────────────────────────────
@router.message(CommandStart())  # <── FIXED: Use CommandStart instead of Command("start")
async def cmd_start(message: types.Message):
    await message.reply(WELCOME_MSG, reply_markup=menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        f"{pe(E['gem'])} {bold('Stripe SK Bot Commands')}\n\n"
        f"{pe(E['bolt'])} /gen sk_xxx [amount] [currency] — {bold('Generate Checkout')}\n"
        f"{pe(E['link'])} /pay sk_xxx [amount] [currency] — {bold('Generate Payment Link')}\n"
        f"{pe(E['bank'])} /lookup sk_xxx — {bold('Look up SK info')}\n"
        f"{pe(E['check'])} /test sk_xxx — {bold('Test SK')}\n"
        f"{pe(E['bolt'])} /session sk_xxx session_id — {bold('Lookup Session')}\n"
        f"{pe(E['bolt'])} /intents sk_xxx [limit] — {bold('List Payment Intents')}\n\n"  # <── FIXED: removed E['list']
        f"{pe(E['star'])} {bold('Examples:')}\n"
        f"/gen sk_live_xxx 100 usd\n"
        f"/lookup sk_test_xxx\n"
        f"/test sk_live_xxx 500 eur"
    )
    await message.reply(text, reply_markup=back_keyboard())


# ── Callback Handlers ──────────────────────────────────────────────────────
@router.callback_query(F.data == "menu_back")
async def cb_menu_back(callback: types.CallbackQuery):
    await callback.answer()
    await safe_edit(callback.message, WELCOME_MSG, reply_markup=menu_keyboard())


@router.callback_query(F.data == "menu_cmds")
async def cb_menu_cmds(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        f"{pe(E['gem'])} {bold('SK Bot Commands')}\n\n"
        f"{pe(E['bolt'])} /gen sk [amount] [currency] — {bold('Generate Checkout')}\n"
        f"{pe(E['link'])} /pay sk [amount] [currency] — {bold('Generate Payment Link')}\n"
        f"{pe(E['bank'])} /lookup sk — {bold('Look up SK info')}\n"
        f"{pe(E['check'])} /test sk — {bold('Test SK')}\n"
        f"{pe(E['bolt'])} /session sk session_id — {bold('Lookup Session')}\n"
        f"{pe(E['bolt'])} /intents sk [limit] — {bold('List Intents')}"
    )
    await safe_edit(callback.message, text, reply_markup=back_keyboard())


@router.callback_query(F.data == "menu_checkout")
async def cb_menu_checkout(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        f"{pe(E['gem'])} {bold('Generate Checkout Session')}\n\n"
        f"{pe(E['bolt'])} {bold('Usage:')}\n"
        f"/gen sk_live_xxx 100 usd\n\n"
        f"{pe(E['star'])} {bold('Amount in cents (100 = $1.00)')}\n"
        f"{pe(E['globe'])} {bold('Currency:')} usd, eur, gbp, etc."
    )
    await safe_edit(callback.message, text, reply_markup=back_keyboard())


@router.callback_query(F.data == "menu_paylink")
async def cb_menu_paylink(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        f"{pe(E['link'])} {bold('Generate Payment Link')}\n\n"
        f"{pe(E['bolt'])} {bold('Usage:')}\n"
        f"/pay sk_live_xxx 100 usd\n\n"
        f"{pe(E['star'])} {bold('Creates a buy.stripe.com link')}"
    )
    await safe_edit(callback.message, text, reply_markup=back_keyboard())


@router.callback_query(F.data == "menu_lookup")
async def cb_menu_lookup(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        f"{pe(E['bank'])} {bold('Lookup SK Info')}\n\n"
        f"{pe(E['bolt'])} {bold('Usage:')}\n"
        f"/lookup sk_live_xxx\n\n"
        f"{pe(E['star'])} {bold('Shows:')}\n"
        f"• Account info\n"
        f"• Balance\n"
        f"• Recent transactions"
    )
    await safe_edit(callback.message, text, reply_markup=back_keyboard())


@router.callback_query(F.data == "menu_test")
async def cb_menu_test(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        f"{pe(E['check'])} {bold('Test SK')}\n\n"
        f"{pe(E['bolt'])} {bold('Usage:')}\n"
        f"/test sk_live_xxx 100 usd\n\n"
        f"{pe(E['star'])} {bold('Tests if the key can create payment intents')}"
    )
    await safe_edit(callback.message, text, reply_markup=back_keyboard())


@router.callback_query(F.data == "menu_intents")  # <── ADDED
async def cb_menu_intents(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        f"{pe(E['bolt'])} {bold('List Payment Intents')}\n\n"
        f"{pe(E['bolt'])} {bold('Usage:')}\n"
        f"/intents sk_live_xxx 10\n\n"
        f"{pe(E['star'])} {bold('Shows recent payment intents for the account')}"
    )
    await safe_edit(callback.message, text, reply_markup=back_keyboard())


# ── Command Handlers ───────────────────────────────────────────────────────

@router.message(Command("gen"))
async def cmd_gen(message: types.Message):
    """Generate a checkout session."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /gen sk_xxx [amount] [currency]\n"
            f"{pe(E['next'])} {bold('Example:')} /gen sk_live_xxx 100 usd"
        )
        return
    
    sk = extract_sk_from_text(args[1])
    if not sk:
        await message.reply(f"{pe(E['cross'])} {bold('No valid Stripe secret key found!')}")
        return
    
    if not validate_sk(sk):
        await message.reply(f"{pe(E['cross'])} {bold('Invalid SK format!')}")
        return
    
    rest = args[1].replace(sk, "").strip()
    parts = rest.split()
    amount = 100
    currency = "usd"
    
    if parts:
        try:
            amount = int(parts[0])
        except ValueError:
            pass
    if len(parts) >= 2:
        currency = parts[1].lower()[:3]
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Generating checkout...')}\n"
        f"🔑 {bold(mask_key(sk))}\n"
        f"💰 {bold(f'{amount/100:.2f} {currency.upper()}')}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL,
            generate_checkout_session,
            sk, amount, currency
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}")
        return
    
    text = format_session_result(result)
    await safe_edit(loading, text)


@router.message(Command("pay"))
async def cmd_pay(message: types.Message):
    """Generate a payment link."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /pay sk_xxx [amount] [currency]\n"
            f"{pe(E['next'])} {bold('Example:')} /pay sk_live_xxx 100 usd"
        )
        return
    
    sk = extract_sk_from_text(args[1])
    if not sk:
        await message.reply(f"{pe(E['cross'])} {bold('No valid Stripe secret key found!')}")
        return
    
    if not validate_sk(sk):
        await message.reply(f"{pe(E['cross'])} {bold('Invalid SK format!')}")
        return
    
    rest = args[1].replace(sk, "").strip()
    parts = rest.split()
    amount = 100
    currency = "usd"
    
    if parts:
        try:
            amount = int(parts[0])
        except ValueError:
            pass
    if len(parts) >= 2:
        currency = parts[1].lower()[:3]
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Generating payment link...')}\n"
        f"🔑 {bold(mask_key(sk))}\n"
        f"💰 {bold(f'{amount/100:.2f} {currency.upper()}')}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL,
            generate_payment_link,
            sk, amount, currency
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}")
        return
    
    text = format_payment_link_result(result)
    await safe_edit(loading, text)


@router.message(Command("lookup"))
async def cmd_lookup(message: types.Message):
    """Look up SK information."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /lookup sk_xxx\n"
            f"{pe(E['next'])} {bold('Or reply to a message containing an SK')}"
        )
        return
    
    sk = extract_sk_from_text(args[1])
    if not sk and message.reply_to_message:
        reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
        sk = extract_sk_from_text(reply_text)
    
    if not sk:
        await message.reply(f"{pe(E['cross'])} {bold('No valid Stripe secret key found!')}")
        return
    
    if not validate_sk(sk):
        await message.reply(f"{pe(E['cross'])} {bold('Invalid SK format!')}")
        return
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Looking up key...')}\n"
        f"🔑 {bold(mask_key(sk))}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL,
            lookup_key_info,
            sk
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}")
        return
    
    text = format_lookup_result(result)
    await safe_edit(loading, text)


@router.message(Command("test"))
async def cmd_test(message: types.Message):
    """Test a Stripe SK."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /test sk_xxx [amount] [currency]\n"
            f"{pe(E['next'])} {bold('Example:')} /test sk_live_xxx 100 usd"
        )
        return
    
    sk = extract_sk_from_text(args[1])
    if not sk:
        await message.reply(f"{pe(E['cross'])} {bold('No valid Stripe secret key found!')}")
        return
    
    if not validate_sk(sk):
        await message.reply(f"{pe(E['cross'])} {bold('Invalid SK format!')}")
        return
    
    rest = args[1].replace(sk, "").strip()
    parts = rest.split()
    amount = 100
    currency = "usd"
    
    if parts:
        try:
            amount = int(parts[0])
        except ValueError:
            pass
    if len(parts) >= 2:
        currency = parts[1].lower()[:3]
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Testing key...')}\n"
        f"🔑 {bold(mask_key(sk))}\n"
        f"💰 {bold(f'{amount/100:.2f} {currency.upper()}')}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL,
            test_charge,
            sk, amount, currency
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}")
        return
    
    text = format_test_result(result)
    await safe_edit(loading, text)


@router.message(Command("session"))
async def cmd_session(message: types.Message):
    """Look up a checkout session by ID."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /session sk_xxx session_id"
        )
        return
    
    parts = args[1].split()
    if len(parts) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /session sk_xxx session_id"
        )
        return
    
    sk = extract_sk_from_text(parts[0])
    if not sk:
        await message.reply(f"{pe(E['cross'])} {bold('No valid Stripe secret key found!')}")
        return
    
    if not validate_sk(sk):
        await message.reply(f"{pe(E['cross'])} {bold('Invalid SK format!')}")
        return
    
    session_id = parts[1].strip()
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Looking up session...')}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL,
            lookup_checkout_session,
            sk, session_id
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}")
        return
    
    if result.get("success"):
        text = format_session_result(result)
        await safe_edit(loading, text)
    else:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Failed!')}\n{result.get('error', 'Unknown error')}")


@router.message(Command("intents"))
async def cmd_intents(message: types.Message):
    """List recent payment intents."""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            f"{pe(E['warn'])} {bold('Usage:')} /intents sk_xxx [limit]"
        )
        return
    
    parts = args[1].split()
    sk = extract_sk_from_text(parts[0])
    if not sk:
        await message.reply(f"{pe(E['cross'])} {bold('No valid Stripe secret key found!')}")
        return
    
    if not validate_sk(sk):
        await message.reply(f"{pe(E['cross'])} {bold('Invalid SK format!')}")
        return
    
    limit = 10
    if len(parts) >= 2:
        try:
            limit = int(parts[1])
        except ValueError:
            pass
    
    loading = await message.reply(
        f"{pe(E['loading'])} {bold('Listing intents...')}"
    )
    
    try:
        result = await asyncio.get_running_loop().run_in_executor(
            CHECKER_POOL,
            list_payment_intents,
            sk, limit
        )
    except Exception as e:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Error:')} {str(e)}")
        return
    
    if result.get("success"):
        lines = [
            f"{pe(E['bolt'])} {bold('Payment Intents')} ({result.get('count', 0)})",
            "━━━━━━━━━━━━━━━━━━━━",
        ]
        for intent in result.get("intents", []):
            amount = f"{intent['amount']/100:.2f} {intent['currency'].upper()}"
            status_emoji = "✅" if intent['status'] == 'succeeded' else "⏳" if intent['status'] == 'requires_payment_method' else "❌"
            lines.append(f"{status_emoji} {intent['id'][:20]}... — {amount} — {intent['status']}")
        
        if not result.get("intents"):
            lines.append("No payment intents found.")
        
        await safe_edit(loading, "\n".join(lines))
    else:
        await safe_edit(loading, f"{pe(E['cross'])} {bold('Failed!')}\n{result.get('error', 'Unknown error')}")


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    me = await bot.get_me()
    log.info(f"⚡ SK Bot @{me.username} is running...")
    
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(
            bot,
            skip_updates=True,
            allowed_updates=["message", "callback_query"],
        )
    finally:
        CHECKER_POOL.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot stopped.")