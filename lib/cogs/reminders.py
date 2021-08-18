from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext import commands
from datetime import date, datetime
from datetime import timedelta

class Reminders(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def testdate(self, ctx):
        current_time = datetime.now()
        await ctx.send(current_time.isoformat())

    @command()
    async def testdateinput(self, ctx, *, date_str : str):
        try:
            inputted_time = datetime.strptime(date_str, '%Y/%m/%d')
            await ctx.send(inputted_time.isoformat())
        except:
            await ctx.send("Date inputted in incorrect format. Use format year/month/day (e.g., **2021/02/03**) for Feb 3, 2021.")

    @testdateinput.error
    async def testdateinput_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument)):
            await ctx.send("To use *testdateinput* command do: **testdateinput <date>** \n(e.g., testdateinput 2021/02/03)")

    @command(brief="Set a reminder", description="Set a reminder by indicating the date and at what time to receive your reminder notification")
    async def setreminder(self, ctx, date_str : str, time_str : str, * , description : str):
        time_arg = date_str + ' ' + time_str
        
        try:
            notify_time = datetime.strptime(time_arg, '%m/%d/%Y %I:%M%p')
        except:
            await ctx.send("Error: date/time format does not match. Use format: month/day/year hr:min(am/pm) \n(e.g., 05/25/2021 05:30am) for Dec 25, 2021 at 5:30am")
        
        if notify_time < datetime.now():
            await ctx.send("Error: You cannot set a reminder for a time in the past!")
            return

        self.bot.scheduler.add_job(self.bot.send_notification, 'date', run_date=notify_time, args=[ctx, f"Here's your reminder for **{description}**!"])

        if (notify_time.date() == datetime.now().date()):
            await ctx.send(f"You set a reminder for **{description}** for today at {notify_time.strftime('%I:%M %p')[1:]}")
        else:
            await ctx.send(f"You set a reminder for **{description}** for {notify_time.strftime('%a, %b %d, %Y')} at {notify_time.strftime('%I:%M %p')[1:]}")

    @setreminder.error
    async def setreminder_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument)):
            await ctx.send("To use setreminder command do: **setreminder <date> <time> <description>** \n(e.g., setreminder 5/25/2021 5:40am Take out the trash.)")

    @command(brief="Set reminder from now", description="Set a reminder by indicating how much time to wait until you get a reminder notification.")
    async def setreminderfromnow(self, ctx, time_str : str, * , description : str):

        try:
            [days, hrs, mins, secs] = time_str.split("/")
        except ValueError:
            await ctx.send("Error: time format is wrong. Use format: days/hrs/mins/secs \n(e.g., 0/5/0/1) for 5 hrs and 1 sec")

        notify_time = datetime.now() + timedelta(
            int(days), 
            int(secs), 
            minutes=int(mins), 
            hours=int(hrs)
        )

        if notify_time < datetime.now():
            await ctx.send("Error: You cannot set a reminder for a time in the past!")
            return

        self.bot.scheduler.add_job(self.bot.send_notification, 'date', run_date=notify_time, args=[ctx, f"Here's your reminder for **{description}**!"])

        if (notify_time.date() == datetime.now().date()):
            await ctx.send(f"You set a reminder for **{description}** for today at {notify_time.strftime('%I:%M:%S %p')[1:]}")
        else:
            await ctx.send(f"You set a reminder for **{description}** for {notify_time.strftime('%a, %b %d, %Y')} at {notify_time.strftime('%I:%M:%S %p')[1:]}")
        
    @setreminderfromnow.error
    async def setreminderfromnow_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument)):
            await ctx.send("To use setreminderfromnow command do: **setreminderfromnow <time_to_wait> <description>** \n(e.g., setreminderfromnow 5/0/0/0 Take out the trash.).")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reminders")
    
def setup(bot):
    bot.add_cog(Reminders(bot))