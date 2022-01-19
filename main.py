import os
import discord
import sys
from discord.ext import commands
from googletrans import Translator
from discord_slash import SlashCommand, SlashContext
import random
import asyncio 

bot = commands.Bot(command_prefix='z!')

def restart_bot(): 
  os.execv(sys.executable, ['python'] + sys.argv)

bot.remove_command('help')

# My sample help command:
@bot.command()
async def help(ctx, args=None):
    help_embed = discord.Embed(title="My Bot's Help!")
    command_names_list = [x.name for x in bot.commands]

    # If there are no arguments, just list the commands:
    if not args:
        help_embed.add_field(
            name="List of supported commands:",
            value="\n".join([str(i+1)+". "+x.name for i,x in enumerate(bot.commands)]),
            inline=False
        )
        help_embed.add_field(
            name="Details",
            value="Type `.help <command name>` for more details about each command.",
            inline=False
        )

    # If the argument is a command, get the help text from that command:
    elif args in command_names_list:
        help_embed.add_field(
            name=args,
            value=bot.get_command(args).help
        )

    # If someone is just trolling:
    else:
        help_embed.add_field(
            name="Nope.",
            value="Don't think I got that command, boss!"
        )

    await ctx.send(embed=help_embed)



@bot.command()
async def ping(ctx):
    await ctx.send('pong')
   
@bot.command(name= 'restart')
async def restart(ctx):
  await ctx.send("Restarting bot...")
  restart_bot() 

  
@bot.command()
async def say(ctx, *, question):
    await ctx.message.delete()
    await ctx.send(f'{question}')
 
@bot.command(name='clear', help='this command will clear msgs')
async def clear(ctx, amount = 5):
    await ctx.channel.purge(limit=amount)
 
@bot.command(name='banword', aliases=['bw'])
async def ban_word(self, ctx, word: str, paranoia: int):
        '''Bans a phrase from user messages.
        ```css
        Example Usage:
        ``````py
        ?banword badword 0  # Bans "badword from messages with level 0 paranoia."
        ``````py
        ?bw badword 2  # Bans "bad word" from messages with paranoia level 2.
        Levels of paranoia:
        ```k
        (assume "badword" is banned)
        0 | Exact word - badword (✓) bad word (✓) motherbadword (x) nobadwordplz (x)
        1 | Root word match - badword (✓) bad word (✓) motherbadword (✓) nobadwordplz (x)
        2 | Any match - badword (✓) bad word (✓) motherbadword (✓) nobadwordplz (✓)
        ```
        '''
        msg = ctx.message
        guild = ctx.guild
        author = ctx.author
        fd = await read('banWords', True, False)

        if guild.id in fd:
            guild_list = fd[guild.id]

        else:
            guild_list = []

        if word.lower() not in [w['word'] for w in guild_list]:
            print('appending')
            guild_list.append({'word': word.lower(), 'paranoia': paranoia})

        else:
            await ctx.send(
                f"`{word}` is already in the server's ban list!"
            )
            return

        fd[guild.id] = guild_list
        await write('banWords', fd, False)
        await self.log(
            ctx,
            f"<@{author.id}> added `{word}` to the server's ban list.",
            '**Banword**',
            showauth=True
        )
        await ctx.send(f"`{word}` has been added to the server's ban list.")
  
  
@bot.command(name='banreaction', aliases=['br'])
async def ban_reaction(self, ctx, *_):
        '''Bans a reaction.
        ```css
        Example Usage:
        ``````css
        ?banreaction ✅ //Bans the reaction ✅
        ```'''
        msg = ctx.message
        guild = ctx.guild
        author = ctx.author
        phrase = msg.content.split(None, 1)[1]
        lower_phrase = phrase.lower()
        fd = await read('banEmojis', True, False)

        if guild.id in fd:
            guild_list = fd[guild.id]

        else:
            guild_list = []

        if lower_phrase not in guild_list:
            guild_list.append(lower_phrase)
            failed = False

        else:
            await ctx.send(
                f"`{phrase}` is already in the server's ban list!"
            )
            failed = True

        if not failed:
            fd[guild.id] = guild_list
            await write('banEmojis', fd, False)
            await self.log(
                ctx,
                f"<@{author.id}> added `{phrase}` to the server's ban list.",
                '**Ban reaction**',
                showauth=True
            )
            await ctx.send(f"`{phrase}` has been added to the server's ban list.")
 
 
 
  
