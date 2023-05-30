import discord
from discord.ext import commands
from discord import Embed

class Dropdown(discord.ui.Select):
    def __init__(self, args):

        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label=f'{args[0]}', description='Your favourite colour is red', emoji='🟥'),
            discord.SelectOption(label=f'{args[1]}', description='Your favourite colour is green', emoji='🟩'),
            discord.SelectOption(label=f'{args[2]}', description='Your favourite colour is blue', emoji='🟦'),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Choose your favourite colour...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(f'Your favourite colour is {self.values[0]}')

class DropdownView(discord.ui.View):
    def __init__(self,args):
        super().__init__()
        # Adds the dropdown to our view object.
        self.add_item(Dropdown(args))

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def embed(self, ctx):
        embed = Embed(
            title='Embed Title',
            description='Embed Description',
            color=discord.Color.blue()
        )
        embed.set_author(name=ctx.author.display_name, url="https://twitter.com/RealDrewData",
                         icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url="https://i.imgur.com/6yHmlwT.jpeg")
        embed.set_image(url="https://i.imgur.com/axLm3p6.jpeg")
        embed.add_field(name='Field 1', value='Value 1', inline=True)
        embed.add_field(name='Field 2', value='Value 2', inline=True)
        embed.set_footer(text='Embed Footer')

        await ctx.channel.send(embed=embed)

    @commands.command()
    async def dropdown(self, ctx, *args):
        await ctx.send("Choose a flavor!", view=DropdownView(args))


async def setup(bot: commands.Bot):
    await bot.add_cog(Embeds(bot))
