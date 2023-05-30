from discord.ext import commands, tasks
import os
from dataclasses import dataclass
import discord

BOT_TOKEN = os.getenv('BOT_TOKEN')
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)



@dataclass
class Settings:
    sleeping = False
    movie_id = None
    confirm_clicked = None
    server = None

sleeping = False
settings = Settings()

@bot.event
async def on_ready():
    cogs_folder = 'cogs'  # Add to settings.py
    cogs_files = [file for file in os.listdir(cogs_folder) if file.endswith('.py')]
    await bot.tree.sync()
    for file in cogs_files:
        if file.endswith('.py'):
            cog_name = file[:-3]  # Remove the '.py' extension
            cog_module = f"{cogs_folder}.{cog_name}"
            try:
                await bot.load_extension(cog_module)
                print(f"Loaded extension: {cog_module}")
            except Exception as e:
                print(f"Failed to load extension {cog_module}. Error: {e}")

    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("Developing..."))
    print(f"Bot is ready. Logged in as {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        # Handling missing permissions error
        await ctx.send("You don't have the required permissions to run this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        # Handling missing required argument error
        await ctx.send("Please provide all the required arguments for this command.")
    elif isinstance(error, commands.BadArgument):
        # Handling bad argument error
        await ctx.send("One or more arguments are of the wrong type.")
    else:
        # Handling other errors
        await ctx.send(f"An error occurred: {str(error)}")

@bot.event
async def on_message(ctx):
    if not settings.sleeping:
        await bot.process_commands(ctx)
    else:
        if ctx.content == "!wakeup":
            user = ctx.author
            permissions = ctx.channel.permissions_for(user)
            if permissions.administrator:
                await bot.change_presence(status=discord.Status.online)
                await ctx.channel.send("I'm awake now")
                settings.sleeping = False

@bot.event
async def on_member_join(member):
    direct_message = 'Welcome to the server!'
    await member.send(direct_message)

@bot.command()
async def avatar(ctx, *, member: discord.Member):
    avatar_url = member.avatar.url
    embed = discord.Embed(title=f"Profile picture of {member.mention}")
    embed.set_image(url=avatar_url)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def sleep(ctx):
    await ctx.send("Sleeping...")
    await bot.change_presence(status=discord.Status.offline)
    settings.sleeping = True







import imdb
from discord import Embed
import sqlite3
from datetime import datetime, timedelta
import typing
from discord import app_commands
import emoji


ia = imdb.IMDb()
conn = sqlite3.connect('movies.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS movies
                  (id TEXT, name TEXT, username TEXT, date TEXT, server TEXT)''')

def get_movie_names(query):
    ia = imdb.IMDb()
    movies = ia.search_movie(query)

    if not movies:
        return []

    movie_names = [movie['title'] for movie in movies[:5]]
    return movie_names

async def request_autocompletion(
        interaction: discord.Interaction,
        current: str
) -> typing.List[app_commands.Choice[str]]:
    movies = get_movie_names(current)
    data = []
    for movie_choice in movies:
        if current.lower() in movie_choice.lower():
            data.append(app_commands.Choice(name=movie_choice, value=movie_choice))
    print(data)
    return data

@bot.tree.command(name="request")
@app_commands.autocomplete(movie_title=request_autocompletion)
async def request(interaction: discord.Interaction, movie_title: str):
    async def movies_select_callback(interaction: discord.Interaction):
        async def movie_confurm(interaction: discord.Interaction, embed):
            async def server_select_callback(interaction: discord.Interaction, embed):
                name = embed.title
                server = server_select.values[0]
                start_date = datetime.now().date()
                end_date = start_date + timedelta(days=5)
                query = '''SELECT * FROM movies WHERE name=? AND server=? AND date BETWEEN ? AND ?'''
                cursor.execute(query, (name, server, start_date, end_date))
                rows = cursor.fetchall()
                if len(rows) > 0:
                    embed = Embed(
                        title=f':x: This movie is already requested by this user {rows["username"]}.',
                        color=discord.Color.red()
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
                else:
                    embed_c = Embed(
                        title=':white_check_mark: Your request has been sent.',
                        color=discord.Color.green()
                    )
                    await interaction.response.edit_message(embed=embed_c, view=None)
                    user_id = 631222064400957441
                    embed.add_field(name='Server', value=f'{server}', inline=True)
                    await bot.get_user(user_id).send(embed=embed)
                    current_time = datetime.now().strftime("%Y-%m-%d")
                    sample_data = ("id", name, str(interaction.user), current_time, server)
                    cursor.execute('INSERT INTO movies VALUES (?,?,?,?,?)', sample_data)
                    conn.commit()

            server_select = discord.ui.Select(placeholder="Select a server",
                                              min_values=1,
                                              max_values=1,
                                              options=[
                                                  discord.SelectOption(label='AM', emoji=emoji.emojize(":blue_circle:"),
                                                                       description=f"Yerevan", value="AM"),
                                                  discord.SelectOption(label='US', emoji=emoji.emojize(":red_circle:"),
                                                                       description=f"New York", value="US")
                                              ])
            server_select.callback = lambda interaction: server_select_callback(interaction, embed)
            server_view = discord.ui.View()
            server_view.add_item(server_select)
            await interaction.response.edit_message(embed=None, view=server_view)

        async def movie_cancel(interaction: discord.Interaction):
            print(2)
            embed = Embed(
                title=':x: Your request has been canceled.',
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)

        embed = Embed(
            title=':information_source: Fetching data...',
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        movie = ia.get_movie(movies_select.values[0])
        movie_name = movie.get('title', 'N/A')
        movie_length = int(movie.get('runtime', 'N/A')[0])
        movie_length = f"{movie_length // 60}:{movie_length % 60}"
        age_ratings = movie.get('certificates', {})
        for rating in age_ratings:
            if rating.startswith("United States:"):
                us_age_rating = rating.split(":")[1]
                break
        else:
            us_age_rating = 'N/A'
        year = movie.get('year', 'N/A')
        media_type = movie.get('kind', 'N/A')
        description = movie.get('plot', 'N/A')[0][0:500] + "..."
        poster_url = movie.get('cover url')
        current_time = datetime.now().strftime("%H:%M")
        embed = Embed(
            title=f'{movie_name} ({year})',
            description=description,
            color=discord.Color.blue()
        )
        embed.add_field(name='Media Type', value=media_type, inline=True)
        embed.add_field(name='Age Raiting', value=us_age_rating, inline=True)
        embed.add_field(name='Runtime', value=f'{movie_length}', inline=True)
        embed.set_thumbnail(url=poster_url)
        embed.set_footer(text=f'Made with ❤️ by {interaction.user.name} - Today at {current_time}')
        button_confurm = discord.ui.Button(style=discord.ButtonStyle.success, label="Confirm")
        button_confurm.callback = lambda interaction: movie_confurm(interaction, embed)
        button_cancel = discord.ui.Button(style=discord.ButtonStyle.danger, label="Cancel")
        button_cancel.callback = movie_cancel
        button_view = discord.ui.View()
        button_view.add_item(button_confurm)
        button_view.add_item(button_cancel)
        await interaction.edit_original_response(embed=embed, view=button_view)

    embed = Embed(
        title=':information_source: Fetching data...',
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)
    movies = ia.search_movie(movie_title)
    movies_select = discord.ui.Select(placeholder="Choose color",
                                      min_values=1,
                                      max_values=1,
                                      options=[
                                          discord.SelectOption(label=movie['title'], emoji="🍿", description=f"Movie ({movie['year']})", value=movie.movieID) for movie in movies
                                      ])
    movies_view = discord.ui.View()
    movies_view.add_item(movies_select)
    movies_select.callback = movies_select_callback
    await interaction.edit_original_response(view=movies_view, embed=None)


@bot.tree.command(name="color")
async def color(interaction: discord.Interaction):
    choose_color = discord.ui.Select(
        placeholder="Choose color",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Green",
                value="green",
                emoji=emoji.emojize(":green_circle:")
            ),
            discord.SelectOption(
                label="Red",
                value="red",
                emoji=emoji.emojize(":red_circle:")
            ),
            discord.SelectOption(
                label="Blue",
                value="blue",
                emoji=emoji.emojize(":blue_circle:")
            )
        ]
    )
    async def show(interaction: discord.Interaction):
        embed = discord.Embed(title="Color", description=f"You selected {choose_color.values[0]}", color=discord.Color.red())
        await interaction.response.edit_message(content=None, embed=embed)

    async def callback(interaction: discord.Interaction):
        button = discord.ui.Button(style=discord.ButtonStyle.danger, label="Click me")
        button.callback = show
        my_view = discord.ui.View()
        my_view.add_item(button)
        await interaction.response.edit_message(content=f"You selected {choose_color.values[0]}", view=my_view)
    choose_color.callback = callback
    my_view = discord.ui.View()
    my_view.add_item(choose_color)

    await interaction.response.send_message("Choose color", view=my_view)

bot.run(BOT_TOKEN)

