import pandas as pd
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get

# load tokens from .env file
load_dotenv()

# ATTEMPTS_CSV = 'CSE221-attempts.csv'

# CSV file location containing student information: std_id, name, section, attempts
INFO_CSV = 'CSE221-student-info.csv'

client = discord.Client()
bot = commands.Bot(command_prefix='!')


# def find_attempts_csv(file, author):
#     df = pd.read_csv(file)
#     idx = df.index[df.user_id == author.id]
#     if len(idx):  # if author is found
#         return df.attempts[idx].tolist()[0]
#     else:
#         df.loc[len(df.index)] = [author.id, 2]
#         df.to_csv(file, index=False)
#         return 2
#
#
# def decrease_attempts(file, author):  # does not check remaining attempts
#     df = pd.read_csv(file)
#     idx = df.index[df.user_id == author.id]
#     if len(idx):  # if author id is found
#         df.at[idx, 'attempts'] = df.attempts[idx].tolist()[0] - 1
#         df.to_csv(file, index=False)
#         return True
#     return False


def find_member_csv(file, sid):
    sid = int(sid)
    student_id = name = section = ""
    attempts = 0
    df = pd.read_csv(file)
    idx = df.index[df.std_id == sid]
    if len(idx):
        student_id = df.std_id[idx].tolist()[0]
        name = df.name[idx].tolist()[0]
        section = df.section[idx].tolist()[0]
        attempts = df.attempts[idx].tolist()[0]
        if attempts == 0:
            return student_id, name, section, attempts

        df.at[idx, 'attempts'] = attempts - 1
        df.to_csv(file, index=False)
    print(f'student_id\t: {student_id}\nname\t:{name}\nsection\t:{section}')
    return student_id, name, section, attempts


# Check if author has a role: in_role
def has_role(author, in_role):
    for role in author.roles:
        if role.name == in_role:
            return True
    else:
        return False


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
    channel = message.channel
    author = message.author
    content = message.content
    print(f'{author.id}:{author.name}#{author.discriminator}')
    if author.bot:
        pass
    elif content.startswith('!'):
        await bot.process_commands(message)
    elif channel.name in ['verify-me', 'test-bot']:

        if author.top_role.name in ['faculty', 'student-tutor']:
            await message.channel.send(f'Sorry. You are not eligible for verification!')
            return

        is_verified = False

        if len(content) == 8 and content.isdigit():
            print(f'A student ID {content} found')
            is_verified = author.top_role.name == "student"
            if is_verified:
                await message.channel.send(
                    f'You are already verified as {author.mention}.\n'
                    f'Contact your faculty for further '
                    f'change')
                return

            (student_id, name, section, attempts) = find_member_csv(INFO_CSV, content)

            if attempts == 0:
                await message.channel.send(f'A member with this id exists already. \n'
                                           f'In case you find something fishy, contact your faculty asap.')
                return

            # print(f'student_id\t: {student_id}\nname\t:{name}\nsection\t:{section}')
            if student_id:
                is_verified = True

                # change nickname
                nickname = f'{section}_{student_id}_{name}'
                await author.edit(nick=nickname[0:32])
                print(f'nickname set successfully for {author.name}')

                # set student role
                role = get(author.guild.roles, name=f'student')
                await author.add_roles(role)
                # set section role
                role = get(author.guild.roles, name=f'section-{section}')
                await author.add_roles(role)
                print(f'role {role.name} set successfully for {author.name}')
                await message.channel.send(f'Congratulations! You are now verified.\n'
                                           f'Your nickname is changed to {author.mention}\n'
                                           f'And two roles are set for you: **student** and **section-{section}**.\n'
                                           f'In case the above information is not correct, '
                                           f'contact your theory faculty.')

        if not is_verified:
            await message.channel.send(f'Something went wrong. Please provide your **8 digit student id**.')


# @bot.command(pass_context=True)
# async def user_info(ctx, user: discord.Member):
#     await ctx.send(f'The username of the user is {user.name}')
#     await ctx.send(f'The ID of the user is {user.id}')
#     await ctx.send(f'The status of the user is {user.status}')
#     await ctx.send(f'The role of the user is {user.top_role}')
#     await ctx.send(f'The user joined at {user.joined_at}')
#
#


@bot.command(pass_context=True)
@has_permissions(administrator=True)
async def remove(ctx, user: discord.Member, *, reason=None):
    await user.kick(reason=reason)
    await ctx.send(f'The Kicking Hammer Has Awoken! {user.name} Has Been Banished')


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command()
@has_permissions(administrator=True)
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)


# @bot.command()
# @has_permissions(administrator=True)
# async def clearChannel(ctx, channelName, amount):
#     channel = discord.utils.get(ctx.guild.channels, name=channelName)
#     await channel.purge(limit=amount)

# Remove all members from a server except admins
# and those whose top_role are placed above the bot in the roles page
@bot.command()
@has_permissions(administrator=True)
async def removeR(ctx, role: discord.Role, *, reason=None):
    for member in bot.get_all_members():
        if role in member.roles:  # does member have the specified role?
            try:
                await member.kick(reason=reason)
                await ctx.send(f' {member.name} removed')
            except:
                await ctx.send(f'Permission Error: Skipping member: {member.name}')


@bot.command()
@has_permissions(administrator=True)
async def getAllChannels(ctx):
    for channel in bot.get_all_channels():
        await ctx.send(f'member: {channel.name}')


bot.run('TOKEN')
