import asyncio
import discord
from discord.ext import commands
from discord.utils import get
import random
from dataclasses import dataclass

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wordle(self, ctx, command):
        if command == "start":
            if constants.wordle_active:
                await ctx.send("A game is already active!")
                return
            else:
                constants.wordle_word = self.generate_word()
                constants.wordle_active = True
                constants.wordle_player = ctx.author
                await ctx.send("The game has started. Guess the word!")
                return
        elif command == "stop":
            constants.wordle_active = False
            constants.wordle_word = ""
            constants.wordle_player = ""
            constants.wordle_attept = 6
            constants.wordle_guess.clear()
            await ctx.send("wordle is stopped")
            return
        else:
            await ctx.send('**Please pass in all requirements. Type ** `!help command` **for more information **')

    def generate_word(self):
        with open("../data/wordle.txt", "r") as f:
            data = f.readlines()
            word = random.choice(data)
            return word[:5]

    def word_game(self, input, size: int = 5):
        input = str(input.lower())
        if len(input) != 5:
            return "The length of the input must be 5"
        if not input.isalpha():
            return "The input must contains only letters"
        if input == constants.wordle_word:
            constants.wordle_active = False
            constants.wordle_word = ""
            constants.wordle_player = ""
            constants.wordle_attept = 6
            constants.wordle_guess.clear()
            return f"```ansi\n {constants.color_green}{input}{constants.color_end} Correct! \n```"
        guessed_word = ""
        response = ""
        for i in range(len(input)):
            if input[i] == constants.wordle_word[i]:
                guessed_word += f"{constants.color_green}{input[i]} {constants.color_end}"
            elif constants.wordle_word.count(input[i]) > 0:
                guessed_word += f"{constants.color_yellow}{input[i]} {constants.color_end}"
            else:
                guessed_word += f"{constants.color_red}{input[i]} {constants.color_end}"
        # guessed_word = f"""```ansi\n{guessed_word}\n```"""
        constants.wordle_guess.append(guessed_word)
        constants.wordle_attept -= 1
        if constants.wordle_attept == 0:
            return f"You losed, the word is {constants.wordle_word}"
        for guessed_word in constants.wordle_guess:
            response += guessed_word + "\n"
        response += ("- " * size + "\n") * constants.wordle_attept
        response = f"""```ansi\n{response}\n```"""
        return response


@dataclass
class Constants:
    color_red = "[2;31m"
    color_green = "[2;32m"
    color_yellow = "[2;33m"
    color_end = "[0m"

    wordle_active = False
    wordle_word = ""
    wordle_player = ""
    wordle_attept = 6
    wordle_guess = []
    
constants = Constants()

async def setup(bot: commands.Bot):
    await bot.add_cog(Game(bot))
