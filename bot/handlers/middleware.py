from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from typing import Callable, Dict, Any, Awaitable

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Проверяем, что событие — это сообщение (не callback, не inline-запрос и т. д.)
        if not isinstance(event, Message):
            return await handler(event, data)  # пропускаем дальше, если это не Message

        print(f"Юзер {event.from_user.id} отправил сообщение: {event.text}")
        return await handler(event, data)