@bot.command(name='unbanword', aliases=['unbw'])
async def unban_word(self, ctx, word: str):
        '''Unbans a string or word from user messages.
        ```css
        example usage:
        ``````fix
        unbanword allseeingbot
        ``````fix
        unbw all seeing bot'''
        msg = ctx.message
        guild = ctx.guild
        author = ctx.author
        fd = await read('banWords', True, False)

        if guild.id in fd:
            guild_list = fd[guild.id]

        else:
            guild_list = []

        exists = [w for w in guild_list if w['word'] == word]

        if exists == []:
            await ctx.send(
                f"`{word}` is not in the server's ban list!"
            )

        word = exists[0]

        guild_list.remove(word)

        fd[guild.id] = guild_list
        await write('banWords', fd, False)
        await self.log(
            ctx,
            f"<@{author.id}> removed `{word}` from the server's ban list.",
            '**Banword**',
            showauth=True
        )
        await ctx.send(f"`{word}` has been removed from the server's ban list.")
  
  
@bot.command(name='kick', aliases=['k'])
async def kick(self, ctx, user: discord.Member, *_):
        '''Kick a user.
        ```css
        Example Usage:```
        ```css
        ?kick <user> bc i can // Kicks <user> for bc i can```'''
        msg = ctx.message
        author = ctx.author
        try:
            reason = msg.content.split(None, 1)[1]
            found_reason = True
        except IndexError:
            found_reason = False
        if found_reason:
            await self.log(
                ctx,
                f'<@{author.id} kicked <@{user.id}>',
                fields=[
                    ('**Reason:**', reason)
                ]
            )
            await user.kick(reason=reason)
        else:
            await self.log(
                ctx,
                f'<@{author.id}> kicked <@{user.id}>'
            )
            await user.kick()
  
@bot.command(name='mute', aliases=['silence'])
async def mute(self, ctx, user: discord.Member, time=None, *argv):
        '''Mute a user so that they cannot send messages anymore.
        ```css
        Example Usage:
        ``````css
        ?mute <user> 5d bc i can // Mutes <user> for 5 days with the reason because i can.
        ``````css
        ?mute <user> bc i can // Mutes <user> permanately for reason bc i can
        ```'''

        fields = []
        guild = ctx.guild
        if time is not None:
            try:
                duration = find_date(time)
                end_date = duration + datetime.now()

                end_date = end_date.strftime('%Y-%m-%w-%W %H:%M:%S')
                mute_list = await read('muteList')
                if str(guild.id) in mute_list:
                    guild_list = mute_list[str(guild.id)]
                else:
                    guild_list = {}
                guild_list[user.id] = end_date

                mute_list[str(guild.id)] = guild_list
                await write('muteList', mute_list)
                fields.append(
                    ('**Duration:**', f'`{time}`', True)
                )
            except InvalidDate:
                argv = list(argv)
                argv.insert(0, time)

        author = ctx.author
        if len(argv) > 0:
            reason = ' '.join(argv)
            fields.append(
                ('**Reason:**', reason, True)
            )

        await self.log(
            ctx,
            f'<@{author.id}> muted <@{user.id}>',
            fields=fields,
            showauth=True
        )
        muted_role = await get_muted_role(guild)
        await user.add_roles(muted_role)
        embed = discord.Embed(
            title='**Mute**',
            description=f'<@{user.id}> has been muted.',
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='unmute')
async def unmute(self, ctx, user: discord.Member, *argv):
        '''Unmute a user.
        ```css
        Example usage:
        ``````css
        ?unmute <user> oops wrong person // Unbans <user> for the reason oops wrong person.
        ```'''
        fields = []
        guild = ctx.guild

        mute_list = await read('muteList')
        if guild.id in mute_list:
            if user.id in mute_list:
                del mute_list[guild.id][user.id]
                await write('muteList', mute_list)

        author = ctx.author
        try:
            reason = ' '.join(argv)
            fields.append(
                ('**Reason:**', reason, True)
            )
        except IndexError:
            pass

        await self.log(
            ctx,
            f'<@{author.id}> unmuted <@{user.id}>',
            fields=fields,
            showauth=True
        )
        muted_role = await get_muted_role(guild)
        await user.remove_roles(muted_role)



