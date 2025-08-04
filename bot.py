import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ChatJoinRequestHandler

# Конфигурация
BOT_TOKEN = "8377374186:AAH9mLRNJxS6VjIvdWkxlFJkoRU5a0lEpSM"
CHANNEL_ID = -1001989783724  # Канал для проверки подписки
GROUP_ID = -1002873957981    # ID группы для автопринятия заявок
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
        
        # Проверяем подписку на канал
        chat_member = await bot.get_chat_member(CHANNEL_ID, user.id)
        
        if chat_member.status not in ["member", "administrator", "creator"]:
            await update.message.reply_text("❌ Ты не подписан на канал! Подпишись и попробуй снова.")
            logger.info(f"Отказ: пользователь {user.id} не подписан на канал")
            return

        # Отправляем готовую ссылку
        await bot.send_message(
            chat_id=user.id,
            text=f"✅ Доступ открыт! Жми на ссылку:\n\n{GROUP_INVITE_LINK}"
        )
        logger.info(f"Пользователь {user.id} получил ссылку")

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("⚠️ Ошибка. Сообщите админу.")

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    try:
        # Проверяем подписку на канал
        chat_member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
        
        if chat_member.status in ["member", "administrator", "creator"]:
            # Одобряем заявку
            await update.chat_join_request.approve()
            await context.bot.send_message(
                chat_id=user.id,
                text="✅ Ваша заявка одобрена! Добро пожаловать в группу."
            )
            logger.info(f"Заявка одобрена для {user.id}")
        else:
            await update.chat_join_request.decline()
            await context.bot.send_message(
                chat_id=user.id,
                text="❌ Вы не подписаны на наш канал. Подпишитесь и подайте заявку снова."
            )
            logger.info(f"Заявка отклонена для {user.id}")

    except Exception as e:
        logger.error(f"Ошибка при обработке заявки: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчик команды /start
    app.add_handler(CommandHandler("start", start))
    
    # Обработчик заявок на вступление (НОВАЯ ФУНКЦИЯ)
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    
    logger.info("Бот запущен с поддержкой заявок на вступление!")
    app.run_polling()

if __name__ == "__main__":
    main()
