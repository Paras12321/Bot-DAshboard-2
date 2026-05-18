import asyncio
from telegram import Bot
from telegram.error import TelegramError, InvalidToken, Forbidden


class TelegramBotHandler:
    async def send_message(self, token: str, chat_id: str, message: str) -> dict:
        try:
            bot = Bot(token=token)

            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML"
            )

            print(f"[Telegram] Message sent to chat {chat_id}")
            return {
                "status": "success",
                "detail": f"Message sent to chat {chat_id}"
            }

        except InvalidToken:
            print(f"[Telegram] Invalid token")
            return {"status": "failed", "detail": "Invalid bot token"}

        except Forbidden:
            print(f"[Telegram] Bot blocked or chat not found: {chat_id}")
            return {
                "status": "failed",
                "detail": "Bot is blocked or chat not found"
            }

        except TelegramError as e:
            print(f"[Telegram] Error: {e}")
            return {"status": "failed", "detail": str(e)}

        except Exception as e:
            print(f"[Telegram] Unexpected error: {e}")
            return {"status": "failed", "detail": str(e)}

    async def validate_token(self, token: str) -> bool:
        try:
            bot = Bot(token=token)
            user = await bot.get_me()
            return user is not None
        except Exception:
            return False

    async def get_bot_info(self, token: str) -> dict:
        try:
            bot = Bot(token=token)
            user = await bot.get_me()
            return {
                "id": user.id,
                "name": user.first_name,
                "username": user.username,
                "is_bot": user.is_bot
            }
        except Exception as e:
            return {"error": str(e)}

    async def close_all(self):
        """Shut down all cached bot sessions gracefully."""
        pass

telegram_handler = TelegramBotHandler()