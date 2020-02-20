import os
import uuid
from urllib.request import urlretrieve
from discord.ext import commands
from module import quickstart

client = 0


def setup(client1):
    client1.add_cog(ImageUploader(client1))
    global client
    client = client1

# This does not work perfectly as it blocks other commands - was not built for async - they added new methods to grabbing files, so this is kinda pointless
# but it may be helpful in certain cases.
# does not always grab the right file format? was not tested enough.
class ImageUploader(commands.Cog):
    final_url = ""

    def __init__(self, client):
        pass

    @commands.command(aliases=["log"])
    @commands.is_owner()
    async def steal(self, ctx, *, amount=0):
        """Downloads Images from Current Text Channel [Format: %steal (amount of messages)][Aliases: log]"""
        if amount == 0:
            amount = None
        print("Starting to download images to PC")
        count = 0
        async for response in ctx.history(limit=amount):
            # await asyncio.sleep(1)
            # attachment
            try:
                if len(response.attachments) >= 1:
                    # await ctx.send("> {}".format(response.attachments[0].url))
                    # file_name1 = response.attachments[0].filename
                    all_photos = os.listdir('Photos')
                    """
                    for photo in all_photos:
                        if photo != file_name1:
                            pass
                        else:
                            file_name1 = str(uuid.uuid1()) + file_name1
                    """
                    file_name1 = str(uuid.uuid1()) + file_name1
                    url = "{}".format(response.attachments[0].url)
                    await response.attachments[0].save("Photos/{}".format(file_name1))
                    # await ctx.send("{} has been saved to your PC".format(file_name1))
                    # urlretrieve(url, "local-filename.jpg")
                    count += 1
                    print("Finished downloading #{}".format(count))
                # embed
                elif len(response.embeds) >= 1:
                    # await ctx.send("> {}".format(response.embeds[0].url))
                    url = "{}".format(response.embeds[0].url)
                    type = response.embeds[0].type
                    # print (url)
                    # print (type)
                    if type == "gifv":
                        keep_going = False
                    elif type == "image":
                        file_name1 = str(uuid.uuid1()) + ".jpg"
                        keep_going = True
                    elif type == "link":
                        keep_going = False
                    elif type == "video":
                        keep_going = False
                    elif type == "article":
                        keep_going = False
                    elif type == "rich":
                        keep_going = False
                    else:
                        print("THERE IS A NEW TYPE!")

                    if keep_going == True:
                        # file_name1 = str(uuid.uuid1()) + ".jpg"
                        # await ctx.send("{} has been saved to your PC".format(file_name1))
                        urlretrieve(url, "Photos/{}".format(file_name1))
                        count += 1
                        print("Finished downloading #{}".format(count))
                        # print ("Finished downloading #{} for {}".format(count,file_name1))
                else:
                    # print ("Not an attachment or image")
                    pass
            except:
                pass

        await ctx.send("> **{}** Photos have been saved to your PC".format(count))

    @commands.command()
    @commands.is_owner()
    async def upload(self, ctx, *, filename=''):
        """Uploads All Images in the Photos Folder to Google Drive [Format: %upload (all/filename)]"""
        print("Startng to upload photos to Google Drive")
        try:
            count = 0
            if filename == '':
                await ctx.send("> The proper format is `%upload filename.type`")
            elif filename == 'all':
                all_photos = os.listdir('Photos')
                for photo in all_photos:
                    count += 1
                    print("Currently Uploading Number **{}**".format(count))
                    # print ("Currently Uploading {}, Number: {}".format(photo,count))
                    quickstart.main(photo)
                await ctx.send(
                    "> All Photos have been uploaded to the Google Drive at \n> <https://drive.google.com/drive/folders/1VMG-6m1p_5W-JquWMCA-DZRUnYAFujUd?usp=sharing>")
            else:
                await ctx.send("> Uploading {} to Google Drive".format(filename))
                quickstart.main(filename)
                f = open("link.txt", "r")
                final_url = f.read()
                f.close()
                await ctx.send("> Here is the link: <{}>".format(final_url))
                os.remove("link.txt")
        except:
            await ctx.send("> That image name does not exist in Photos")

    @commands.command()
    @commands.is_owner()
    async def deletephotos(self, ctx):
        """Delete All Photos in Photos Folder [Format: %deletephotos]"""
        count = 0
        all_photos = os.listdir('Photos')
        for photo in all_photos:
            try:
                os.unlink('Photos/{}'.format(photo))
                count += 1
            except:
                pass
        await ctx.send("> **{}** Photos have been deleted.".format(count))

    @commands.command()
    @commands.is_owner()
    async def view(self, ctx):
        """Shows amount of Images in the Photos Folder [Format: %view]"""
        all_photos = os.listdir('Photos')
        print(all_photos)
        await ctx.send("> There are **{}** Photos ready to be uploaded.".format(len(all_photos)))

