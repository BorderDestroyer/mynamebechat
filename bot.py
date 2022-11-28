from twitchio.ext import commands
from twitchio.ext import routines
import twitchio
import sqlite3
import Secrets
import datetime
import twitchio.websocket
import threading

con = sqlite3.connect("mynamebechat.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS bathroom(name text, date text)")

connectedChannels = []
channelClass = []
userIDs = []
OnlineChannels = []

quirkyMessages = []

testing = True
class Bot(commands.Bot):
    def __init__(self):
        if not testing:
            super().__init__(token=Secrets.access_token, prefix=["?", "!", "."], initial_channels=connectedChannels)
        else:
            super().__init__(token=Secrets.access_token_test, prefix=["?", "!", "."], initial_channels=connectedChannels)
            
    async def event_ready(self):
        print("~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Logged in as | {self.nick}")        
        print("~~~~~~~~~~~~~~~~~~~~~~")
        
        user = await self.fetch_users(names=connectedChannels)
        for i in range(len(connectedChannels)):
            userIDs.append(user[i].id)
            channelClass.append(user[i].channel)
            
        print(channelClass)
        
        print(userIDs)
        print("~~~~~~~~~~~~~~~~~~~~~~")
                
    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(F"Hello {ctx.author.mention}!")

    @commands.command()
    async def cactus(self, ctx: commands.Context):
        cur.execute("""SELECT name
                    FROM bathroom
                    WHERE name=?""",
                    [ctx.author.name,])
        results = cur.fetchone()
        
        if results:
            cur.execute("""SELECT date
                        FROM bathroom
                        WHERE name=?""",
                        [ctx.author.name,])
            date = cur.fetchone()[0]
            
            await ctx.send(f"{ctx.author.mention} You have been in the bathroom since {date}!")
        else:
            today = datetime.date.today()
            day = today.strftime("%m/%d/%y")
            
            cur.execute(f"INSERT INTO bathroom VALUES ('{ctx.author.name}', '{day}')")
            
            await ctx.send(f"{ctx.author.mention} You have joined the bathroom!")
            con.commit()
    
    @commands.command()
    async def bathroom(self, ctx: commands.Context):
        cur.execute("""SELECT *
                    FROM bathroom""")
        result = cur.fetchall()
        
        amount = len(result)
        
        await ctx.send(f"{ctx.author.mention} There are currently {amount} people in the bathroom!")
    
    async def event_message(self, message):
        if message.echo:
            return
        
        print(message.content)
        
        await self.handle_commands(message)
    
    @routines.routine(minutes=2, wait_first=True)
    async def checkChannels():
        print("Checking For Live Channels")
        streamsInfo = []
        temp = []
        streamsInfo = await Bot.fetch_streams(self=Bot(), user_ids=userIDs)
        
        print(streamsInfo)
        
        for i in range(len(streamsInfo)):
            if streamsInfo[i].user.id in userIDs:
                temp.append(streamsInfo[i].user.id)   
                if streamsInfo[i].user.id not in OnlineChannels:
                    OnlineChannels.append(streamsInfo[i].user.id)
                    
                    placeholder = userIDs.index(streamsInfo[i].user.id)           
                    await channelClass[placeholder].send(f"Good evening {connectedChannels[placeholder]}! The chat bot created by BorderDestroyer has connected to your channel! Have a good stream!")
        
        print(OnlineChannels)
        print(temp)
        
        for i in range(len(OnlineChannels)):
            if OnlineChannels[i] not in temp:
                OnlineChannels.remove(OnlineChannels[i])
                
        print("~~~~~~~~~~~~~~~~~~~~~~")            
    checkChannels.start()
    
    @routines.routine(minutes=1, wait_first=True)
    async def joinNewChannels():
        print("Checking For Added Channels")
        checkingChannels = file.readlines()
        
        for i in range(len(checkingChannels)):
            if checkingChannels[i].strip() not in connectedChannels:
                connectedChannels.append(checkingChannels[i].strip())
                temp = [checkingChannels[i]]
                await bot.join_channels(channels=temp)
                print("Added Connection To | " + checkingChannels[i])
                print("~~~~~~~~~~~~~~~~~~~~~~")
                
                channelInfo = await bot.fetch_channel(broadcaster=checkingChannels[i])
                channel = channelInfo.user.channel
                channelClass.append(channel)
                
        print("Currently Connected To - ")
        for i in range(len(connectedChannels)):
            print(connectedChannels[i])
        print("Classes - ")
        for i in range(len(connectedChannels)):
            print(channelClass[i])
        print("~~~~~~~~~~~~~~~~~~~~~~")
    joinNewChannels.start()

file = open("channels.txt")
temp = file.readlines()
for i in range(len(temp)):
    connectedChannels.append(temp[i].strip())

print(connectedChannels)

bot = Bot()
bot.run()