import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ─── Configurações ────────────────────────────────────────────────────────────
TOKEN = os.environ.get("BOT_TOKEN", "8727130976:AAHIE79Th7uYamez4os-2pFos2IDPpMkblo")
API_BASE = os.environ.get("API_BASE", "http://212.227.7.153:9945")
MASTER_KEY = os.environ.get("MASTER_KEY", "43FUHF78FWIUTPULMH")

WHATSAPP_CHANNEL = "https://whatsapp.com/channel/0029VbCu4r23WHTYia22EO3N"

# ─── Estados da conversa ──────────────────────────────────────────────────────
AGUARDANDO_KEY, AGUARDANDO_NOVO_IP = range(2)

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── Helpers de API ───────────────────────────────────────────────────────────
def api_check_key(generated_key: str) -> dict:
    """Consulta informações da key via /check."""
    try:
        resp = requests.get(
            f"{API_BASE}/check",
            params={"key": MASTER_KEY, "generated_key": generated_key},
            timeout=10,
        )
        return {"ok": resp.status_code == 200, "data": resp.json() if resp.content else {}, "status": resp.status_code}
    except Exception as e:
        logger.error(f"Erro ao checar key: {e}")
        return {"ok": False, "data": {}, "status": 0}


def api_update_ip(generated_key: str, new_ip: str) -> dict:
    """Atualiza o IP da key via /update."""
    try:
        resp = requests.get(
            f"{API_BASE}/update",
            params={"key": MASTER_KEY, "generated_key": generated_key, "new_ip": new_ip},
            timeout=10,
        )
        return {"ok": resp.status_code == 200, "data": resp.json() if resp.content else {}, "status": resp.status_code, "raw": resp.text}
    except Exception as e:
        logger.error(f"Erro ao atualizar IP: {e}")
        return {"ok": False, "data": {}, "status": 0, "raw": str(e)}


# ─── Handlers ─────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa e solicita a key."""
    context.user_data.clear()
    await update.message.reply_text(
        "🔑 *Atualização de IP — Proxy Manager*\n\n"
        "Olá! Para atualizar o IP da sua key, por favor *envie a key* que deseja atualizar:",
        parse_mode="Markdown",
    )
    return AGUARDANDO_KEY


async def receber_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recebe a key, consulta o IP atual e solicita o novo IP."""
    key = update.message.text.strip()
    context.user_data["generated_key"] = key

    await update.message.reply_text("⏳ Consultando informações da key, aguarde...")

    resultado = api_check_key(key)

    if not resultado["ok"]:
        await update.message.reply_text(
            f"❌ *Key não encontrada ou inválida.*\n\n"
            f"Verifique a key e tente novamente com /start.",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    data = resultado["data"]
    ip_atual = data.get("ip", data.get("current_ip", "Não disponível"))
    context.user_data["ip_atual"] = ip_atual

    await update.message.reply_text(
        f"✅ *Key encontrada!*\n\n"
        f"🔑 *Key:* `{key}`\n"
        f"🌐 *IP atual:* `{ip_atual}`\n\n"
        f"Agora envie o *novo IP* que deseja registrar nesta key:",
        parse_mode="Markdown",
    )
    return AGUARDANDO_NOVO_IP


async def receber_novo_ip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recebe o novo IP e exibe botões de confirmação."""
    novo_ip = update.message.text.strip()
    context.user_data["novo_ip"] = novo_ip

    key = context.user_data["generated_key"]
    ip_atual = context.user_data.get("ip_atual", "Não disponível")

    keyboard = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data="confirmar"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancelar"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"⚠️ *Confirme a atualização de IP*\n\n"
        f"🔑 *Key:* `{key}`\n"
        f"🌐 *IP atual:* `{ip_atual}`\n"
        f"🆕 *Novo IP:* `{novo_ip}`\n\n"
        f"Deseja realmente atualizar o IP desta key?",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
    return AGUARDANDO_NOVO_IP


async def callback_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a confirmação e chama a API de atualização."""
    query = update.callback_query
    await query.answer()

    key = context.user_data.get("generated_key")
    novo_ip = context.user_data.get("novo_ip")

    await query.edit_message_text(
        f"⏳ Atualizando IP da key `{key}`, aguarde...",
        parse_mode="Markdown",
    )

    resultado = api_update_ip(key, novo_ip)

    if resultado["ok"]:
        await query.edit_message_text(
            f"✅ *IP atualizado com sucesso!*\n\n"
            f"🔑 *Key:* `{key}`\n"
            f"🌐 *Novo IP registrado:* `{novo_ip}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📢 *Fique por dentro de tudo!*\n\n"
            f"Entre no nosso *Canal Oficial do WhatsApp* e aproveite:\n\n"
            f"🎁 Sorteios de keys diárias\n"
            f"🔥 Promoções exclusivas\n"
            f"📣 Novidades e atualizações\n\n"
            f"👉 [Clique aqui para entrar no canal]({WHATSAPP_CHANNEL})\n\n"
            f"_Não perca nenhuma oportunidade! 🚀_",
            parse_mode="Markdown",
            disable_web_page_preview=False,
        )
    else:
        raw = resultado.get("raw", "Sem detalhes")
        await query.edit_message_text(
            f"❌ *Falha ao atualizar o IP.*\n\n"
            f"🔑 *Key:* `{key}`\n"
            f"📋 *Resposta da API:* `{raw}`\n\n"
            f"Tente novamente com /start.",
            parse_mode="Markdown",
        )

    context.user_data.clear()
    return ConversationHandler.END


async def callback_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela a operação."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🚫 *Operação cancelada.*\n\n"
        "Nenhuma alteração foi realizada. Use /start para começar novamente.",
        parse_mode="Markdown",
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancelar_comando(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler para o comando /cancelar."""
    context.user_data.clear()
    await update.message.reply_text(
        "🚫 *Operação cancelada.*\n\nUse /start para começar novamente.",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde a mensagens fora de contexto."""
    await update.message.reply_text(
        "ℹ️ Use /start para iniciar a atualização de IP da sua key.",
    )


# ─── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AGUARDANDO_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_key)
            ],
            AGUARDANDO_NOVO_IP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receber_novo_ip),
                CallbackQueryHandler(callback_confirmar, pattern="^confirmar$"),
                CallbackQueryHandler(callback_cancelar, pattern="^cancelar$"),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancelar_comando)],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    logger.info("Bot iniciado com sucesso!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