@bot.command(name='warn', aliases=['hint', 'suggest'])
async def warn(self, ctx, user: discord.Member, *argv):
        '''Warn a user.
        ```css
        Example Usage:
        ``````css
        ?warn <user> dont say that word // Warns <user> dont say that word.```'''
        guild = ctx.guild
        author = ctx.author
        warn_dict = await read('warn_list')
        reason = ' '.join(argv)
        if str(guild.id) in warn_dict:
            guild_warn_dict = warn_dict[str(guild.id)]

        else:
            guild_warn_dict = {}

        date = datetime.now()
        date_str = date.strftime('%Y-%m-%w-%W %H:%M:%S')
        if str(user.id) in guild_warn_dict:
            user_warns = guild_warn_dict[str(user.id)]
        else:
            user_warns = []

        warn_info = {
            'type': 'warn',
            'moderator': author.id,
            'reason': reason,
            'date': date_str
        }

        user_warns.append(warn_info)

        guild_warn_dict[str(user.id)] = user_warns

        warn_dict[str(guild.id)] = guild_warn_dict

        await write('warn_list', warn_dict)
        warn_embed = discord.Embed(
            title='**You have been warned.**',
            description=f'You have been warned on `{guild.name}`.',
            color=0xff0000
        )
        warn_embed.add_field(
            name='**Reason:**',
            value=reason
        )
        await user.send(embed=warn_embed)

        await self.log(
            ctx,
            f'<@{author.id}> warned <@{user.id}>.',
            title='**Warn**',
            fields=[('**Warn Content:**', reason)],
            showauth=True
        )
        embed = discord.Embed(
            title='**Warn**',
            description=f'Warned <@{user.id}>.',
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='selfhistory')
async def self_history(self, ctx):
        '''List a user's warns.
        ```css
        Example Usage:
        ``````css
        ?history <user> // Get a list of <user>'s warns'''
        user = ctx.author
        warns = await read('warn_list')

        guild = ctx.guild
        if str(guild.id) not in warns:
            await user.send("User has not been warned.")
            return

        guild_warns = warns[str(guild.id)]

        if str(user.id) not in guild_warns:
            await user.send("User has not been warned.")
            return

        user_warns = guild_warns[str(user.id)]

        if len(user_warns) == 0:
            await user.send("User has not been warned.")
            return

        fields = []
        warn_count = 0
        strike_count = 0
        icin = 0

        for w in user_warns:

            if w['type'] == 'strike':
                strike_count += 1
            else:
                warn_count += 1

            value = ''

            value += f'Type: **{w["type"]}**\n'
            value += f'Reason: ***{w["reason"]}***\n'
            value += f'Timestamp: **{w["date"]}**'
            # print(value)
            fields.append((f'ICIN **{icin}**:', value))
            icin += 1

        max_warn_counts = await read('wl')
        if guild.id in max_warn_counts:
            max_warns = max_warn_counts[guild.id]
        else:
            max_warns = 3

        max_strike_counts = await read('sl')
        if guild.id in max_strike_counts:
            max_strikes = max_strike_counts[guild.id]
        else:
            max_strikes = 5

        strikes_from_warns = int(
            (warn_count - (warn_count % max_warns)) / max_warns)
        remaining_warns = warn_count % max_warns
        created_at = user.created_at
        created_at_str = created_at.strftime('%Y-%m-%w-%W %H:%M:%S')
        desc = f'''
		Total Warnings: **{remaining_warns}/{max_warns}**
		Total Strikes: **{strikes_from_warns + strike_count}/{max_strikes}**
		Strikes from warnings: **{strikes_from_warns}**
		Account Creation Date: **{created_at_str}**
		'''

        embed = discord.Embed(
            title=f"{user.display_name}'s History",
            description=desc,
            color=0x8002d4
        )

        embed.set_thumbnail(url=user.avatar_url)

        for f in fields:
            embed.add_field(
                name=f[0],
                value=f[1],
                inline=False
            )

        await user.send(embed=embed)

