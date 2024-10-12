from flask import Flask, render_template, redirect, jsonify, request, url_for
from graph import cache
import time
import graph


app = Flask(__name__)

cache.init_app(app) # initialize cache in app


@app.route('/')
def index():
    return redirect("/anime")
        #return redirect('/winter/2024')

'''@app.route('/favicon.ico')
def favicon():
    return None'''

@app.route('/seasons')
def seasons():
    return redirect(f'/winter/2024/TV')

@app.route('/anime', methods=['GET'])
def anime():
    time.sleep(0.3)
    title = request.args.get('title')
    genre = request.args.get('selectgenre')
    if not title and not genre:
        # get all animes and sort by popularity
        data = graph.get_anime_by_title(None)
        print('1 working')
    elif title and not genre:
        data = graph.get_anime_by_title(title)
        print('2 working')
    elif not title and genre:
        # get all animes by genre and sort by popularity
        data = graph.get_anime_by_genre(genre)
        print('3 working')
    elif title and genre:
        data = graph.get_anime_by_title(title, genre)
        print('4 working')
    '''
    if request.args.get('selectgenre') is not "":
        data = graph.get_anime_by_title(request.args.get('title'), request.args.get('selectgenre'))
    else:
        data = graph.get_anime_by_title(request.args.get('title'))
    '''
    
    return render_template('anime.html', title="Search", data=data)

@app.route('/anime/<int:id>', methods=['GET'])
def gotoanime(id: int):
    data = graph.get_anime_info(id)
    if not data:
        return redirect('/404')
    return render_template('animeinfo.html', title="Anime", data=data)


@app.route('/<season>/<int:year>/<format>', methods=['GET'])
@app.route('/<season>/<int:year>/<format>/<int:page>', methods=['GET'])
def anime_season(season, year, format='TV', page=0):
        
        if page is None:
            print('page is none')
            return redirect(f'/{season}/{year}/{format}/0')
        cache_key = f"{season.lower()}-{year}-{format}-{page}"
        print(cache_key)
        cached_data = cache.get(cache_key)
        title = f'{season.capitalize()} {year}'
        if cached_data:
            print("CACHED!")
            return render_template('season.html', title=title, data=cached_data)

        # If data is not cached, retrieve it and cache it
        print("NOT CACHED!!!")
        variables = {
            'season': season.upper(),
            'seasonYear': year,
            'format': format,
            'page': page
        }
        season_data = graph.get_anime_season(variables)
        cache.set(cache_key, season_data)
        return render_template('season.html',title=title, data=season_data)

@app.route('/gotoseason', methods=['POST'])
def gotoseason():
    try:
        season = request.form['season']
        year = request.form['yearint']
        format = request.form['format']
        return redirect(f'{season}/{year}/{format}')
    except:
        return error("Missing input in format")
    

    
@app.route('/404', methods=['GET'])
def error(error: str="Not Found"):
     return render_template("error.html", error=error)

