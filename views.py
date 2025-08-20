import discord
from discord import Embed

from utility import safe_edit_message

active_events = {}


class ActivityView(discord.ui.View):
    def __init__(self, message_id: int, role_id: int):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.role_id = role_id

    @discord.ui.button(label="✅ Участвую", style=discord.ButtonStyle.success)
    async def going_button(self, button, interaction: discord.Interaction):
        event = active_events[self.message_id]
        user_id = interaction.user.id
        event["not_going"].discard(user_id)
        event["going"].add(user_id)
        await self.update_embed(interaction)

    @discord.ui.button(label="❌ Не участвую", style=discord.ButtonStyle.danger)
    async def not_going_button(self, button, interaction: discord.Interaction):
        event = active_events[self.message_id]
        user_id = interaction.user.id
        event["going"].discard(user_id)
        event["not_going"].add(user_id)
        await self.update_embed(interaction)

    @discord.ui.button(label="🛑 Завершить", style=discord.ButtonStyle.blurple)
    async def finish_button(self, button, interaction: discord.Interaction):
        self.clear_items()
        await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction):
        event = active_events[self.message_id]
        guild = interaction.guild
        role_members = {m.id for m in guild.get_role(event["role_id"]).members}

        undecided = role_members - event["going"] - event["not_going"]

        def format_list(user_ids):
            if not user_ids:
                return "—"
            return "\n".join(f"<@{uid}>" for uid in user_ids)

        embed = Embed(title=event['title'], description=f"Дата и время: {event['time']}", color=0x00ff00)
        embed.add_field(name="✅ Участвую", value=format_list(event["going"]), inline=True)
        embed.add_field(name="❌ Не участвую", value=format_list(event["not_going"]), inline=True)
        embed.add_field(name="🕒 Не принял решение", value=format_list(undecided), inline=True)

        await safe_edit_message(interaction=interaction, embed=embed, view=self)
        await interaction.response.defer()

