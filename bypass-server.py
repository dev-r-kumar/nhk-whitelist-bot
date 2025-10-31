import time, json, os
import discord
from discord.ext import commands
from keep_alive import keep_alive
import base64

keep_alive() # new 

whitelist_db_path = os.path.join(os.path.dirname(__file__), "whitelist.json")


def get_token():
    token_path = os.path.join(os.path.dirname(__file__), "token.json")
    with open(token_path, 'r') as token_file:
        token = json.load(token_file)['token']

    unpad_token = str(token).replace("====", "")
    final_token = base64.b64decode(unpad_token).decode()

    return final_token


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return 
    
    await bot.process_commands(message)


@bot.command()
async def whitelist(ctx, *, uid):
    uid = int(uid)

    with open(whitelist_db_path, 'r') as f:
        data = json.load(f)

    current_time = int(time.time())
    add_time = 2 * 60 * 60
    updated = False

    # Check if UID exists
    for entry in data:
        if entry['uid'] == uid:
            whitelist_expiry = entry.get("expiry", 0)

            if current_time >= whitelist_expiry:
                # Extend expiry
                entry['expiry'] = current_time + add_time

                embed = discord.Embed(
                    title="UID Bypass !",
                    description=(
                        f"status: **Whitelist Success ✅**, duration extended.\n"
                        f"UID: **{uid}**\nTime Added: **2 hours**"
                    ),
                    color=discord.Color.green()
                )

            else:
                embed = discord.Embed(
                    title="UID Bypass !",
                    description=(
                        f"status: **Whitelist Failed ❌**, cannot whitelist uid now.\n"
                        f"UID: **{uid}**\nReason: **Already whitelisted !**"
                    ),
                    color=discord.Color.red()
                )

            await ctx.send(f'{ctx.author.mention}', embed=embed)
            updated = True
            break

    # If not found, add new entry
    if not updated:
        data.append({
            "uid": uid,
            "expiry": current_time + add_time
        })

        embed = discord.Embed(
            title="UID Bypass !",
            description=(
                f"status: **Whitelist Success ✅**.\n"
                f"UID: **{uid}**\nTime Added: **2 hours**"
            ),
            color=discord.Color.green()
        )

        await ctx.send(f'{ctx.author.mention}', embed=embed)

    # Save the updated list
    with open(whitelist_db_path, 'w') as f:
        json.dump(data, f, indent=2)



if __name__ == "__main__":
    bot.run(token=get_token())


