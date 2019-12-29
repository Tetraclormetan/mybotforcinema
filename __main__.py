
import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from imdb import IMDb, IMDbError
from kinopoisk.movie import Movie
# import wikipedia
# import urllib
# from bs4 import BeautifulSoup


# wikipedia.set_lang("ru")




'''
'airing', 'akas', 'alternate versions', 'awards',
 'connections', 'crazy credits', 'critic reviews',
  'episodes', 'external reviews', 'external sites',
   'faqs', 'full credits', 'goofs', 'keywords',
    'locations', 'main', 'misc sites', 'news',
     'official sites', 'parents guide',
      'photo sites', 'plot', 'quotes',
       'recommendations', 'release dates',
        'release info', 'reviews', 'sound clips',
         'soundtrack', 'synopsis', 'taglines',
          'technical', 'trivia', 'tv schedule',
           'video clips', 'vote details'''


bot = Bot(token='1067437658:AAGcrdziqbljDoeBFSDiPYxRJjFQHz5E-To')
dp = Dispatcher(bot)
ia = IMDb()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message) -> None:
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.\n Type /movie")


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message) -> None:
    await message.reply(ia.get_movie_infoset())


@dp.message_handler(commands=["movie"])
async def echo(message: types.Message) -> None:
    to_find = str(message.text[7:])
    try:
        await message.answer("searching movie...")


        # st = str(wikipedia.search(to_find))
        # serch_res = wikipedia.search(st)
        # found = wikipedia.search(st)[0]
        # if found:
        #    await message.reply(str(found))

        # await message.answer(st)

        movies = ia.search_movie(to_find)
        await message.answer("title: " + str(movies[0]["title"]))
        if "year" in movies[0]:
            await message.answer("\nyear: " + str(movies[0]["year"]))
        if "kind" in movies[0]:
            await message.answer("" + str(movies[0]["kind"]))
        await message.answer(movies[0]["cover url"])
        await message.answer("searching additional info...")
        ans = movies[0].getID()
        res = ia.get_movie(ans, info=['quotes', 'plot', 'awards', "full credits", "video clips"])
        await message.answer("processing info...")
        quotes = res.get('quotes', [])
        plot = res.get("plot")
        cred = res.get("cast")
        awards = res.get("awards", [])
        a = res.get("video clips")

        #if "genres" in res:
        #    await message.answer("genres: ", " ".join(res["genres"]))
        await message.answer(type(a))
        if a:
            await message.answer_video(a[0])
        if plot:
            await message.answer("plot: " + str(plot[0]))
        if cred:
            await message.answer("credits: \n " + str("\n".join([str(cred[i]["name"]) + " -- " + str(cred[i].currentRole) for i in range(min(len(cred), 5))])))
        if len(awards) > 0:
            awards = [str(x["award"]) + " " + str(x["year"]) + " " + (str(x["notes"] if "notes" in x else ""))
                      for x in awards]
            res_aw = "\n".join(awards[0: min(5, len(awards))])
            await message.answer("awards: \n" + res_aw)
        if len(quotes) > 0:
            await message.answer("best quote: \n " + str(quotes[0][0][:min(len(quotes[0][0]), 150)] +
                                                        ("..." if (len(quotes[0][0]) > 150) else "")))
    except IMDbError as e:
        await message.reply('try another')
    except Exception as ex:
        await message.reply(str(ex))
    try:
        await message.answer("Now kinopoisk")
        movie_list = Movie.objects.search(to_find)
        m = movie_list[0]
        m.get_content('main_page')
        await message.answer(m.year)
        await message.answer(m.title)
        await message.answer(m.plot)
        await message.answer(m.runtime)
        await message.answer(m.tagline)
        await message.answer(m.rating)
        await message.answer(m.imdb_rating)
        m.get_content('posters')
        if m.posters:
            await message.answer_photo(m.posters[0])

    except Exception as ex:
        await message.reply("kinopoisk wrong")


if __name__ == '__main__':
    executor.start_polling(dp)


'''

julia = i.get_person('0000210')
for job in julia['filmography'].keys():
    print('# Job: ', job)
    for movie in julia['filmography'][job]:
        print('\t%s %s (role: %s)' % (movie.movieID, movie['title'], movie.currentRole))
        
last = julia['filmography']['actress'][0]
# Retrieve full information
i.update(last)
# name of the first director
print(last['director'][0]['name'])


'''