from . import helper
from .. import helper as main_helper
import disnake
from disnake.ext import commands, tasks
from disnake import ApplicationCommandInteraction as AppCmdInter
from keys import get_keys
from IreneAPIWrapper.models import (
    Group,
    Person,
    Affiliation,
    EightBallResponse,
    User,
    Interaction,
    InteractionType,
    AutoMedia,
    TwitchAccount,
    TwitterAccount,
    Reminder,
    Notification,
    ReactionRoleMessage,
)


class BotOwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_mentions = disnake.AllowedMentions(everyone=False, roles=False)
        self._loop_running = False

    async def cog_check(self, ctx: commands.Context) -> bool:
        """A local cog check to confirm the right owner."""
        return await ctx.bot.is_owner(ctx.author)

    async def cog_slash_command_check(self, inter: AppCmdInter):
        """A local cog check to confirm the right owner."""
        if not await inter.bot.is_owner(inter.author):
            raise commands.NotOwner
        return True

    @commands.group(name="8ballresponse", description="Modify 8ball responses.")
    async def regular_eight_ball_response(self, ctx: commands.Context):
        ...

    @regular_eight_ball_response.command(
        name="add", description="Add an 8ball response."
    )
    async def regular_add_eight_ball_response(
        self, ctx: commands.Context, *, response: str
    ):
        await helper.process_add_eight_ball_response(
            response=response,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_eight_ball_response.command(
        name="list", description="List all 8ball responses."
    )
    async def regular_list_eight_ball_response(self, ctx: commands.Context):
        await helper.process_list_eight_ball_responses(
            user_id=ctx.author.id, ctx=ctx, allowed_mentions=self.allowed_mentions
        )

    @regular_eight_ball_response.command(
        name="delete", description="Delete an 8ball response."
    )
    async def regular_delete_eight_ball_response(
        self, ctx: commands.Context, response_id: int
    ):
        await helper.process_delete_eight_ball_response(
            response_id=response_id,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.group(
        name="interaction",
        description="Interaction commands",
        extras={"permissions": "Bot Owner"},
    )
    async def regular_interaction(self, ctx: commands.Context):
        ...

    @regular_interaction.command(name="add", description="Add an interaction")
    async def regular_interaction_add(
        self, ctx: commands.Context, type_name: str, url: str
    ):
        await helper.process_interaction_add(
            type_name=type_name,
            url=url,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_interaction.command(name="delete", description="Delete an interaction")
    async def regular_interaction_delete(
        self, ctx: commands.Context, type_name: str, url: str
    ):
        await helper.process_interaction_add(
            type_name=type_name,
            url=url,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_interaction.group(name="type")
    async def regular_interaction_type(self, ctx: commands.Context):
        ...

    @regular_interaction_type.command(name="add", description="Add an interaction type")
    async def regular_interaction_add(self, ctx: commands.Context, type_name: str):
        await helper.process_interaction_type_add(
            type_name=type_name,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    @regular_interaction_type.command(
        name="delete", description="Delete an interaction type"
    )
    async def regular_interaction_delete(self, ctx: commands.Context, type_name):
        await helper.process_interaction_type_delete(
            type_name=type_name,
            user_id=ctx.author.id,
            ctx=ctx,
            allowed_mentions=self.allowed_mentions,
        )

    ################
    # SLASH COMMANDS
    ################

    @commands.slash_command(
        name="8ballresponse",
        description="Modify 8ball responses.",
        guild_ids=get_keys().bot_owner_only_servers,
        extras={"permissions": "Bot Owner"},
    )
    async def eight_ball_response(self, inter: AppCmdInter):
        ...

    @eight_ball_response.sub_command(
        name="add",
        description="Add an 8ball response.",
        extras={"permissions": "Bot Owner", "syntax": "/8ballresponse add (response)"},
    )
    async def add_eight_ball_response(
        self,
        inter: AppCmdInter,
        response: str = commands.Param("8ball Response to add."),
    ):
        await helper.process_add_eight_ball_response(
            response=response,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @eight_ball_response.sub_command(
        name="list",
        description="List all 8ball responses.",
        extras={"permissions": "Bot Owner", "syntax": "/8ballresponse list"},
    )
    async def list_eight_ball_response(self, inter: AppCmdInter):
        await helper.process_list_eight_ball_responses(
            user_id=inter.author.id, inter=inter, allowed_mentions=self.allowed_mentions
        )

    @eight_ball_response.sub_command(
        name="delete",
        description="Delete an 8ball response.",
        extras={
            "permissions": "Bot Owner",
            "syntax": "/8ballresponse delete (response id)",
        },
    )
    async def delete_eight_ball_response(
        self,
        inter: AppCmdInter,
        response_id: int = commands.Param("ID of 8ball response."),
    ):
        await helper.process_delete_eight_ball_response(
            response_id=response_id,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @commands.slash_command(
        name="interaction",
        description="Interaction Commands",
        guild_ids=get_keys().bot_owner_only_servers,
        extras={"permissions": "Bot Owner"},
    )
    async def interaction(self, inter: AppCmdInter):
        ...

    @interaction.sub_command(
        name="add",
        description="Add an interaction",
        extras={
            "permissions": "Bot Owner",
            "syntax": "/interaction add (url) (type name)",
        },
    )
    async def interaction_add(
        self,
        inter: AppCmdInter,
        url: str,
        type_name: str = commands.Param(
            autocomplete=helper.auto_complete_interaction_types
        ),
    ):
        await helper.process_interaction_add(
            type_name=type_name,
            url=url,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @interaction.sub_command(
        name="delete",
        description="Delete an interaction",
        extras={
            "permissions": "Bot Owner",
            "syntax": "/interaction delete (url) (type name)",
        },
    )
    async def interaction_delete(
        self,
        inter: AppCmdInter,
        url: str,
        type_name: str = commands.Param(
            autocomplete=helper.auto_complete_interaction_types
        ),
    ):
        await helper.process_interaction_add(
            type_name=type_name,
            url=url,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @interaction.sub_command_group(
        name="type",
        extras={
            "permissions": "Bot Owner",
            "notes": "This is a sub-command group.",
            "syntax": "/interaction type (add/delete) (type name)",
            "description": "Modify Interaction Types",
        },
    )
    async def interaction_type(self, inter: AppCmdInter):
        ...

    @interaction_type.sub_command(
        name="add",
        description="Add an interaction type",
        extras={
            "permissions": "Bot Owner",
            "syntax": "/interaction type add (type name)",
        },
    )
    async def interaction_type_add(self, inter: AppCmdInter, type_name):
        await helper.process_interaction_type_add(
            type_name=type_name,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @interaction_type.sub_command(
        name="delete",
        description="Delete an interaction type",
        extras={
            "permissions": "Bot Owner",
            "syntax": "/interaction type delete (type name)",
        },
    )
    async def interaction_type_delete(
        self,
        inter: AppCmdInter,
        type_name: str = commands.Param(
            autocomplete=helper.auto_complete_interaction_types
        ),
    ):
        await helper.process_interaction_type_delete(
            type_name=type_name,
            user_id=inter.author.id,
            inter=inter,
            allowed_mentions=self.allowed_mentions,
        )

    @tasks.loop(minutes=1, reconnect=True)
    async def stats_updates(self):
        """
        Send updates to the API regarding bot stats.
        """
        try:
            if not self.bot.api.connected or self._loop_running:
                return

            self._loop_running = True
            tracker = await main_helper.get_tracker()

            """
            TODO: (when a more suitable approach is given)
            -) GuessingGame / GroupGuessingGame
                -> Users with GG Filter enabled.
                -> Users with GGG Filter enabled.
            -> Number of Patrons
            -> Number of Super Patrons
            -> Users with API keys
            -> # of Guild Custom Prefixes

            """

            """
            Track:
                -) BotOwner
                    -> Wolfram Requests (per day?)
                    -> # Bot API Calls
                    -> # IreneBot Number of Errors
                    -> # IreneBot Number of Errors to API
            """
            from util import botinfo

            active_games = botinfo.get_count_active_games()
            inactive_games = botinfo.get_count_unfinished_games()
            total_games = botinfo.get_count_total_games()

            current_memory_usage, peak_memory_usage = await main_helper.get_memory_usage()

            trackables_to_update = {
                "active_gg": active_games[0],
                "active_ggg": active_games[1],
                "active_bg": active_games[2],
                "active_us": active_games[3],
                "active_others": active_games[4],
                "active_all": sum(active_games),
                "inactive_gg": inactive_games[0],
                "inactive_ggg": inactive_games[1],
                "inactive_bg": inactive_games[2],
                "inactive_us": inactive_games[3],
                "inactive_others": inactive_games[4],
                "inactive_all": sum(inactive_games),
                "total_gg": total_games[0],
                "total_ggg": total_games[1],
                "total_bg": total_games[2],
                "total_us": total_games[3],
                "total_others": total_games[4],
                "total_all": total_games[5],
                "users_in_bot_cache": len(self.bot.users),
                "servers_connected": len(self.bot.guilds),
                "ping_to_discord": botinfo.get_bot_ping(self.bot),
                # Wrapper Cache
                "count_of_interactions": len(await Interaction.get_all()),
                "interaction_types": len(await InteractionType.get_all()),
                "users_in_wrapper_cache": len(await User.get_all()),
                "count_of_groups": len(await Group.get_all()),
                "count_of_persons": len(await Person.get_all()),
                "count_of_affiliations": len(await Affiliation.get_all()),
                "eight_ball_responses": len(await EightBallResponse.get_all()),
                "count_of_auto_media": len(await AutoMedia.get_all()),
                "twitch_channels_followed": len(await TwitchAccount.get_all()),
                "twitter_accounts_followed": len(await TwitterAccount.get_all()),
                "active_user_reminders": len(await Reminder.get_all()),
                "user_notifications": len(await Notification.get_all()),
                "reaction_role_messages": len(await ReactionRoleMessage.get_all()),
                "peak_memory_usage": peak_memory_usage,
                "current_memory_usage": current_memory_usage,

                "user_requests_today": botinfo.get_today_user_requests(),
                "numbers_of_distance_words": botinfo.get_numbers_of_distance_words(),
            }

            for key, value in trackables_to_update.items():
                await main_helper.set_trackable(key, value)

            await tracker.update_to_api()

            self._loop_running = False
        except Exception as e:
            self.bot.logger.error(f"Stats Error -> {e}")
            self._loop_running = False


def setup(bot: commands.AutoShardedBot):
    cog = BotOwnerCog(bot)
    bot.add_cog(cog)
    cog.stats_updates.start()
