from flask import Flask, render_template, redirect, jsonify
from graph import cache
import graph




app = Flask(__name__)

cache.init_app(app) # initialize cache in app


@app.route('/')
def index():
        return redirect('/winter/2024')

@app.route('/<season>/<int:year>')
def anime_season(season, year):
    cache_key = f"{season.lower()}-{year}"
    cached_data = cache.get(cache_key)
    title = f'{season.capitalize()} {year}'
    if cached_data is not None:
        print("CACHED!")
        return render_template('season.html', data=cached_data)

    # If data is not cached, retrieve it and cache it
    print("NOT CACHED!!!")
    season_data = graph.get_anime_season(season, year)
    cache.set(cache_key, season_data)
    return render_template('season.html',title=title, data=season_data)





