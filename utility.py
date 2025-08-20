import asyncio
import json
import os
import time
from functools import wraps

import discord

CHANNELS_ROLES_FILE = "channels_roles.json"
_last_edit_time = 0


def load_channel_roles():
    try:
        with open(CHANNELS_ROLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_channel_roles(data):
    with open(CHANNELS_ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


async def safe_edit_message(interaction: discord.Interaction = None, message: discord.Message = None, *, embed=None,
                            view=None):
    """Безопасное редактирование сообщения с защитой от rate limit"""
    global _last_edit_time
    now = time.time()
    delay = now - _last_edit_time
    if delay < 1:
        await asyncio.sleep(1 - delay)
    _last_edit_time = time.time()
    try:
        if interaction:
            await interaction.message.edit(embed=embed, view=view)
        elif message:
            await message.edit(embed=embed, view=view)
    except discord.NotFound:
        #Сообщение удалено
        await interaction.response.send_message("Сообщение удалено", ephemeral=True)
    except discord.HTTPException as e:
        print(f"Ошибка редактирования сообщения: {e}")


MODER_FILE = "moderators.json"


def load_moder_roles():
    if not os.path.exists(MODER_FILE):
        return {}
    with open(MODER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_moder_roles(data: dict):
    with open(MODER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def moder_only():
    def predicate(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            data = load_moder_roles()
            guild_id = str(ctx.guild.id)

            allowed_roles = data.get(guild_id, [])

            # Проверяем, есть ли у автора хотя бы одна разрешённая роль
            if not any(r.id in allowed_roles for r in ctx.author.roles):
                await ctx.respond("❌ У вас нет прав для использования этой команды.", ephemeral=True)
                return

            return await func(ctx, *args, **kwargs)
        return wrapper
    return predicate
