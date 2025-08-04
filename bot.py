import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Конфигурация
BOT_TOKEN = "8377374186:AAH9mLRNJxS6VjIvdWkxlFJkoRU5a0lEpSM"
CHANNEL_ID = -1001989783724  # Канал для проверки подписки
GROUP_INVITE_LINK = "https://t.me/+W60fzUwV7DE2YTZi"  # Ваша готовая ссылка

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🔍 Проверяю подписку на канал, {user.first_name}...")

    try:
        bot = context.bot
        
        # 1. Проверяем подписку на канал
        chat_member = await bot.get_chat_member(CHANNEL_ID, user.id)
        
        if chat_member.status not in ["member", "administrator", "creator"]:
            await update.message.reply_text("❌ Ты не подписан на канал! Подпишись и попробуй снова.")
            logger.info(f"Отказ: пользователь {user.id} не подписан на канал")
            return

        # 2. Отправляем готовую ссылку
        await bot.send_message(
            chat_id=user.id,
            text=f"✅ Доступ открыт! Жми на ссылку:\n\n{GROUP_INVITE_LINK}"
        )
        logger.info(f"Пользователь {user.id} получил ссылку")

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("⚠️ Ошибка. Сообщите админу.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()