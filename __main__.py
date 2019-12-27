
import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from imdb import IMDb, IMDbError
# import wikipedia
# import urllib
# from bs4 import BeautifulSoup


# wikipedia.set_lang("ru")


bot = Bot(token='1067437658:AAGcrdziqbljDoeBFSDiPYxRJjFQHz5E-To')
dp = Dispatcher(bot)
ia = IMDb()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message) -> None:
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.\n Type /movie")


@dp.message_handler(commands=["movie"])
async def echo(message: types.Message) -> None:
    try:
        await message.answer("searching movie...")
        to_find = str(message.text[7:])

        # st = str(wikipedia.search(to_find))
        # serch_res = wikipedia.search(st)
        # found = wikipedia.search(st)[0]
        # if found:
        #    await message.reply(str(found))

        # await message.answer(st)

        movies = ia.search_movie(message.text[7:])
        await message.reply("title: " + str(movies[0]["title"]) + "\nyear: " + str(movies[0]["year"]) + "\n" +
        #                    str(movies[0]['kind']) +
                            "\n")
        await message.answer(movies[0]["cover url"])
        await message.reply("searching additional info...")
        ans = movies[0].getID()
        res = ia.get_movie(ans, info=['quotes', 'plot', 'awards', "full credits"])
        await message.reply("processing info...")
        quotes = res.get('quotes', [])
        plot = res.get("plot")
        cred = res.get("cast")
        awards = res.get("awards", [])
        # movie = ia.get_movie('0133093', info=['full credits'])  # Matrix
        # assert 'cast' in movie
        await message.reply("plot: " + str(plot[0]))
        if cred:
            await message.reply("credits: \n " + str("\n".join([str(cred[i]) for i in range(min(len(cred), 5))])))
        if len(awards) > 0:
            awards = [str(x["award"]) + " " + str(x["year"]) + " " + (str(x["notes"] if "notes" in x else ""))
                      for x in awards]
            res_aw = "\n".join(awards[0: min(5, len(awards))])
            await message.reply("awards: \n" + res_aw)
        if len(quotes) > 0:
            await message.reply("best quote: \n " + str(quotes[0][0][:min(len(quotes[0][0]), 150)] +
                                                        ("..." if (len(quotes[0][0]) > 150) else "")))
    except IMDbError as e:
        await message.reply('try another')
    except Exception as ex:
        await message.reply("Try smth else")


if __name__ == '__main__':
    executor.start_polling(dp)
