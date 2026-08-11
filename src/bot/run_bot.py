from datetime import timedelta

import discord
from discord.ext import commands

from src.core import ensure_utf8
from src.bot.config import Config, load_config
from src.bot.moderator import ChatModerator
from src.bot.store import Store

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

config: Config | None = None
moderator: ChatModerator | None = None


@bot.event
async def on_ready():
    print(f"Conectado como {bot.user} (ID {bot.user.id})")
    await bot.tree.sync()
    print("Comandos sincronizados")


def _should_monitor(channel_id):
    ids = config.monitor_channel_ids
    return not ids or channel_id in ids


@bot.event
async def on_message(message):
    if message.author.bot or not message.content.strip():
        return
    if message.guild is None or not _should_monitor(message.channel.id):
        return

    result = moderator.moderate(
        message.content,
        guild_id=str(message.guild.id),
        user_id=str(message.author.id),
        channel_id=str(message.channel.id),
    )

    if result.block:
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        try:
            await message.author.timeout(
                discord.utils.utcnow() + timedelta(seconds=config.timeout_seconds),
                reason="Mensaje bloqueado por el moderador",
            )
        except discord.Forbidden:
            pass
        await message.channel.send(
            f"{message.author.mention} tu mensaje fue bloqueado "
            f"({result.source}: {result.decision.label}).",
            delete_after=8,
        )
    elif result.needs_review:
        if config.review_channel_id:
            channel = bot.get_channel(config.review_channel_id)
            if channel is None:
                try:
                    channel = await bot.fetch_channel(config.review_channel_id)
                except discord.DiscordException:
                    channel = None
            if channel is not None:
                await channel.send(
                    f"[REVISION HUMANA] {message.author} en #{message.channel}: "
                    f"{message.content} (prob. {result.prob:.2f})"
                )
                return
        await message.channel.send(
            f"{message.author.mention} tu mensaje sera revisado por un moderador "
            f"({result.decision.label}).",
            delete_after=8,
        )
    elif result.action == "advertencia":
        await message.channel.send(
            f"{message.author.mention} advertencia: {result.decision.label}.", delete_after=8
        )

    if config.log_channel_id:
        channel = bot.get_channel(config.log_channel_id)
        if channel is not None:
            await channel.send(
                f"`{result.source}` {result.decision.label} ({message.author}): "
                f"{message.content[:200]}"
            )


@bot.tree.command(name="moderate", description="Analiza un mensaje con ambos sistemas")
async def moderate_cmd(interaction: discord.Interaction, mensaje: str):
    guild_id = str(interaction.guild.id) if interaction.guild else "dm"
    result = moderator.moderate(mensaje, guild_id=guild_id, user_id=str(interaction.user.id))
    tradicional = result.traditional.label if result.traditional else "-"
    prob = f" | prob. IA {result.prob:.2f}" if result.prob is not None else ""
    await interaction.response.send_message(
        f"**Tradicional:** {tradicional}\n"
        f"**Resultado ({result.source}):** {result.decision.label}{prob}",
        ephemeral=True,
    )


@bot.tree.command(name="reputacion", description="Muestra la reputacion acumulada de un usuario")
async def reputacion_cmd(interaction: discord.Interaction, usuario: discord.Member):
    rep = moderator.store.get_reputation(str(interaction.guild.id), str(usuario.id))
    await interaction.response.send_message(
        f"Reputacion de {usuario.mention}: {rep:.2f}", ephemeral=True
    )


def main():
    global config, moderator
    ensure_utf8()
    config = load_config()
    if not config.token:
        raise SystemExit(
            "Falta DISCORD_TOKEN en el archivo .env (usa .env.example como plantilla)"
        )
    print("Cargando moderadores (tradicional + IA)...")
    from src.ai.inference import ToxicClassifier

    moderator = ChatModerator(
        store=Store(config.db_path),
        ai=ToxicClassifier(config.model_dir),
        umbral_bloqueo=config.umbral_bloqueo,
        umbral_revision=config.umbral_revision,
    )
    print("Listo.")
    bot.run(config.token)


if __name__ == "__main__":
    main()
