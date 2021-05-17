import IreneUtility.Base
import dbl
import module
from IreneUtility.Utility import Utility
from IreneUtility.util import u_logger as log


ex: Utility = Utility(keys=module.keys.keys_obj, d_py_client=module.keys.keys_obj.client,
                      aiohttp_session=module.keys.keys_obj.client_session)


class Irene:
    """
    Startup Client for Irene.

    We are not subclassing an AutoShardedClient, but will rather define it directly in keys.
    """
    def __init__(self):
        # Set to True if running a test bot.
        ex.test_bot = True
        # Set to True if you need the db structure created.
        ex.create_db_structure = False

        # define the modules for reuse
        self.miscellaneous = module.Miscellaneous.Miscellaneous(ex)
        self.twitter = module.Twitter.Twitter(ex)
        self.currency = module.Currency.Currency(ex)
        self.blackjack = module.BlackJack.BlackJack(ex)
        self.youtube = module.Youtube.Youtube(ex)
        self.groupmembers = module.GroupMembers.GroupMembers(ex)
        self.archive = module.Archive.Archive(ex)
        self.moderator = module.Moderator.Moderator(ex)
        self.profile = module.Profile.Profile(ex)
        self.help = module.Help.Help(ex)
        self.logging = module.Logging.Logging(ex)
        self.music = module.Music.Music(ex)
        self.botmod = module.BotMod.BotMod(ex)
        self.events = module.events.Events(ex)
        self.lastfm = module.LastFM.LastFM(ex)
        self.interactions = module.Interactions.Interactions(ex)
        self.wolfram = module.Wolfram.Wolfram(ex)
        self.guessinggame = module.GuessingGame.GuessingGame(ex)
        self.customcommands = module.CustomCommands.CustomCommands(ex)
        self.biasgame = module.BiasGame.BiasGame(ex)
        self.weverse = module.Weverse.Weverse(ex)
        self.selfassignroles = module.SelfAssignRoles.SelfAssignRoles(ex)
        self.reminder = module.Reminder.Reminder(ex)
        self.twitch = module.Twitch.Twitch(ex)
        self.botowner = module.BotOwner.BotOwner(ex)
        # self.gacha = module.Gacha.Gacha()
        self.status = module.status.Status(ex)  # not a command cog

        self.cogs = [self.miscellaneous, self.twitter, self.currency, self.blackjack, self.youtube, self.groupmembers,
                     self.archive, self.moderator, self.profile, self.help, self.logging, self.music, self.botmod,
                     self.events, self.lastfm, self.interactions, self.wolfram, self.guessinggame, self.customcommands,
                     self.biasgame, self.weverse, self.selfassignroles, self.reminder, self.twitch,
                     self.botowner]

        # Modules/Cogs that contain 'ex' (Utility) and the 'conn' (DB connection).
        # AKA -> Classes that are have inherited IreneUtility.Base.Base()
        self.base_modules: [IreneUtility.Base.Base] = self.cogs + [self.status]

    def run(self):
        """Start the bot."""
        # should define the needed properties of Utility before anything else.
        ex.define_unique_properties(weverse=True, data_dog=True, twitter=True, db_connection=True,
                                    base_modules=self.base_modules, events=self.events)

        # start the connection to the bot
        if ex.test_bot:
            self.run_test_bot()
        else:
            self.run_live_bot()

    def run_live_bot(self):
        """Run Production Ver. of the the bot."""
        # set top.gg client
        module.keys.keys_obj.top_gg = dbl.DBLClient(ex.client, module.keys.keys_obj.top_gg_key, autopost=True)
        self.start_up()
        self.start_loops()
        ex.client.run(module.keys.keys_obj.client_token)

    def run_test_bot(self):
        """Run Test Ver. of the the bot."""
        self.start_up()
        # background loops are optional with test bot.
        self.start_loops(run_weverse=False)
        log.console("--TEST BOT--")
        ex.client.run(module.keys.keys_obj.test_client_token)

    def start_up(self):
        # Add all cogs
        self.add_cogs()
        # Add all listeners
        self.add_listeners()
        # Start logging to console and file
        # For INFO Logging
        log.info()
        # For Debugging
        # module.log.debug()

    def start_loops(self, run_weverse=True):
        """Start Loops (Optional)"""
        # Start checking for Weverse Updates
        if run_weverse:
            self.weverse.weverse_updates.start()
        # Check for Reminders
        self.reminder.reminder_loop.start()
        # Check if twitch channels go live and send the announcements to discord channels.
        self.twitch.twitch_updates.start()
        # Start Automatic Youtube Scrape Loop
        ex.cache.main_youtube_instance = module.Youtube.YoutubeLoop(ex)
        ex.cache.main_youtube_instance.loop_youtube_videos.start()
        # Start Status Change Loop
        self.status.change_bot_status_loop.start()
        # Start Voice Client Loop
        self.music.check_voice_clients.start()
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

    def add_listeners(self):
        """Add Listener Events."""
        module.keys.keys_obj.client.add_listener(self.groupmembers.idol_photo_on_message, 'on_message')
        module.keys.keys_obj.client.add_listener(self.archive.on_message, 'on_message')
        module.keys.keys_obj.client.add_listener(self.logging.on_message_log, 'on_message')
        module.keys.keys_obj.client.add_listener(self.logging.logging_on_message_edit, 'on_message_edit')
        module.keys.keys_obj.client.add_listener(self.logging.logging_on_message_delete, 'on_message_delete')
        module.keys.keys_obj.client.add_listener(self.miscellaneous.on_message_user_notifications, 'on_message')
        module.keys.keys_obj.client.add_listener(self.botmod.mod_mail_on_message, 'on_message')
        module.keys.keys_obj.client.add_listener(self.customcommands.process_custom_commands, 'on_message')
        module.keys.keys_obj.client.add_listener(self.profile.increase_profile_level, 'on_message')

    def add_cogs(self):
        """Add the cogs to the bot client."""
        for cog in self.cogs:
            ex.client.add_cog(cog)
            log.console(f"Loaded Module {cog.__class__.__name__}.")


if __name__ == '__main__':
    Irene().run()
