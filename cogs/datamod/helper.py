from typing import Optional
from IreneAPIWrapper.models import User, EightBallResponse, Interaction, InteractionType
from disnake import ApplicationCommandInteraction as AppCmdInter, Message
from disnake.ext import commands
from ..helper import send_message
