from . import helper
from typing import Literal
import disnake
from disnake.ext import commands, tasks


class RemindersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)

    # ==============
    # Slash Commands
    # ==============
    @commands.slash_command(name="reminders", description="Manage Reminders.")
    async def slash_reminders(self, inter):
        ...

    @slash_reminders.sub_command(name="add", description="Add a reminder.")
    async def slash_reminders_add(self, inter,
                                  reason: str,
                                  _in: commands.Range[1.0, 86400.0],
                                  period: str = commands.Param(autocomplete=helper.get_periods)):
        await helper.process_reminder_add(user_id=inter.author.id, reason=reason,
                                          _in=_in,
                                          period=period, inter=inter, allowed_mentions=self.allowed_mentions)

    @slash_reminders.sub_command(name="remove", description="Remove a reminder.")
    async def slash_reminders_remove(self, inter,
                                     choices: str = commands.Param(autocomplete=helper.auto_complete_get_reminders)):
        remind_id = int(choices.split(")")[0])
        await helper.process_reminder_remove(user_id=inter.author.id, remind_id=remind_id,
                                             inter=inter, allowed_mentions=self.allowed_mentions)

    @tasks.loop(seconds=45, reconnect=True)
    async def loop_reminders(self):
        """Loop for user reminders."""
        try:
            await helper.process_reminder_loop(self.bot)
        except Exception as e:
            self.bot.logger.error(f"Auto Reminder Loop Error -> {e}")


def setup(bot: commands.AutoShardedBot):
    reminders_cog = RemindersCog(bot)
    bot.add_cog(reminders_cog)
    reminders_cog.loop_reminders.start()

