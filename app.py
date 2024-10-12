from flask import Flask, render_template, redirect, jsonify, request, url_for
from graph import cache
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
    graph.time.sleep(0.3)
    title = request.args.get('title')
    genre = request.args.get('selectgenre')
    page = request.args.get('page', default=1, type=int)
    
    if not title and not genre:
        # get all animes and sort by popularity
        data = graph.get_anime_by_title(None, None, page)
        print('1 working')
    elif title and not genre:
        data = graph.get_anime_by_title(title, None, page)
        print('2 working')
    elif not title and genre:
        # get all animes by genre and sort by popularity
        data = graph.get_anime_by_genre(genre, page)
        print('3 working')
    elif title and genre:
        data = graph.get_anime_by_title(title, genre, page)
        print('4 working')
    
     # Construct the URL dynamically based on the parameters with values
    url_params = {}
    if title:
        url_params['title'] = title
    if genre:
        url_params['selectgenre'] = genre

     # Build the URL query string
    url_query_string = '&'.join([f"{key}={value}" for key, value in url_params.items()])
    url = f"/anime?{url_query_string}" if url_query_string else "/anime"

    prev_page_url = url_for('anime', title=title, selectgenre=genre, page=page-1) if page > 1 else None
    next_page_url = url_for('anime', title=title, selectgenre=genre, page=page+1) if data['page_info']['hasNextPage'] else None
    
    return render_template('anime.html', title="Search", data=data, prev_page_url=prev_page_url, next_page_url=next_page_url, url=url)

@app.route('/anime/<int:id>', methods=['GET'])
def gotoanime(id: int):
    data = graph.get_anime_info(id)
    if data is None:
        return render_template('error.html', "Anime not found")
    else:
        banner = data['bannerImage']
    
        return render_template('animeinfo.html', title="Anime", data=data, banner=banner)


@app.route('/<season>/<int:year>/<format>', methods=['GET'])
@app.route('/<season>/<int:year>/<format>/<int:page>', methods=['GET'])
def anime_season(season, year, format='TV', page=0):
    form_data = {
        "season": season,
        "year": year,
        "format": format
    }
    SEASONS = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
    if page is None:
        print('page is none')
        return redirect(f'/{season}/{year}/{format}/1')
    cache_key = f"{season.lower()}-{year}-{format}-{page}"
    print(cache_key)
    cached_data = cache.get(cache_key)
    title = f'{season.capitalize()} {year}'
    if cached_data:
        print("CACHED!")
        return render_template('season.html', title=title, data=cached_data, form_data=form_data, seasons=SEASONS)

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
    return render_template('season.html',title=title, data=season_data, form_data=form_data)

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
