import module
from Utility import resources as ex


class Irene:
    def __init__(self):
        # Set to True if running a test bot.
        ex.test_bot = False

    def run(self):
        """Start the bot."""
        # all active blackjack games are also deleted, current session stats refreshed.
        # cache is reset in the on_ready event.
        ex.set_db_connection.start()
        if ex.test_bot:
            self.run_test_bot()
        else:
            self.run_live_bot()

    def run_live_bot(self):
        self.start_up()
        self.start_loops()
        ex.client.run(module.keys.client_token)

    def run_test_bot(self):
        # background loops are not started in test bot.
        self.start_up()
        self.start_loops()
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
    def start_loops():
        # Start Automatic DC Loop
        module.DreamCatcher.DcApp().new_task4.start()
        # Start Automatic Youtube Scrape Loop
        module.Youtube.YoutubeLoop().new_task5.start()
        # Start Status Change Loop
        module.status.Status().change_bot_status_loop.start()
        # Start Voice Client Loop
        module.Music.Music().check_voice_clients.start()
        # Update Group Photo Count Cache Every 12 hours
        ex.update_cache.start()
        # after intents was pushed in place, d.py cache loaded a lot slower and patrons are not added properly.
        # therefore it must be looped instead.
        ex.update_patron_cache.start()
        # Send Packets to localhost:5123 to show Irene is alive. This is meant for auto restarting Irene
        # This feature is essential in case of any overload or crashes by external sources.
        # This also avoids having to manually restart Irene.
        ex.show_irene_alive.start()

    @staticmethod
    def add_listeners():
        module.keys.client.add_listener(module.GroupMembers.GroupMembers.on_message2, 'on_message')
        module.keys.client.add_listener(module.Archive.Archive.on_message, 'on_message')
        module.keys.client.add_listener(module.Logging.Logging.on_message_log, 'on_message')
        module.keys.client.add_listener(module.Logging.Logging.logging_on_message_edit, 'on_message_edit')
        module.keys.client.add_listener(module.Logging.Logging.logging_on_message_delete, 'on_message_delete')
        module.keys.client.add_listener(module.Miscellaneous.Miscellaneous.on_message_notifications, 'on_message')
        module.keys.client.add_listener(module.BotMod.BotMod.mod_on_message, 'on_message')

    @staticmethod
    def add_cogs():
        # Note that this can be heavily simplified by iterating over every cog but is like this for testing purposes.
        ex.client.add_cog(module.Miscellaneous.Miscellaneous())
        ex.client.add_cog(module.Twitter.Twitter())
        ex.client.add_cog(module.Currency.Currency())
        ex.client.add_cog(module.DreamCatcher.DreamCatcher())
        ex.client.add_cog(module.BlackJack.BlackJack())
        ex.client.add_cog(module.Cogs.Cogs())
        ex.client.add_cog(module.Youtube.Youtube())
        ex.client.add_cog(module.GroupMembers.GroupMembers())
        ex.client.add_cog(module.Archive.Archive())
        ex.client.add_cog(module.BotSites.BotSites())
        ex.client.add_cog(module.Moderator.Moderator())
        ex.client.add_cog(module.Profile.Profile())
        ex.client.add_cog(module.Help.Help())
        ex.client.add_cog(module.Logging.Logging())
        ex.client.add_cog(module.Music.Music())
        ex.client.add_cog(module.BotMod.BotMod())
        ex.client.add_cog(module.events.Events())
        ex.client.add_cog(module.Testing.Testing())
        ex.client.add_cog(module.LastFM.LastFM())
        ex.client.add_cog(module.Interactions.Interactions())
        ex.client.add_cog(module.Wolfram.Wolfram())
        ex.client.add_cog(module.cache.Cache())
        ex.client.add_cog(module.GuessingGame.GuessingGame())


if __name__ == '__main__':
    Irene().run()
