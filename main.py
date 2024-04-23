import discord
from discord import Intents
from discord.ext import commands
from secret import TOKEN
import datetime
import time
from db import users


CHANNEL_ID = 1209491033474342976 #1073113435660886107

bot = commands.Bot(intents=Intents.default(), command_prefix="!")


limits = {
    "@everyone": 3
}


@bot.event
async def on_ready():
    print(f'Bot is running!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except:
        pass


@bot.tree.command(name="voice_kick", description="Kicks user from voice channel")
async def voice_kick(interaction: discord.Interaction, user: discord.Member):
    if user.voice is None:
        await interaction.response.send_message(
            f"You can't kick this user, science they aren't in voice channel.")
        return
    if user.id == interaction.user.id:
        await interaction.response.send_message(
            f"You can't your self from voice channel.")
        return
    d = datetime.datetime.now(tz=datetime.timezone.utc)
    used_today = 0
    if user.id in users:
        for time_ in users[user.id]:
            if time_ == str(d.date()):
                used_today += 1

    limit = 0
    for role in user.roles:
        print(role.name)
        if role.name in limits:
            limit = max(limit, limits[role.name])

    if used_today >= limit:
        await interaction.response.send_message(f"You ran out of kicks.\nYou will get your `{limit}` kicks <t:{int(time.time()//1+(23-d.hour)*60*60+(60-d.minute)*60+(60-d.second))}:R>")
        return

    await interaction.response.send_message(f"You kicked {user.name} from voice channel!\nKicks left: `{limit-used_today-1}`")

    try:
        await user.move_to(None)
    except Exception as e:
        print(e)

    if user.id in users:
        users[user.id].append(str(d.date()))
    else:
        users[user.id] = [str(d.date())]

    with open("db.py","w") as f:
        f.write(f"users = {users}")


bot.run(token=TOKEN)
