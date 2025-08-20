import json
import os

import discord
from discord import Embed, Option, TextChannel, Role, Interaction, ButtonStyle
from discord.ext import commands
from dotenv import load_dotenv

from utility import load_channel_roles, save_channel_roles, moder_only, load_moder_roles, \
    save_moder_roles
from views import ActivityView, active_events

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user.name}")


@bot.slash_command(name="moder_set", description="Назначить роль модераторской")
@commands.has_permissions(administrator=True)  # только админ сервера
async def moder_set(ctx, role: discord.Role):
    data = load_moder_roles()
    guild_id = str(ctx.guild.id)

    if guild_id not in data:
        data[guild_id] = []

    if role.id not in data[guild_id]:
        data[guild_id].append(role.id)
        save_moder_roles(data)
        await ctx.respond(f"✅ Роль {role.mention} добавлена как модераторская.", ephemeral=True)
    else:
        await ctx.respond(f"⚠ Роль {role.mention} уже модераторская.", ephemeral=True)


# --- Команда для установки связки канал → роль ---
@bot.slash_command(name="setchrl", description="Установить связку канал → роль для 'Не принял решение'")
@moder_only()
async def setchrl(
        ctx,
        channel: Option(TextChannel, description="Канал"),
        role: Option(Role, description="Роль для поля 'Не принял решение'")
):
    data = load_channel_roles()
    data[str(channel.id)] = role.id
    save_channel_roles(data)
    await ctx.respond(f"✅ Связка установлена: {channel.mention} → {role.mention}", ephemeral=True)


# --- Команда /create ---
@bot.slash_command(name="create", description="Создать активность")
@moder_only()
async def create_activity(ctx, title=Option(str, "Название", name="название"), time=Option(str, "Время", name="время")):
    await ctx.defer(ephemeral=True)
    # Проверка, есть ли канал в JSON
    data = load_channel_roles()
    role_id = data.get(str(ctx.channel.id))
    if not role_id:
        await ctx.respond(
            "❌ Роль для канала не определена. Сначала используйте команду /setchrl",
            ephemeral=True
        )
        return

    role = ctx.guild.get_role(role_id)

    # Создаём embed
    embed = Embed(title=title, description=f"Дата и время: **{time}**", color=0x00ff00)
    embed.add_field(name="✅ Участвую", value="—", inline=True)
    embed.add_field(name="❌ Не участвую", value="—", inline=True)
    embed.add_field(
        name="🕒 Не принял решение",
        value="\n".join(f"<@{m.id}>" for m in role.members) if role.members else "—",
        inline=True
    )

    # Отправляем embed
    msg = await ctx.send(embed=embed)
    active_events[msg.id] = {
        "going": set(),
        "not_going": set(),
        "role_id": role.id,
        "title": title,
        "time": time
    }
    view = ActivityView(message_id=msg.id, role_id=role.id)
    await msg.edit(view=view)

bot.run(TOKEN)
