import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from imdb import IMDb, IMDbError
from kinopoisk.movie import Movie
import re
import urllib.request
import urllib.parse

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
    await message.reply("Type /movie <title> \n or /actor <full name>")


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message) -> None:
    # await message.reply(ia.get_movie_infoset())
    await message.reply("Type /movie <title> \n or /actor <full name>")


@dp.message_handler(commands=["movie"])
async def echo(message: types.Message) -> None:
    to_find = str(message.text[7:])

    query_string = urllib.parse.urlencode({"search_query": to_find+" trailer"})
    html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    await message.answer("http://www.youtube.com/watch?v=" + search_results[0])

    try:
        await message.answer("searching movie imdb...")

        movies = ia.search_movie(to_find)
        if movies:
            # raise Exception("skip")
            s = ""
            if "title" in movies[0]:
                s += "\ntitle: " + str(movies[0]["title"])
            if "year" in movies[0]:
                s += "\nyear: " + str(movies[0]["year"])
            if "kind" in movies[0]:
                s += "\n" + str(movies[0]["kind"])
            if s:
                await message.answer("main info:\n" + s)

            await message.answer("searching additional info...")

            ans = movies[0].getID()
            res = ia.get_movie(ans, info=['quotes', 'plot', 'awards', "full credits", "video clips", "main", 'reviews',
                                          ])

            quotes = res.get('quotes', [])
            plot = res.get("plot")
            cred = res.get("cast")
            awards = res.get("awards", [])
            poster = res.get("cover url")
            video_ref = res.get("video clips and trailers", [])
            r = res.get("rating")
            revs = res.get('reviews', [])

            if r:
                await message.answer("rating: " + str(r))

            if plot:
                await message.answer("plot: " + str(plot[0]))
            if cred:
                await message.answer("credits:\n " + str("\n".join([str(cred[i]["name"]) +
                                                                    " -- " + str(cred[i].currentRole) for i in
                                                                    range(min(len(cred), 5))])))
            if len(awards) > 0:
                awards = [str(x["award"]) + " " + str(x["year"]) + " " + (str(x["notes"] if "notes" in x else ""))
                          for x in awards]
                res_aw = "\n".join(awards[0: min(5, len(awards))])
                await message.answer("awards: \n" + res_aw)

            if len(quotes) > 0:
                await message.answer("best quote: \n " + str(quotes[0][0][:min(len(quotes[0][0]), 150)] +
                                                             ("..." if (len(quotes[0][0]) > 150) else "")))

            if len(revs) > 0:
                rev = ["review " + str(i + 1) + ") :" + str(revs[i]["content"][: min(300, len(revs[i]["content"]))])
                       + ("..." if (len(revs[i]["content"]) > 300) else "") for i in range(min(5, len(revs)))]
                await message.answer("top reviews:\n" + "\n".join(rev))

            await message.answer("processing poster...")
            if poster:
                await message.answer_photo(poster)

            if video_ref:
                ur = video_ref[0][1]
                ur = "".join(ur.split("\t"))
                ur = "".join(ur.split("\n"))
                await message.answer("smth like trailer:")
                await message.answer(ur)
                # await message.answer_video(ur)
        else:
            await message.answer("nothing found")
    except IMDbError as e:
        await message.reply('try another (c) IMDB')
    except Exception as ex:
        await message.reply(str(ex))
    try:
        await message.answer("Kinopoisk")
        movie_list = Movie.objects.search(to_find)
        if len(movie_list) == 0:
            await message.answer("nothing found")
            return None
        m = movie_list[0]
        m.get_content('main_page')
        if hasattr(m, 'title'):
            await message.answer("title: " + m.title)
        if hasattr(m, 'year'):
            await message.answer(m.year)
        if hasattr(m, 'plot'):
            await message.answer("plot:\n" + m.plot)
        if hasattr(m, 'rating'):
            await message.answer("rating " + str(m.rating))
        if m.imdb_rating:
            await message.answer("imdb rating: " + str(m.imdb_rating))
        if hasattr(m, "actors"):
            await message.answer("actors: \n" + "\n".join(str(x) for x in m.actors[: min(len(m.actors), 5)]))
        # await message.answer(m.runtime)
        # await message.answer(m.tagline)
        await message.answer("wait for large data...")
        m.get_content('posters')
        if m.posters:
            await message.answer_photo(m.posters[0])
        m.get_content('trailers')
        if m.trailers and m.trailers[0].is_valid:
            # await message.answer(str(dir(m.trailers[0])))
            # await message.answer(str(m.trailers[0].file[:min(50, len(m.trailers[0].file))]))
            await message.answer("https://www.kinopoisk.ru/trailer/player/share/" + str(m.trailers[0].id) + "/?share=true")

            #file = m.trailers[0].file
            #await message.answer_video(file)
        else:
            await message.answer("no trailer, sorry")
        await message.answer("end of processing")
    except Exception as ex:
        await message.reply(str(ex))


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
