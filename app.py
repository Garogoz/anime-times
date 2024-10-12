from flask import Flask, render_template, redirect, jsonify, request, url_for
from graph import cache
import graph




app = Flask(__name__)

cache.init_app(app) # initialize cache in app


@app.route('/')
def index():
    return render_template("index.html", title="AnimeTiming")
        #return redirect('/winter/2024')


@app.route('/seasons')
def seasons():
    return redirect(f'/winter/2024/TV')

@app.route('/anime', methods=['GET'])
def anime():
    data = graph.get_anime(request.args.get('title'))
    
    return render_template('anime.html', title="Search", data=data)

@app.route('/anime/<int:id>', methods=['GET'])
def gotoanime(id: int):
    
    
    return render_template('animeinfo.html', title="Anime")


@app.route('/<season>/<int:year>/<format>', methods=['GET'])
@app.route('/<season>/<int:year>/<format>/<int:page>', methods=['GET'])
def anime_season(season, year, format="TV",  page=0):
        if page is None:
            return redirect(f'/{season}/{year}/{format}/1')
        cache_key = f"{season.lower()}-{year}-{format}-{page}"
        cached_data = cache.get(cache_key)
        title = f'{season.capitalize()} {year}'
        if cached_data is not None:
            print("CACHED!")
            return render_template('season.html', title=title, data=cached_data)

        # If data is not cached, retrieve it and cache it
        print("NOT CACHED!!!")
        season_data = graph.get_anime_season(season, year, page, format)
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
    

    

def error(error: str="Not specified"):
     return render_template("error.html", error=error)

