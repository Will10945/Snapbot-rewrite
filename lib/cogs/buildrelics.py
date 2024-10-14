import discord
import random
from discord.ext import commands
# import relicbuilderv2
import datetime
import time
import json
import string
import random

primeaccess = {}

class BuildRelics(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.client.cogs_ready.ready_up('build_relics')


    @commands.command(name='asdf',
        aliases=['asd'],
        brief='   Creates a fake set of unvault relics', 
        help=('**Creates relics based on the given parameters** \n'
            'You can choose between duplicates(default) or junk parts to fill extra space.\n\n'
            'Include frames to build relics for frames of your choosing\n\n'
            'Use \"random\" to build relics for random frames (default 2)\n\n'
            'Use \"fake\" to build relics from Guthixbot\'s \"--fakeunvault\" command \n'
            '(Guthixbot message must be within the 5 most recent messages in the channel)'),
        usage='<Frame Frame ...> <d/j>\n\"fake\" <d/j>\n\"random\" <number of frames> <d/j>'
    )

    async def asdf(self, ctx):

        allowedchannels = [
            780393312695746580,     #VRC bot-spamm
            851251652492525569,     #ME asd
            777976661307424798,     #INQ bot-spam
            849126576879828993,     #WDFA relic
            780378403127689227,     #VRC Staff Bot Spam
        ]

        if ctx.message.channel.id not in allowedchannels and ctx.author.id != 148706546308612096 and ctx.message.author.guild_permissions.administrator:
            await ctx.message.delete(delay=3)
            await ctx.send('Command not allowed in this channel', delete_after=3)

        else:
            with open('bot_data.json') as f:
                primeaccesstemp = json.load(f)
            primeaccess = primeaccesstemp['prime access']
            primeaccesslist = list(primeaccess)

            cancelbuild = False
            inlist = ''
            inlistoriginal = ''
            cancelmessage = ''
            messageauthor = ''
            messageserver = ''
            dupe = True
            messagestodelete = []

            goodframes = []
            badframes = ''
            dupeframes = ''

            doctoredmessage = ''

            author = None
            server = None
            textchannel = None

            try:
                server = ctx.guild.name
            except:
                print('No server in most recent message')
            try:
                textchannel = ctx.channel
            except:
                print('No text channel in most recent message')
            try:
                author = ctx.author
            except:
                print('No author in most recent message')

            def check(ctx):
                try:
                    ctxguildname = ctx.guild.name
                except:
                    ctxguildname = None
                if not ctxguildname and ctx.author == author and ctx.guild.name == server and ctx.channel == textchannel:
                    messagestodelete.append(ctx)
                    return (ctx.author == author and ctx.guild.name == server and ctx.channel == textchannel)
                elif not ctxguildname and ctx.author == author:
                    messagestodelete.append(ctx)
                    return (ctx.author == author and ctx.channel == textchannel)
                else:
                    return (ctx.author == author and ctx.channel == textchannel)

            def checkframesin(message):
        
                fgoodframes = []
                fbadframes = ''
                fdupeframes = ''

                if 's!buildrelics' in message:
                    message = message[14:]
                elif 's!build' in message:
                    message = message[8:]

                for x in message.split(' '):
                    if x[0].upper() + x[1:].lower() in primeaccesslist:
                        if x in fgoodframes:
                            if x not in fdupeframes:
                                fdupeframes += x + ', '
                        else:
                            fgoodframes.append(x)
                            #print(fgoodframes)
                    else:
                        fbadframes += x + ', '
                fbadframes = fbadframes[:-2]

                return fgoodframes, fbadframes, fdupeframes

            def buildrandom(amount, noexcal):

                goodframes = []

                primeaccesslisttemp = primeaccesslist.copy()
                random.shuffle(primeaccesslisttemp)

                for x in (range(amount if amount < len(primeaccesslist) else len(primeaccesslist))):
                    if len(primeaccesslisttemp) == 0:
                        break
                    if noexcal and 'Excalibur' in primeaccesslisttemp[0]:
                        del(primeaccesslisttemp[0])
                    else:
                        goodframes.append(primeaccesslisttemp[0])
                        del(primeaccesslisttemp[0])

                return goodframes
            
            if 'fake' in ctx.message.content.lower():
                recentmessage = ''
                nofake = False
                async for mess in ctx.message.channel.history(limit=8):
                    if (mess.author.id == 148706546308612096 or mess.author.id == 777949472507559976) and 'Make an unvault' in mess.content:
                        recentmessage = mess
                        nofake = False
                        break
                    else:
                        nofake = True
                if nofake:
                    await ctx.send('No fake unvault found', delete_after=3)
                else:
                    recentmessagelist = recentmessage.content.split('\n')
                    tempmessage = ''
                    doctoredmessage = ''
                    for x in recentmessage.content.split('\n'):
                        if 'Make' not in x:
                            tempmessage += x.lower() + ' '
                    for x in tempmessage.split(' prime'):
                        doctoredmessage += x
                    doctoredmessage = doctoredmessage[:-1]
                    if len(ctx.message.content) > 2:
                        if ctx.message.content[-2:] == ' j':
                            dupe = False
                    print(doctoredmessage)
                    goodframes, badframes, dupeframes = checkframesin(doctoredmessage)

                await ctx.message.delete(delay=3)

            elif 'prime' in ctx.message.content.lower():
                for x in ctx.message.content.lower().split(' prime'):
                    doctoredmessage += x
            
            elif 'random' in ctx.message.content.lower():
                noexcal = False
                try:
                    int(ctx.message.content.split(' ')[2])
                    randint = int(ctx.message.content.split(' ')[2])
                except:
                    randint = 2
                try:
                    if 'j' in ctx.message.content.split(' ')[2:]:
                        dupe = False
                except:
                    dupe = True
                if 'noexcal' in ctx.message.content.lower():
                    noexcal = True
                goodframes = buildrandom(randint, noexcal)

            else:
                tempmessage = ctx.message.content
                if ctx.message.content[-2:] == ' j':
                    dupe = False
                    tempmessage = tempmessage[:-2]
                elif 'junk' in ctx.message.content.lower():
                    dupe = False
                    tempmessage = tempmessage[:-5]
                elif ctx.message.content[-2:] == ' d':
                    dupe = True
                    tempmessage = tempmessage[:-2]
                elif 'dupl' in ctx.message.content.lower():
                    dupe = False
                    tempmessage = tempmessage[:-10]
                goodframes, badframes, dupeframes = checkframesin(tempmessage)

            try:
                messageauthor = ctx.message.author
            except:
                print('No author in original message')
            try:
                messageserver = ctx.message.guild.name
            except:
                print('No server in original message')

                ########################## HERE

            print(f"Building relics for: {(', '.join(goodframes)).title()}")

            finaloutmessage = ''
            goodframesstr = ''
            for x in goodframes:
                goodframesstr += x[0].upper() + x[1:].lower() + ', '
            goodframesstr = goodframesstr[:-2]

            if len(badframes) > 0 and len(dupeframes) > 0:
                await ctx.message.channel.send(f'Duplicate frames: {dupeframes}\nInvalid frames: {badframes}', delete_after=3)
            elif len(badframes) > 0 and len(dupeframes) == 0:
                await ctx.message.channel.send(f'Invalid frames: {badframes}', delete_after=3)
            elif len(badframes) == 0 and len(dupeframes) > 0:
                await ctx.message.channel.send(f'Duplicate frames: {dupeframes}', delete_after=3)

            validrelics = False

            if len(goodframes) == 0:
                await ctx.message.delete(delay=3)
                f  = open('generationlog.txt', 'a')
                f.writelines(str('[' + datetime.datetime.today().strftime('%m/%d/%y') + ' ' + datetime.datetime.now().strftime('%H:%M:%S')) + ']  Created by user ' + str(messageauthor) + ' in ' + str(messageserver) + ' ' + str(goodframes) + '  Duplicates: ' + str(dupe) + '\n')
                f.close()
            else:
                validrelics = None
                try:
                    validrelics = relicbuilderv2.takeinput(goodframes, messageauthor, messageserver, dupe)
                except:
                    pass
                infomessage = ''
                if not validrelics:
                    infomessage = 'Attempt at making '
                    if dupe == True:
                        infomessage += 'relics for: ' + goodframesstr + ' using duplicate parts FAILED. Please try again, and if that does not work, try mixing up the order.'
                    else:
                        infomessage += 'relics for: ' + goodframesstr + ' using junk parts FAILED. Please try again, and if that does not work, try mixing up the order.'
                elif dupe == True:
                    infomessage = 'Relics for: ' + goodframesstr + ' using duplicate parts'
                else:
                    infomessage = 'Relics for: ' + goodframesstr + ' using junk parts'
                if not validrelics:
                    await ctx.message.channel.send(infomessage)
                if validrelics:
                    await ctx.message.channel.send(infomessage, file=discord.File('relicout.json'))
                    if ctx.message.channel != self.client.get_channel(851980874971217971) and str(ctx.message.guild) != 'M E':
                        mychannel = self.client.get_channel(851980874971217971)
                        if type(ctx.message.guild) is not None and type(ctx.message.channel) is not None and type(ctx.message) is not None:
                            await mychannel.send(str(ctx.author) + ' in ' + str(ctx.message.guild) + '\n' +
                            'https://discordapp.com/channels/' + str(ctx.message.guild.id) + '/' + str(ctx.message.channel.id) + '/' + str(ctx.message.id))
                        else:
                            await mychannel.send(str(ctx.author) + ' in DMs')
                        await mychannel.send(file=discord.File('relicout.json'))

                f  = open('generationlog.txt', 'a')
                f.writelines(str('[' + datetime.datetime.today().strftime('%m/%d/%y') + ' ' + datetime.datetime.now().strftime('%H:%M:%S')) + ']  Created by user ' + str(messageauthor) + ' in ' + str(messageserver) + ' ' + str(goodframes) + '  Duplicates: ' + str(dupe) + '\n')
                f.close()
            
            if not validrelics:
                print('No relics generated')
                f = open('generationlog.txt', 'a', encoding='utf-8')
                f.writelines((str('[' + datetime.datetime.today().strftime('%m/%d/%y') + ' ' + datetime.datetime.now().strftime('%H:%M:%S')) + ']  Created by user ' + str(messageauthor) + ' in ' + str(messageserver) + ' [' + str(badframes) + ']  Duplicates: ' + str(dupe) + ' FAILED'))
                f.writelines('\n')
                f.close()

            await textchannel.delete_messages(messagestodelete)

async def setup(client):
    await client.add_cog(BuildRelics(client))
