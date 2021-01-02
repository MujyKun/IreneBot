import discord
from discord.ext import commands
from module import logger as log
from Utility import resources as ex


class SelfAssignRoles(commands.Cog):
    def __init__(self):
        self.error_msg = f"> An error has occurred. Please report it."

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def setrolechannel(self, ctx, text_channel: discord.TextChannel = None):
        """Set the channel for self-assignable roles to be used in."""
        if not text_channel:
            text_channel = ctx.channel
        try:
            await ex.u_self_assign_roles.remove_current_channel_role(text_channel.id, ctx.guild.id)
            return await ctx.send(f"> Self-Assignable Roles was removed for {text_channel.name}")
        except KeyError:
            await ex.u_self_assign_roles.modify_channel_role(text_channel.id, ctx.guild.id)
            return await ctx.send(f"> Self-Assignable Roles can now only be used in {text_channel.name}")
        except Exception as e:
            log.console(e)
            return await ctx.send(self.error_msg)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def removerole(self, ctx, *, role_name):
        """Remove a self-assignable role based on the role name given.
        [Format: %removerole <role_name>]"""
        try:
            await ex.u_self_assign_roles.remove_self_role(role_name, ctx.guild.id)
            return await ctx.send(f"> If {role_name} existed as a Self-Assignable role, it was removed.")
        except Exception as e:
            log.console(e)
            return await ctx.send(self.error_msg)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def listroles(self, ctx):
        """List all the self-assignable roles in a server.
        [Format: %listroles]"""
        try:
            roles = await ex.u_self_assign_roles.get_assignable_server_roles(ctx.guild.id)
            if not roles:
                return await ctx.send("> You have no Self-Assignable roles in this server.")
            msg_body = ""
            for role_id, role_name in roles:
                msg_body += f"<@&{role_id}> - {role_name}\n"
            embed_title = f"{ctx.guild}'s Self-Assignable Roles"
            embed = await ex.create_embed(title=embed_title, title_desc=msg_body)
            return await ctx.send(embed=embed)
        except Exception as e:
            log.console(e)
            return await ctx.send(self.error_msg)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def addrole(self, ctx, role: discord.Role, *, role_name):
        """Add a role to be self-assignable.
        [Format: %addrole <role> <role name>]"""
        try:
            if await ex.u_self_assign_roles.check_self_role_exists(role.id, role_name, ctx.guild.id):
                return await ctx.send("> You have an identical role or role name, remove it first.")
            await ex.u_self_assign_roles.add_self_role(role.id, role_name, ctx.guild.id)
            await ctx.send(f"> Added {role.name} ({role_name}) to Self-Assignable Roles.")
        except Exception as e:
            log.console(e)
            return await ctx.send(self.error_msg)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def sendrolemessage(self, ctx):
        """Sends the default role message in the current channel. Is not needed for the roles to work."""
        roles = await ex.u_self_assign_roles.get_assignable_server_roles(ctx.guild.id)
        if not roles:
            return await ctx.send("> This server does not have any self-assignable roles.")
        role_names = [f"`{role[1]}`" for role in roles]

        message = f"""
How to use Self-Assigning Roles:

To add a role, use a `+` followed by the custom role name (One role per message).
To remove a role, use a `-` followed by the custom role name (One role per messsage).

Example: `+role name` to join a role. `-role name` to remove a role.

Available Roles: {', '.join(role_names)}
"""
        return await ctx.send(message)

    @addrole.before_invoke
    @setrolechannel.before_invoke
    @removerole.before_invoke
    @listroles.before_invoke
    @sendrolemessage.before_invoke
    async def check_server_id(self, ctx):
        server_id = await ex.get_server_id(ctx)
        if not server_id:
            await ctx.send("> You cannot use this command in DMs.")
            raise commands.CommandError(f"{ctx.author.id} attempted to use Self-Assignable Roles in DMs.")

