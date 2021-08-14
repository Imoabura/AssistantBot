from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext import commands
from datetime import datetime
from datetime import timedelta

class Settings(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=["hi"])
    async def say_hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")

    @command(brief="Bot Info", description="Bot Description and Function Overview")
    async def info(self, ctx):
        await ctx.send("```Description:\n  Assistant Bot is a Discord Bot that is used to keep track of tasks, task deadlines, and personal reminders!\n  " + 
            "Create, edit, and remove Tasks and personal Reminders!\n  " + 
            "Set Task deadlines and Reminder times to automatically receive notifications from Assistant Bot!\n  " + 
            "Assistant Bot is a personal, hobby project of Imoabura#4837.```")

    @command(brief="Rename Notif Channel", description="Renames the channel Assistant Bot uses for notifications. (Limit 1 rename per 5 minutes)")
    async def renamebotchannel(self, ctx, *, new_channel_name : str):
        current_time = datetime.now()
        
        if (self.bot.rename_time != None):
            delay = self.bot.get_rename_time_delay()
            if (delay[0] < 5):
                await ctx.send("**Error:** Limited to 1 rename per 5 minutes.")
                return
        
        if (self.bot.notif_channel.name == new_channel_name):
            await ctx.send("**Error:** New name is the same as the current name.")
            return
        
        await self.bot.notif_channel.edit(name=new_channel_name)
        self.bot.rename_time = current_time

        if (self.bot.notif_channel.name != new_channel_name):
            await ctx.send("**Error** Rename failed.")
        else:
            await ctx.send("Notification Channel renamed!")

    @renamebotchannel.error
    async def renamebotchannel_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument)):
            await ctx.send("To use the renamebotchannel command do: **!renamebotchannel <new_name>**")

    @command(brief="Set DM Setting", description="Choose 'T' to receive notifications through DMs or 'F' to receive notifications through the notification channel.")
    async def dmnotifs(self, ctx, *, activate : str):
        if (activate.upper() == "ON" or activate.upper() == "T" or activate.upper() == "TRUE" or activate == "1"):
            self.bot.use_dms = True
        elif (activate.upper() == "OFF" or activate.upper() == "F" or activate.upper() == "FALSE" or activate == "0"):
            self.bot.use_dms = False
        else:
            await ctx.send(f'**Error: {activate}** is not valid.\nUse (**T**, **TRUE**, **ON**, or **1**) for True.\nUse (**F**, **FALSE**, **OFF**, or **0**) for False.')
            return

        bool_text = self.bot.on_off_str(self.bot.use_dms)
        await ctx.send(f'DM Notifs have been turned **{bool_text}**')

    @dmnotifs.error
    async def dmnotifs_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument)):
            await ctx.send("To use the dmnotifs command do: **!dmnotifs <True or False>**")

    @command(brief="Show Settings Breakdown", description="Shows whether User has use_dms turned ON/OFF.")
    async def mysettings(self, ctx):
        bool_text = self.bot.on_off_str(self.bot.use_dms)
        await ctx.send(f'You have DM Notifs turned **{bool_text}**')

    @command(brief="Notification Test", description="Send a Test Notification Message to yourself.")
    async def test(self, ctx):
        await self.bot.send_notification(ctx, "Notification Test.")

    @command()
    async def testdate(self, ctx):
        current_time = datetime.now()
        await ctx.send(current_time.isoformat())

    @command()
    async def setreminderfromnow(self, ctx, *args):
        notif_name = args[0]
        days = int(args[1])
        hours = int(args[2])
        minutes = int(args[3])
        seconds = int(args[4])
        notify_time = datetime.now() + timedelta(days,seconds,minutes=minutes,hours=hours)
        self.bot.scheduler.add_job(self.bot.send_notification, 'date', run_date=notify_time, args=[ctx, f"Reminder for **{notif_name}**!"])
        await ctx.send(f"You set a reminder for **{notif_name}** for {notify_time.isoformat()}")

    @command()
    async def alljobs(self, ctx):
        for job in self.bot.scheduler.get_jobs():
            await ctx.send(f"id:{job.id}, name:{job.name}, trigger:{job.trigger}, sched_time:{job.next_run_time.isoformat()}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("settings")

    # @Cog.listener()
    # async def on_message(self):
    #     await self.bot.notif_channel.send("Ohh! A Message!")

def setup(bot):
    bot.add_cog(Settings(bot))
