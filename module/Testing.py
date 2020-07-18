from discord.ext import commands
import module


class Testing(commands.Cog):
    def __init__(self):
        """New Instances of the tested classes"""
        self.archive = module.Archive.Archive()
        self.blackjack = module.BlackJack.BlackJack()
        self.botmod = module.BotMod.BotMod()
        self.currency = module.Currency.Currency()
        self.dreamcatcher = module.DreamCatcher.DreamCatcher()
        self.dcapp = module.DreamCatcher.DcApp()
        self.groupmembers = module.GroupMembers.GroupMembers()
        self.logging = module.Logging.Logging()
        self.misc = module.Miscellaneous.Miscellaneous()
        self.moderator = module.Moderator.Moderator()
        self.music = module.Music.Music()
        self.profile = module.Profile.Profile()
        self.twitter = module.Twitter.Twitter()
        self.youtube = module.Youtube.Youtube()

    @commands.command()
    @commands.is_owner()
    async def testcommands(self, ctx):
        """Tests all commands (Use this while in a voice channel)."""
        await self.test_archive(ctx)
        await self.test_blackjack(ctx)
        await self.test_botmod(ctx)
        await self.test_currency(ctx)
        await self.test_dreamcatcher(ctx)
        await self.test_dcapp(ctx)
        await self.test_groupmembers(ctx)
        await self.test_logging(ctx)
        await self.test_misc(ctx)
        await self.test_moderator(ctx)
        await self.test_music(ctx)
        await self.test_profile(ctx)
        # await self.test_twitter(ctx)
        # await self.test_youtube(ctx)

    async def test_archive(self, ctx):
        """Tests the commands in Archive."""
        try:
            await self.archive.addchannel(self.archive, ctx, "1TxpwUPTuBmeHNUCfc6yJU19-Xm2a0uWn", "TEST",1)
            await self.archive.listchannels(self.archive, ctx)
            # await self.archive.addhistory(self.archive, ctx)
            await self.archive.deletechannel(self.archive, ctx)
            await ctx.send(f"> **ARCHIVE WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("Archive Failure")

    async def test_blackjack(self, ctx):
        """Tests the commands in BlackJack"""
        try:
            await self.blackjack.addcards(self.blackjack, ctx)
            await self.blackjack.blackjack(self.blackjack, ctx, "0", "bot")
            # Join game will not be tested due to invalid 2nd player. Will use bot instead.
            await self.blackjack.hit(self.blackjack, ctx)
            await self.blackjack.stand(self.blackjack, ctx)
            await self.blackjack.rules(self.blackjack, ctx)
            await ctx.send(f"> **BLACKJACK WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("Blackjack Failure")

    async def test_botmod(self, ctx):
        """Tests the commands in BotMod"""
        try:
            interaction_url = "https://media2.giphy.com/media/uqSU9IEYEKAbS/giphy.gif?cid=ecf05e4762dbbdd4f605a6625c77725d2445dcc1b1c24280&rid=giphy.gif"
            await self.botmod.addinteraction(self.botmod, ctx, "slap", links=interaction_url)
            await self.botmod.deleteinteraction(self.botmod, ctx, url=interaction_url)
            # bot bans will not be tested.
            # add statuses will not be tested
            await self.botmod.getstatuses(self.botmod, ctx)
            # Idol configuration commands will not be tested.
            await ctx.send(f"> **BOTMOD WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("BotMod Failure")

    async def test_currency(self, ctx):
        """Tests the commands in Currency"""
        try:
            await self.currency.daily(self.currency, ctx)
            await self.currency.balance(self.currency, ctx)
            await self.currency.bet(self.currency, ctx, balance="0")
            await self.currency.leaderboard(self.currency, ctx)
            await self.currency.beg(self.currency, ctx)
            await self.currency.upgrade(self.currency, ctx, "rob")
            # rob/give will not be tested.
            await self.currency.rps(self.currency, ctx, "rock", "0")
            await ctx.send(f"> **CURRENCY WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("Currency Failure")

    async def test_dreamcatcher(self, ctx):
        """Tests the commands in DreamCatcher"""
        try:
            await self.dreamcatcher.dcstop(self.dreamcatcher, ctx)
            await self.dreamcatcher.dcstart(self.dreamcatcher, ctx)
            await self.dreamcatcher.dcstop(self.dreamcatcher, ctx)
            # download_all will not be tested.
            await self.dreamcatcher.latest(self.dreamcatcher, ctx)
            await self.dreamcatcher.updates(self.dreamcatcher, ctx)
            await self.dreamcatcher.updates(self.dreamcatcher, ctx, solution="stop")
            await ctx.send(f"> **DREAMCATCHER WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("DreamCatcher Failure")

    async def test_dcapp(self, ctx):
        """Tests the commands in DC APP"""
        try:
            await self.dcapp.check_dc_post(51593, test=True)  # Class is not a Cog, do not need to pass in self, IMAGE
            await self.dcapp.check_dc_post(51114, test=True)  # Class is not a Cog, do not need to pass in self, VIDEO
            await ctx.send(f"> **DCAPP WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("DC APP Failure")

    async def test_groupmembers(self, ctx):
        """Tests the commands in GroupMembers"""
        try:
            # any command with pages or reactions won't be tested (aliases, fullnames, members, groups, randomidol)
            await self.groupmembers.count(self.groupmembers, ctx, name="Irene")
            await self.groupmembers.countgroup(self.groupmembers, ctx, group_name="Red Velvet")
            await self.groupmembers.countleaderboard(self.groupmembers, ctx)
            await self.groupmembers.countmember(self.groupmembers, ctx, member="Irene")
            await self.groupmembers.sendimages(self.groupmembers, ctx)
            await self.groupmembers.sendimages(self.groupmembers, ctx)
            await self.groupmembers.stopimages(self.groupmembers, ctx)
            await self.groupmembers.stopimages(self.groupmembers, ctx)
            # getlinks, scandrive, sort, and tenor will not be tested
            await ctx.send(f"> **GROUPMEMBERS WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("GroupMembers Failure")

    async def test_logging(self, ctx):
        """Tests the commands in Logging"""
        try:
            await self.logging.startlogging(self.logging, ctx)
            await self.logging.sendall(self.logging, ctx)
            await self.logging.sendall(self.logging, ctx)
            await self.logging.logadd(self.logging, ctx)
            await self.logging.logremove(self.logging, ctx)
            await self.logging.stoplogging(self.logging, ctx)
            await ctx.send(f"> **LOGGING WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("Logging Failure")

    async def test_misc(self, ctx):
        """Tests the commands in Miscellaneous"""
        try:
            await self.misc._8ball(self.misc, ctx, question= "Is This Command Working?")
            await self.misc.botinfo(self.misc, ctx)
            # interactions will not be tested.
            await self.misc.checkprefix(self.misc, ctx)
            await self.misc.translate(self.misc, ctx, "en", "ko", message="hello")
            await self.misc.report(self.misc, ctx, issue= "Testing Report Command")
            await self.misc.suggest(self.misc, ctx, suggestion= "Testing Suggestion Command")
            await self.misc.nword(self.misc, ctx)
            # clear nword will not be tested.
            await self.misc.nwordleaderboard(self.misc, ctx)
            await self.misc.random(self.misc, ctx, 5, 10)
            await self.misc.flip(self.misc, ctx)
            await self.misc.urban(self.misc, ctx, "test", 1, 1)
            await self.misc.invite(self.misc, ctx)
            await self.misc.support(self.misc, ctx)
            # announce will not be tested
            await self.misc.send(self.misc, ctx, module.keys.dc_app_test_channel_id, new_message="Testing Send!")
            await self.misc.servercount(self.misc, ctx)
            await self.misc.serverinfo(self.misc, ctx)
            # servers will not be tested since it has pages/reactions
            await self.misc.say(self.misc, ctx, message="Test")
            await self.misc.speak(self.misc, ctx, message="Test")
            await self.misc.ping(self.misc, ctx)
            # kill will not be tested.
            await ctx.send(f"> **MISCELLANEOUS WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("MISCELLANEOUS Failure")

    async def test_moderator(self, ctx):
        """Tests the commands in Moderator"""
        try:
            emoji_url = "https://cdn.discordapp.com/emojis/585827739186102289.png?v=1"
            await self.moderator.addemoji(self.moderator, ctx, emoji_url, "test_emoji")
            #ban, unban, kick, setprefix, clear will not be tested.
            await self.moderator.tempchannel(self.moderator, ctx, 5)
            await self.moderator.tempchannel(self.moderator, ctx, -1)
            await ctx.send(f"> **MODERATOR WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("Moderator Failure")

    async def test_music(self, ctx):
        """Tests the commands in Music"""
        try:
            await self.music.play(self.music, ctx, url="Crab Rave")
            await self.music.volume(self.music, ctx, 15)
            await self.music.join(self.music, ctx)
            await self.music.pause(self.music, ctx)
            await self.music.resume(self.music, ctx)
            await self.music.shuffle(self.music, ctx)
            # queue will not be tested due to it having pages/reactions
            await self.music.stop(self.music, ctx)
            await ctx.send(f"> **MUSIC WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("Music Failure")

    async def test_profile(self, ctx):
        """Tests the commands in Profile"""
        try:
            await self.profile.profile(self.profile, ctx)
            await self.profile.avatar(self.profile, ctx)
            await ctx.send(f"> **PROFILE WAS TESTED SUCCESSFULLY**")
        except Exception as e:
            module.log.console(f"TESTING - {e}")
            await ctx.send("Profile Failure")

    async def test_twitter(self, ctx):
        """Tests the commands in Twitter"""
        await ctx.send(f"> **TWITTER WAS TESTED SUCCESSFULLY**")

    async def test_youtube(self, ctx):
        """Tests the commands in Youtube"""
        await ctx.send(f"> **YOUTUBE WAS TESTED SUCCESSFULLY**")
