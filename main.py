import discord
from discord import Intents
from discord.ext import commands
from secret import TOKEN
from role_limits_file import LIMITS
import datetime
import time
from users_file import users


CHANNEL_ID = 1209491033474342976 #1073113435660886107

bot = commands.Bot(intents=Intents.default(), command_prefix="!")


@bot.event
async def on_ready():
    print(f'Bot is running!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


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
        if role.id in LIMITS:
            limit = max(limit, LIMITS[role.id])

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

    with open("users_file.py", "w") as f:
        f.write(f"users = {users}")


@bot.tree.command(name="set_role_limit", description="Sets role kicks limit")
async def set_role_limit(interaction: discord.Interaction, role: discord.Role, new_limit: int):
    if not interaction.user.guild_permissions.administrator:
        return
    LIMITS[role.id] = new_limit
    with open("role_limits_file.py","w") as f:
        f.write(f"LIMITS = {LIMITS}")

    await interaction.response.send_message(f"Successfully changed kicks limit of role <@&{role.id}> to `{new_limit}`")


@bot.tree.command(name="limits", description="Shows kicks limits for all roles")
async def limits(interaction: discord.Interaction):
    msg = "Kicks limits for roles:"
    for role in sorted([(LIMITS[i],i) for i in LIMITS])[::-1]:
        msg += f"\n<@&{role[1]}>: `{role[0]}`"
    await interaction.response.send_message(msg)


bot.run(token=TOKEN)
