import module
import util
import util.objects
import dbl
from Utility import resources as ex


class Irene:
    def __init__(self):
        # Set to True if running a test bot.
        ex.test_bot = True

    def run(self):
        """Start the bot."""
        self.create_util_objects()  # create sub-classes for Utility
        ex.u_data_dog.initialize_data_dog()  # initialize the class for DataDog metrics
        # all active blackjack games are also deleted on db start, current session stats refreshed.
        # cache is reset in the on_ready event.
        ex.u_database.set_start_up_connection.start()
        if ex.test_bot:
            self.run_test_bot()
        else:
            self.run_live_bot()

    def run_live_bot(self):
        """Run Production Ver. of the the bot."""
        module.keys.top_gg = dbl.DBLClient(ex.client, module.keys.top_gg_key, autopost=True)  # set top.gg client
        self.start_up()
        self.start_loops()
        ex.client.run(module.keys.client_token)

    def run_test_bot(self):
        """Run Test Ver. of the the bot."""
        self.start_up()
        # background loops are optional with test bot.
        self.start_loops(run_weverse=False)
        module.log.console("--TEST BOT--")
        ex.client.run(module.keys.test_client_token)

    def start_up(self):
        # Add all cogs
        self.add_cogs()
        # Add all listeners
        self.add_listeners()
        # Start logging to console and file
        # For INFO Logging
        module.log.info()
        # For Debugging
        # module.log.debug()

    @staticmethod
    def start_loops(run_weverse=True):
        """Start Loops (Optional)"""
        # Start checking for Weverse Updates
        if run_weverse:
            module.Weverse.Weverse().weverse_updates.start()
        # Check for Reminders
        module.Reminder.Reminder().reminder_loop.start()
        # Check if twitch channels go live and send the announcements to discord channels.
        module.Twitch.Twitch().twitch_updates.start()
        # Start Automatic Youtube Scrape Loop
        ex.cache.main_youtube_instance = module.Youtube.YoutubeLoop()
        ex.cache.main_youtube_instance.loop_youtube_videos.start()
        # Start Status Change Loop
        module.status.Status().change_bot_status_loop.start()
        # Start Voice Client Loop
        module.Music.Music().check_voice_clients.start()
        # Update Cache Every 12 hours
        ex.u_cache.update_cache.start()
        # Start a loop that sends cache information to DataDog.
        ex.u_cache.send_cache_data_to_data_dog.start()
        # after intents was pushed in place, d.py cache loaded a lot slower and patrons are not added properly.
        # therefore patron cache must be looped instead.
        ex.u_cache.update_patron_and_guild_cache.start()
        # Send Packets to localhost:5123 to show Irene is alive. This is meant for auto restarting Irene
        # This feature is essential in case of any overload or crashes by external sources.
        # This also avoids having to manually restart Irene.
        ex.u_database.show_irene_alive.start()

    @staticmethod
    def add_listeners():
        """Add Listener Events."""
        module.keys.client.add_listener(module.GroupMembers.GroupMembers.on_message2, 'on_message')
        module.keys.client.add_listener(module.Archive.Archive.on_message, 'on_message')
        module.keys.client.add_listener(module.Logging.Logging.on_message_log, 'on_message')
        module.keys.client.add_listener(module.Logging.Logging.logging_on_message_edit, 'on_message_edit')
        module.keys.client.add_listener(module.Logging.Logging.logging_on_message_delete, 'on_message_delete')
        module.keys.client.add_listener(module.Miscellaneous.Miscellaneous.on_message_user_notifications, 'on_message')
        module.keys.client.add_listener(module.BotMod.BotMod.mod_mail_on_message, 'on_message')
        module.keys.client.add_listener(module.CustomCommands.CustomCommands.process_custom_commands, 'on_message')

    @staticmethod
    def add_cogs():
        """Add the cogs to the bot client."""
        # Note that this can be heavily simplified by iterating over every cog but is like this for testing purposes.
        ex.client.add_cog(module.Miscellaneous.Miscellaneous())
        ex.client.add_cog(module.Twitter.Twitter())
        ex.client.add_cog(module.Currency.Currency())
        ex.client.add_cog(module.BlackJack.BlackJack())
        ex.client.add_cog(module.Youtube.Youtube())
        ex.client.add_cog(module.GroupMembers.GroupMembers())
        ex.client.add_cog(module.Archive.Archive())
        ex.client.add_cog(module.Moderator.Moderator())
        ex.client.add_cog(module.Profile.Profile())
        ex.client.add_cog(module.Help.Help())
        ex.client.add_cog(module.Logging.Logging())
        ex.client.add_cog(module.Music.Music())
        ex.client.add_cog(module.BotMod.BotMod())
        ex.client.add_cog(module.events.Events())
        ex.client.add_cog(module.LastFM.LastFM())
        ex.client.add_cog(module.Interactions.Interactions())
        ex.client.add_cog(module.Wolfram.Wolfram())
        ex.client.add_cog(module.cache.Cache())
        ex.client.add_cog(module.GuessingGame.GuessingGame())
        ex.client.add_cog(module.CustomCommands.CustomCommands())
        ex.client.add_cog(module.BiasGame.BiasGame())
        ex.client.add_cog(module.Weverse.Weverse())
        ex.client.add_cog(module.SelfAssignRoles.SelfAssignRoles())
        ex.client.add_cog(module.Reminder.Reminder())
        ex.client.add_cog(module.Twitch.Twitch())
        # ex.client.add_cog(module.Gacha.Gacha())

    @staticmethod
    def create_util_objects():
        """Create SubClass Objects to attach to Utility object for easier management and sharing between siblings.
        The Utility object serves as a client for Irene and is managed by the following objects"""
        ex.u_database = util.database.DataBase()
        ex.u_cache = util.cache.Cache()
        ex.u_miscellaneous = util.miscellaneous.Miscellaneous()
        ex.u_blackjack = util.blackjack.BlackJack()
        ex.u_group_members = util.groupmembers.GroupMembers()
        ex.u_logging = util.logging.Logging()
        ex.u_twitter = util.twitter.Twitter()
        ex.u_last_fm = util.lastfm.LastFM()
        ex.u_patreon = util.patreon.Patreon()
        ex.u_moderator = util.moderator.Moderator()
        ex.u_custom_commands = util.customcommands.CustomCommands()
        ex.u_bias_game = util.biasgame.BiasGame()
        ex.u_data_dog = util.datadog.DataDog()
        ex.u_weverse = util.weverse.Weverse()
        ex.u_self_assign_roles = util.selfassignroles.SelfAssignRoles()
        ex.u_reminder = util.reminder.Reminder()
        ex.u_guessinggame = util.guessinggame.GuessingGame()
        ex.u_twitch = util.twitch.Twitch()
        # ex.u_gacha = util.gacha.Gacha()
        
        ex.u_objects = util.objects  # util directory that has the objects directly imported


if __name__ == '__main__':
    Irene().run()