@bot.command(aliases=["memes", "r/memes", "reddit"])
async def meme(self, ctx, subred="memes"):
        msg = await ctx.send('Loading ... <a:Loading:845258574434795570>')

        reddit = praw.Reddit(client_id='ID',
                             client_secret='SECRET',
                             username="USERNAME",
                             password='PASSWORD',
                             user_agent='AGENT')

        subreddit = reddit.subreddit(subred)
        all_subs = []
        top = subreddit.top(limit=350)

        for submission in top:
            all_subs.append(submission)

        random_sub = random.choice(all_subs)

        name = random_sub.title
        url = random_sub.url

        embed = Embed(title=f'__{name}__', colour=discord.Colour.random(), 
                      timestamp=ctx.message.created_at, url=url)

        embed.set_image(url=url)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f'Bot by {botowner}', icon_url=avatarowner)
        await ctx.send(embed=embed)
        await msg.edit(content=f'<https://reddit.com/r/{subreddit}/>  :white_check_mark:')
        return

@bot.command()
async def ask(ctx):

        _list = [
        'question_1', 
        'question_2']

        list1 = random.choice(_list)

        def answer():
            answer = "-1"
            if _list[0] == list1:
                answer = "1"
            else: 
                answer = "2"
            return answer

        await ctx.send("What is the answer to this question?")
        await asyncio.sleep(1)
        await ctx.send(list1)
        def check(m): return m.author == ctx.author and m.channel == ctx.channel

        msg = await client.wait_for('message', check=check, timeout=None)

        if msg.content == answer():
            await ctx.send("good")
        else:
            await ctx.send("no")
  
@bot.command(pass_context = True)
async def chatbot(ctx, *, message):
    result = chat.respond(message)
    if(len(result)<=2048):
        embed=discord.Embed(title="ChatBot AI", description = result, color = (0xF48D1))
        await ctx.send(embed=embed)
    else:
        embedList = []
        n=2048
        embedList = [result[i:i+n]for i in range(0, len(result), n)]
        for num, item in enumerate(embedList, start = 1):
            if(num == 1):
                embed = discord.Embed(title="ChatBot AI", description = item, color = (0xF48D1))
                embed.set_footer(text="Page{}".format(num))
                await ctx.send(embed = embed)
            else:
                eembed = discord.Embed(description = item, color = (0xF48D1))
                embed.st_footer(text = "Page {}".format(num))
                await ctx.send(embed = embed)

@bot.command()
async def testserverinfo(ctx, guild: discord.Guild = None):
    guild = ctx.message.guild
    roles =[role for role in guild.roles]
    text_channels = [text_channels for text_channels in guild.text_channels]
    embed = discord.Embed(title=f'{guild.name} sunucusunun bilgileri', description="Coded by VideroDesigns.#9999", timestamp=ctx.message.created_at, color=discord.Color.red())
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name="Kanal Sayısı:", value=f"{len(text_channels)}")
    embed.add_field(name="Rol Sayısı:", value=f"{len(roles)}")
    embed.add_field(name="Booster Sayısı:", value=guild.premium_subscription_count)
    embed.add_field(name="Üye Sayısı:", value=guild.member_count)
    embed.add_field(name="Kuruluş Tarihi:", value=guild.created_at)
    embed.add_field(name="Sunucu Sahibi:", value=guild.owner)
    embed.set_footer(text=f"Komut {ctx.author} tarafından kullanıldı.", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='generate_verification', help='Generates verification message')
