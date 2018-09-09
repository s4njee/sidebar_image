from PIL import Image
from discord.ext import commands
from io import BytesIO
from urllib.parse import quote
import discord
import asyncio
import requests

apiKey = ''
apiSecret = ''
bot = commands.Bot(command_prefix='!')
client = discord.Client()

image_reactions = {'\U0001F4F7', '\u270F', '\U0001F4AF', '\u2705'}
update_content = []
active_updates = []
image_file = ''

@bot.command()
async def image(ctx, arg1, arg2, arg3):
    url = arg1
    caption = arg2
    stats = arg3

    await ctx.message.delete()
    
    coord = requests.get('https://api.imagga.com/v1/croppings?url=' + quote(url) + '&resolution=300x450&no_scaling=0',
                         auth=(apiKey, apiSecret)).json()['results'][0]['croppings'][0]
    
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image = image.crop((coord['x1'], coord['y1'], coord['x2'], coord['y2']))
    image.thumbnail((300,450), Image.ANTIALIAS)
    image.save('image.png')
    
    embed = discord.Embed(title="Sidebar Image Update", description="Are you sure you want to set this as the sidebar?", color=16753920)
    embed.add_field(name="New caption:", value=arg2, inline=False)
    embed.add_field(name="New stats:", value=arg3, inline=False)
    embed.add_field(name="To edit or confirm your changes", value=":camera: to edit the image\n:pencil2: to edit the caption\n:100: to edit the stats\n:white_check_mark:  to confirm your final changes", inline=False)

    global update_content
    global active_updates
    global image_file
    
    with open('image.png', 'rb') as f:
        update = await ctx.send(embed=embed, file=discord.File(f))
        
    for emoji in ('\U0001F4F7', '\u270F', '\U0001F4AF', '\u2705'):
        await update.add_reaction(emoji)
        
    update_content = [update.id,arg1,arg2,arg3,update]
    active_updates.append(update.id)
    image_file = image

@bot.event
async def on_reaction_add(reaction,user):
    
    global update_content
    global active_updates
    global image_file
    
    if reaction.message.id in active_updates and reaction.emoji in image_reactions and user != bot.user:
        if reaction.emoji == '\U0001F4F7':
            await update_content[4].delete()
            new_url_info = await reaction.message.channel.send('Okay, what\'s the new image url? Use `!editurl` before the url.')

            update_content[4] = new_url_info
            
        elif reaction.emoji == '\u270F':
            await update_content[4].delete()
            new_cap_info = await reaction.message.channel.send('Okay, what\'s the new caption? Use `!editcap` before the caption.')

            update_content[4] = new_cap_info
            
        elif reaction.emoji == '\U0001F4AF':
            
            await update_content[4].delete()
            new_stats_info = await reaction.message.channel.send('Okay, what are the new stats? Use `!editstats` before the stats.')

            update_content[4] = new_stats_info
            
        elif reaction.emoji == '\u2705':
            await update_content[4].delete()
            new_confirm_info = await reaction.message.channel.send('Okay, updating now!')            

            update_content[4] = new_confirm_info

            embed = discord.Embed(title="Sidebar Image Update", color=16753920)
            embed.add_field(name="New caption:", value=update_content[2], inline=False)
            embed.add_field(name="New stats:", value=update_content[3], inline=False)
            
            with open('image.png', 'rb') as f:
                await update_content[4].delete()
                final_msg = await reaction.message.channel.send(embed=embed, file=discord.File(f))
                await final_msg
            
            update_content = [update_content[0],update_content[1],update_content[2],update_content[3],final_msg]
            active_updates.append(final_msg.id)
            
            #sidebar function

@bot.event
async def on_message(message):
    
    global update_content
    global active_updates
    global image_file
    
    if message.content.startswith('!edit'):
        if message.content.startswith('!editurl'):
            
            new_url = message.content[9:]
            url = new_url

            await update_content[4].delete()
            await message.delete()
            
            coord = requests.get('https://api.imagga.com/v1/croppings?url=' + quote(url) + '&resolution=300x450&no_scaling=0',
                                 auth=(apiKey, apiSecret)).json()['results'][0]['croppings'][0]
            
            response = requests.get(url)
            image = Image.open(BytesIO(response.content))
            image = image.crop((coord['x1'], coord['y1'], coord['x2'], coord['y2']))
            image.thumbnail((300,450), Image.ANTIALIAS)
            image.save('image.png')
            
            embed = discord.Embed(title="Sidebar Image Update", description="Are you sure you want to set this as the sidebar?", color=16753920)
            embed.add_field(name="New caption:", value=update_content[2], inline=False)
            embed.add_field(name="New stats:", value=update_content[3], inline=False)
            embed.add_field(name="To edit or confirm your changes", value=":camera: to edit the image\n:pencil2: to edit the caption\n:100: to edit the stats\n:white_check_mark:  to confirm your final changes", inline=False)
            
            with open('image.png', 'rb') as f:
                new_url_msg = await message.channel.send(embed=embed, file=discord.File(f))

            for emoji in ('\U0001F4F7', '\u270F', '\U0001F4AF', '\u2705'):
                await new_url_msg.add_reaction(emoji)
            
            update_content = [new_url_msg.id,new_url,update_content[2],update_content[3],new_url_msg]
            active_updates.append(new_url_msg.id)
                
        if message.content.startswith('!editcap'):
            new_cap = message.content[9:]

            await update_content[4].delete()
            await message.delete()

            embed = discord.Embed(title="Sidebar Image Update", description="Are you sure you want to set this as the sidebar?", color=16753920)
            embed.add_field(name="New caption:", value=new_cap, inline=False)
            embed.add_field(name="New stats:", value=update_content[3], inline=False)
            embed.add_field(name="To edit or confirm your changes", value=":camera: to edit the image\n:pencil2: to edit the caption\n:100: to edit the stats\n:white_check_mark:  to confirm your final changes", inline=False)
            
            with open('image.png', 'rb') as f:
                new_cap_msg = await message.channel.send(embed=embed, file=discord.File(f))

            for emoji in ('\U0001F4F7', '\u270F', '\U0001F4AF', '\u2705'):
                await new_cap_msg.add_reaction(emoji)
            
            update_content = [new_cap_msg.id,update_content[1],new_cap,update_content[3],new_cap_msg]
            active_updates.append(new_cap_msg.id)
        if message.content.startswith('!editstats'):
            new_stats = message.content[10:]

            await update_content[4].delete()
            await message.delete()

            embed = discord.Embed(title="Sidebar Image Update", description="Are you sure you want to set this as the sidebar?", color=16753920)
            embed.add_field(name="New caption:", value=update_content[2], inline=False)
            embed.add_field(name="New stats:", value=new_stats, inline=False)
            embed.add_field(name="To edit or confirm your changes", value=":camera: to edit the image\n:pencil2: to edit the caption\n:100: to edit the stats\n:white_check_mark:  to confirm your final changes", inline=False)
            
            with open('image.png', 'rb') as f:
                new_stats_msg = await message.channel.send(embed=embed, file=discord.File(f))

            for emoji in ('\U0001F4F7', '\u270F', '\U0001F4AF', '\u2705'):
                await new_stats_msg.add_reaction(emoji)
            
            update_content = [new_stats_msg.id,update_content[1],update_content[2],new_stats,new_stats_msg]
            active_updates.append(new_stats_msg.id)

    await bot.process_commands(message)
     
bot.run('')
