import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ChatJoinRequestHandler

# Конфигурация
BOT_TOKEN = "8377374186:AAH9mLRNJxS6VjIvdWkxlFJkoRU5a0lEpSM"
CHANNEL_ID = -1001989783724  # ID канала для проверки подписки
GROUP_ID = -1002873957981    # ID группы для автопринятия заявок
GROUP_INVITE_LINK = "https://t.me/+W60fzUwV7DE2YTZi"  # Ваша готовая ссылка

# Фикс для Render Free Tier (предотвращает "засыпание")
keep_alive = Flask(__name__)

@keep_alive.route('/')
def home():
    return "Bot keep-alive is active!"

def run_flask():
    keep_alive.run(host='0.0.0.0', port=5000)

Thread(target=run_flask, daemon=True).start()

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        await update.message.reply_text(f"🔍 Проверяю подписку, {user.first_name}...")
        
        # Проверка подписки с таймаутом
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=CHANNEL_ID,
                user_id=user.id,
                read_timeout=10,
                write_timeout=10
            )
        except Exception as e:
            logger.error(f"Ошибка проверки подписки: {e}")
            await update.message.reply_text("⌛ Сервер перегружен. Попробуйте через минуту.")
            return

        if chat_member.status not in ["member", "administrator", "creator"]:
            await update.message.reply_text("❌ Вы не подписаны на необходимый канал!")
            return

        # Красивое оформление сообщения с кнопкой
        keyboard = [
            [InlineKeyboardButton("👉 ПРИСОЕДИНИТЬСЯ К ГРУППЕ", url=GROUP_INVITE_LINK)]
        ]
        
        await context.bot.send_message(
            chat_id=user.id,
            text="✅ <b>Доступ открыт!</b>\n\nЖмите на кнопку ниже:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        logger.info(f"Пользователь {user.id} получил ссылку")

    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        await update.message.reply_text("🔴 Произошла системная ошибка. Админ уведомлен.")

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    try:
        # Проверка подписки
        chat_member = await context.bot.get_chat_member(
            CHANNEL_ID,
            user.id,
            read_timeout=10
        )
        
        if chat_member.status in ["member", "administrator", "creator"]:
            await update.chat_join_request.approve()
            await context.bot.send_message(
                chat_id=user.id,
                text="🎉 Добро пожаловать в группу!"
            )
            logger.info(f"Заявка одобрена: {user.id}")
        else:
            await update.chat_join_request.decline()
            await context.bot.send_message(
                chat_id=user.id,
                text="❌ Вы не подписаны на необходимый канал!"
            )
            logger.info(f"Заявка отклонена: {user.id}")

    except Exception as e:
        logger.error(f"Ошибка обработки заявки: {e}")

def main():
    # Инициализация с таймаутами
    app = Application.builder() \
        .token(BOT_TOKEN) \
        .read_timeout(20) \
        .write_timeout(20) \
        .build()
    
    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    
    logger.info("🟢 Бот запущен | Версия 3.2 | Render Fix")
    app.run_polling(
        close_loop=False,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