async def generate_verification(self, ctx):


        message = await ctx.send(" Click the ✅ reaction to verify yourself")

        verification_message_id = message.id


        # Check if Verification role already exists

        if not get(ctx.guild.roles, name="Verified"):
            perms = discord.Permissions()
            perms.general()
            perms.text()
            perms.voice()

            await ctx.guild.create_role(name="Verified", permissions=perms, colour=discord.Colour(0x00bd09))

        await message.add_reaction("✅")

def setup(bot):
    bot.add_cog(Verification(bot))

@bot.command(pass_context=True)
async def test(ctx):
    if ctx.message.author.server_permissions.administrator:
        testEmbed = discord.Embed(color = discord.Color.red())
        testEmbed.set_author(name='Test')
        testEmbed.add_field(name='Test', value='Test')

    msg = await bot.send_message(ctx.message.channel, embed=testEmbed)
    await bot.add_reaction(msg, emoji='✅')


@bot.command()
async def create(ctx, arg: str):
   channel = await ctx.guild.create_text_channel(arg, category=discord.utils.get(ctx.guild.categories, name='FORUM'))

@bot.command()
async def announce(self, ctx):
    # Find a channel from the guilds `text channels` (Rather then voice channels)
    # with the name announcements
    channel = discord.utils.get(ctx.guild.text_channels, name="announcements")
    if channel: # If a channel exists with the name

                embed = discord.Embed(color=discord.Color.dark_gold(), timestamp=ctx.message.created_at)
                embed.set_author(name="Announcement", icon_url=self.client.user.avatar_url)
                embed.add_field(name=f"Sent by {ctx.message.author}", value=str(message), inline=False)
                embed.set_thumbnail(url=self.client.user.avatar_url)
                embed.set_footer(text=self.client.user.name, icon_url=self.client.user.avatar_url)
                await ctx.message.add_reaction(emoji="✅")
                await channel.send(embed=embed)


@bot.command(name="Search", aliases=["search"])
async def _search(self, ctx, *, message):
        if not ctx.author.Bot:
            guild = ctx.guild
            msg = ctx.message
            cli = self.client.user
            gold = discord.Color.dark_gold()
            embed = discord.Embed(color=gold, name=f"{image.name}", description=f"{image.desc}", timestamp=msg.created_at)
            embed.set_image(url=f"{image.url}")
            embed.set_thumbnail(url=cli.avatar_url)
            embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            await ctx.send(embed=embed)
            return


def setup(client):
    client.add_cog(Util(client))


@bot.command()
async def restartBot(ctx):
    await ctx.bot.logout()


@bot.command(name="translator", aliases=['ts','TS','Ts'])   
async def translator(ctx , frm=None, to=None,*,message):
     if to==None and frm==None:
      await ctx.send('Your words here')
     else: 
      google=translators.google(message, from_language=frm , to_language=to)
      await ctx.send(google)

@bot.command()
async def server(ctx):
    name = str(ctx.guild.name)
    description = str(ctx.guild.description)
    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    region = str(ctx.guild.region)
    memberCount = str(ctx.guild.member_count)
    icon = str(ctx.guild.icon_url)

    embed = discord.Embed(
        title = name + " Server Information",
        description = description,
        color=discord.Color.dark_red()
    )
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Server ID", value=id, inline=True)
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Member Count", value=memberCount, inline=True)

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    activity = discord.Game(name="Coding", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("Bot is ready!")
