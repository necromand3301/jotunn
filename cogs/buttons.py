import discord
from discord.ext import commands

class SimpleView(discord.ui.View):
    # This view creates two buttons, after clicking one of them, both will fe disabled
    def __init__(self):
        super().__init__()
        self.message = ""

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label="Hello",
                       style=discord.ButtonStyle.success)
    async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("World")
        await self.disable_all_items()
        self.stop()

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling")
        await self.disable_all_items()
        self.stop()

class KickUser(discord.ui.View):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.message = ""

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label="Yes",
                       style=discord.ButtonStyle.success)
    async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"User {self.member.mention} is kicked")
        await self.disable_all_items()
        self.stop()

    @discord.ui.button(label="Cancel",
                       style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelling")
        await self.disable_all_items()
        self.stop()

class Buttons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def simple_button(self, ctx):
        view = discord.ui.View()
        button = discord.ui.Button(label="Click me")
        view.add_item(button)
        await ctx.send(view=view)

    @commands.command()
    async def button(self, ctx):
        view = SimpleView()
        message = await ctx.send(view=view)
        view.message = message

    @commands.command()
    async def kick(self, ctx, member: discord.Member):
        view = KickUser(member)
        message = await ctx.send(f"Are you sure you want to kick user {member.mention}", view=view)
        view.message = message


async def setup(bot):
    await bot.add_cog(Buttons(bot))
