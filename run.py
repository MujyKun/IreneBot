from typing import List
import dbl
import discord.ext.commands
from discord.ext.tasks import Loop
import module
from IreneUtility.Utility import Utility
from IreneUtility.util import u_logger as log
import importlib  # used for reloading packages or modules.
from sys import modules as system_module  # used for getting references to modules.

ex: Utility = Utility(keys=module.keys.keys_obj, d_py_client=module.keys.keys_obj.client,
                      aiohttp_session=module.keys.keys_obj.client_session)


class Irene:
    """
    Startup Client for Irene.

    We are not subclassing an AutoShardedClient, but will rather define it directly in the keys module.
    """

    def __init__(self):
        self.define_start_up_criteria(test_bot=True, dev_mode=True, upload_from_host=False, reset_cache=False)
        # Whether to Run Twitter
        self.run_twitter = not ex.test_bot

        self.cog_names = ["miscellaneous", "twitter", "currency", "blackjack", "youtube", "groupmembers",
                          "moderator", "profile", "help", "logging", "botmod", "events", "lastfm", "interactions",
                          "wolfram", "guessinggame", "customcommands", "biasgame", "selfassignroles",
                          "reminder", "twitch", "botowner", "unscramble", "vlive", "music", "blocking_monitor",
                          "data_mod",  "status"]

        # define the cogs & modules for reuse
        self.cogs = {}
        self.set_cogs()

        self.loops: List[Loop] = []  # Contains list of loops that may be started/stopped

    def run(self):
        """Start the bot."""
        # should define the needed properties of Utility before anything else.
        self.define_utility_properties()

        # start the connection to the bot
        if ex.test_bot:
            self.run_test_bot()
        else:
            self.run_live_bot()

    @staticmethod
    def get_cog_classes() -> dict:
        """Will get classes for the modules/cogs for fresh imports. This is very important for hot-reloading."""
        import module  # needs to be reimported for future hot-reloading.
        return {
            "miscellaneous": module.Miscellaneous.Miscellaneous,
            "twitter": module.Twitter.Twitter,
            "currency": module.Currency.Currency,
            "blackjack": module.BlackJack.BlackJack,
            "youtube": module.Youtube.Youtube,
            "groupmembers": module.GroupMembers.GroupMembers,
            "moderator": module.Moderator.Moderator,
            "profile": module.Profile.Profile,
            "help": module.Help.Help,
            "logging": module.Logging.Logging,
            "botmod": module.BotMod.BotMod,
            "events": module.events.Events,
            "lastfm": module.LastFM.LastFM,
            "interactions": module.Interactions.Interactions,
            "wolfram": module.Wolfram.Wolfram,
            "guessinggame": module.GuessingGame.GuessingGame,
            "customcommands": module.CustomCommands.CustomCommands,
            "biasgame": module.BiasGame.BiasGame,
            "selfassignroles": module.SelfAssignRoles.SelfAssignRoles,
            "reminder": module.Reminder.Reminder,
            "twitch": module.Twitch.Twitch,
            "botowner": module.BotOwner.BotOwner,
            "unscramble": module.UnScramble.UnScramble,
            "vlive": module.Vlive.Vlive,
            "music": module.Music.Music,
            "blockingmonitor": module.blockingmonitor.BlockingMonitor,
            "datamod": module.DataMod.DataMod,
            "status": module.status.Status
            # "gacha":  module.Gacha.Gacha
        }

    def set_cogs(self, specific_cog_name=None):
        """Set Cogs

        :param specific_cog_name: Cog Name to specifically update.
        """
        for key, value in self.get_cog_classes().items():
            if specific_cog_name and key != specific_cog_name:
                continue

            if key == "botowner":
                self.cogs[key] = value(ex, self)
            else:
                self.cogs[key] = value(ex)

        if specific_cog_name:
            return self.cogs.get(specific_cog_name)

    def define_utility_properties(self):
        """Defines essential attributes and properties for the Utility lib."""
        ex.define_unique_properties(data_dog=True, twitter=True, db_connection=True, events=self.cogs.get("events"))

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
        self.start_loops()
        log.console("--TEST BOT--")
        ex.client.run(module.keys.keys_obj.test_client_token)

    @staticmethod
    def define_start_up_criteria(test_bot=False, dev_mode=False, upload_from_host=True, reset_cache=False):
        """Settings for running the bot."""
        # Set to True if running a test bot (Not equivalent to dev mode).
        ex.test_bot = test_bot
        # Set to True if not on the production server (useful if ex.test_bot is False).
        # This was initially created to not flood datadog with incorrect input while ex.test_bot was False
        ex.dev_mode = dev_mode
        # Set to True if you want the bot to upload its images from host rather than using url.
        ex.upload_from_host = upload_from_host
        # Set to False if you do not want the cache to reset itself every 12 hours.
        ex.reset_cache = reset_cache

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

    def reload(self):
        """Will hot reload all of IreneBot, IreneUtility, and any other self-made packages."""
        # we want to reload the cogs first because we want to make sure the loops are updated before creating new ones
        # in reload_utility.
        self.stop_loops()  # stop all loops.

        for cog in self.cogs.values():
            print(cog)
            self.reload_cog(cog)

        self.reload_utility()

    def reload_utility(self):
        """Reloads the utility package for the bot."""

        # First lets save the data of
        import IreneUtility
        importlib.reload(IreneUtility)

        self.stop_loops(safe_cancel=False)  # we need all loops to stop.

        global ex
        ex = Utility(keys=module.keys.keys_obj, d_py_client=module.keys.keys_obj.client,
                     aiohttp_session=module.keys.keys_obj.client_session)
        self.define_utility_properties()

        # we only need to replace the Utility object in every Base object that uses it.
        for cog in self.cogs.values():
            cog.ex = ex

        # cache will be reset when starting loops.
        self.start_loops()  # we can start loops again.

    def reload_cogs(self):
        """Reloads all cogs."""
        for cog in self.cogs.values():
            self.reload_cog(cog)

    def reload_cog(self, cog: discord.ext.commands.Cog):
        """Reload a cog."""
        # The reason we can use __module__ to extract the exact dot path in this case is
        # because the cogs/modules were created in this class.
        file_dot_path = cog.__module__
        module_to_reload = system_module[file_dot_path]  # sys.modules
        importlib.reload(module_to_reload)

        # d.py's concept of extensions do not fit what we are looking for in this bot in regards to
        # having a third party utility package, so we will reload it ourselves.
        # this is also why none of our modules have setup functions.
        ex.client.remove_cog(cog.qualified_name)

        new_cog = self.set_cogs(cog.qualified_name.lower())
        try:
            ex.client.add_cog(new_cog)
        except Exception as e:
            log.console(f"Failed to add Cog {cog} (Exception) - {e}", self.reload_cog)

    def start_loops(self):
        """Start Loops (Optional)"""
        self.loops = [ex.u_database.show_irene_alive, ex.u_cache.update_patron_and_guild_cache,
                      ex.u_cache.send_cache_data_to_data_dog, ex.u_cache.update_cache,
                      self.cogs["vlive"].vlive_notification_updates,
                      self.cogs["groupmembers"].send_idol_photo_loop, self.cogs["status"].change_bot_status_loop,
                      self.cogs["twitch"].twitch_updates, self.cogs["reminder"].reminder_loop,
                      self.cogs["twitter"].twitter_notification_updates]
        if self.run_twitter:
            self.loops.append(self.cogs["twitter"].send_photos_to_twitter)
        ex.cache.main_youtube_instance = module.Youtube.YoutubeLoop(ex)
        self.loops.append(ex.cache.main_youtube_instance.loop_youtube_videos)

        for loop in self.loops:
            loop.start()

    def stop_loops(self, safe_cancel=False):
        """Stop all loops."""
        for loop in self.loops:
            loop.cancel() if not safe_cancel else loop.stop()

    def add_listeners(self):
        """Add Listener Events."""
        on_message_events = [self.cogs["groupmembers"].idol_photo_on_message,
                             self.cogs["logging"].on_message_log,
                             self.cogs["miscellaneous"].on_message_user_notifications,
                             self.cogs["botmod"].mod_mail_on_message,
                             self.cogs["customcommands"].process_custom_commands,
                             self.cogs["profile"].increase_profile_level]
        on_edit_events = [self.cogs["logging"].logging_on_message_edit]
        on_delete_events = [self.cogs["logging"].logging_on_message_delete]

        for method in on_message_events:
            module.keys.keys_obj.client.add_listener(method, 'on_message')
        for method in on_edit_events:
            module.keys.keys_obj.client.add_listener(method, 'on_message_edit')
        for method in on_delete_events:
            module.keys.keys_obj.client.add_listener(method, 'on_message_delete')

    def add_cogs(self):
        """Add the cogs to the bot client."""
        for cog in self.cogs.values():
            ex.client.add_cog(cog)
            log.console(f"Loaded Cog {cog.__class__.__name__}.")


if __name__ == '__main__':
    Irene().run()
