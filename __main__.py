import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from imdb import IMDb, IMDbError, Person
from kinopoisk.movie import Movie
from google import google
import re
import urllib.request
import urllib.parse
import pytube

bot = Bot(token='1067437658:AAGcrdziqbljDoeBFSDiPYxRJjFQHz5E-To')
dp = Dispatcher(bot)
ia = IMDb()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message) -> None:
    await message.reply("Type /movie <title> \n or /person <full name>")


@dp.message_handler(commands=["movie"])
async def echo(message: types.Message) -> None:
    to_find = str(message.text[7:])
    await message.answer("got task")

    try:
        search_results = google.search(to_find + " watch online")
        if search_results:
            await message.answer("try to watch at: ")
            await message.answer(search_results[0].link)
    except Exception:
        await message.answer("nowhere to watch online")

    try:
        await message.answer("searching movie imdb...")

        movies = ia.search_movie(to_find)
        if movies:
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
        pass
        # await message.reply(str(ex))

    try:
        await message.answer("Kinopoisk")
        movie_list = Movie.objects.search(to_find)
        if len(movie_list) == 0:
            await message.answer("nothing found")
            return None
        m = movie_list[0]
        try:
            m.get_content('main_page')
        except Exception:
            pass
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
        await message.answer("wait for large data...")
        try:
            m.get_content('posters')
            if m.posters:
                await message.answer_photo(m.posters[0])
        except Exception:
            pass
        try:
            m.get_content('trailers')
            if m.trailers and m.trailers[0].is_valid:
                await message.answer("https://www.kinopoisk.ru/trailer/player/share/" +
                                 str(m.trailers[0].id) + "/?share=true")
            else:
                await message.answer("no trailer, sorry")
        except Exception:
            pass

        await message.answer("now really long video sending, get ready\n let's count til sended")
        try:
            await message.answer("three")
            query_string = urllib.parse.urlencode({"search_query": to_find + " trailer"})
            await message.answer("two")
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            await message.answer("one")
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            yt = None
            for el in search_results:
                try:
                    yt = pytube.YouTube("http://www.youtube.com/watch?v=" + el)
                    break
                except Exception:
                    pass
            if not yt:
                await message.answer("omg no videos")
                raise Exception("omg no videos")

            await message.answer("zero")

            st = yt.streams.filter(file_extension='mp4').all()
            if st:
                await message.answer("negative one")
                if len(st) > 1:
                    st[-2].download()
                else:
                    st[0].download()
                await message.answer("negative two")
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            for f in files:
                if f.endswith(".mp4"):
                    with open(f, "rb") as fl:
                        await message.answer("negative infinity")
                        await bot.send_video(chat_id=message.chat.id, video=fl, supports_streaming=True)
                    os.remove(f)
        except Exception as ex:
            # await message.reply(str(ex))
            pass

    except Exception as ex:
        # await message.reply(str(ex))
        pass
    await message.answer("end of processing")


@dp.message_handler(commands=["person"])
async def echo(message: types.Message) -> None:
    pers = str(message.text[7:])
    await message.answer("got name")
    try:

        persons = ia.search_person(pers)
        if len(persons) == 0:
            await message.answer("nothing found")
            return
        person = ia.get_person(persons[0].getID(), info=['main', 'biography', 'filmography'])
        if 'name' in person:
            await message.answer("name: " + str(person['name']))
        if 'mini biography' in person:
            await message.answer("biography: \n" +
                                 str(person['mini biography'][0][:min(150, len(person['mini biography'][0]))]) + "...")
        if 'filmography' in person:
            await message.answer("filmography: \n")
            for el, val in person['filmography'].items():
                await message.answer(str(el) + " : " + ", ".join(str(x) for x in val[:min(len(val), 5)]))
        if 'headshot' in person:
            await message.answer_photo(person['headshot'])
        await message.answer("end of processing")
    except Exception as ex:
        pass
        # await message.answer(str(ex))


if __name__ == '__main__':
    executor.start_polling(dp)

