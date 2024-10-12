from flask import Flask, render_template, redirect, jsonify, request, url_for, abort
from graph import cache
import graph


app = Flask(__name__)

cache.init_app(app) # initialize cache in app


@app.route('/')
def index():
    return redirect("/anime")
        

@app.route('/seasons')
def seasons():
    today = graph.get_date()
    return redirect(f'/{today.get("season")}/{today.get("year")}/TV')

@app.route('/anime', methods=['GET'])
def anime():
    graph.time.sleep(0.3)
    title = request.args.get('title') or None
    genre = request.args.get('selectgenre') or None
    page = request.args.get('page', default=1, type=int)
    format = request.args.get('formatsearch') or None
    sort = request.args.get('sort') or 'TRENDING_DESC'

    data = graph.get_anime_search(title, genre, sort, format, page)
    
     # Construct the URL dynamically based on the parameters with values
    url_params = {}
    if title:
        url_params['title'] = title
    if genre:
        url_params['selectgenre'] = genre
    if sort:
        url_params['sort'] = sort
    if format:
        url_params['format'] = format

     # Build the URL query string
    url_query_string = '&'.join([f"{key}={value}" for key, value in url_params.items()])
    url = f"/anime?{url_query_string}" if url_query_string else "/anime"

    prev_page_url = url_for('anime', title=title, selectgenre=genre, sort=sort, format=format, page=page-1) if page > 1 else None
    next_page_url = url_for('anime', title=title, selectgenre=genre, sort=sort, format=format, page=page+1) if data['page_info']['hasNextPage'] else None
    
    return render_template('anime.html', title="Search", data=data, url_params=url_params, prev_page_url=prev_page_url, next_page_url=next_page_url, url=url)

@app.route('/anime/<int:id>', methods=['GET'])
def gotoanime(id: int):
    data = graph.get_anime_info(id)
    if data is None:
        return render_template('error.html', error = "Anime not found")
    else:
        banner = data['bannerImage']
    
        return render_template('animeinfo.html', title="Anime", data=data, banner=banner)

@app.route('/<season>/<int:year>/', methods=['GET'])
@app.route('/<season>/<int:year>/<format>', methods=['GET'])
@app.route('/<season>/<int:year>/<format>/<int:page>', methods=['GET'])
def anime_season(season, year, format='TV', page=0):
    form_data = {
        "season": season,
        "year": year,
        "format": format
    }
    SEASONS = ['WINTER', 'SPRING', 'SUMMER', 'FALL']
    FORMATS = ['TV', 'MOVIE', 'OVA', 'TV_SHORT', 'ONA', 'SPECIAL']
    if form_data["season"].upper() not in SEASONS:
        abort(404, description="Invalid season")
    if form_data["format"].upper() not in FORMATS:
        abort(404, description="Invalid format")
    date = graph.get_date()
    if page is None:
        print('page is none')
        return redirect(f'/{season}/{year}/{format}/1')
    cache_key = f"{season.lower()}-{year}-{format}-{page}"
    print(cache_key)
    cached_data = cache.get(cache_key)
    title = f'{season.capitalize()} {year}'
    if cached_data:
        print("CACHED!")
        return render_template('season.html', title=title, data=cached_data, form_data=form_data, seasons=SEASONS, formats=FORMATS, date=date)

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
    return render_template('season.html',title=title, data=season_data, form_data=form_data, seasons=SEASONS, formats=FORMATS, date=date)

@app.route('/gotoseason', methods=['POST'])
def gotoseason():
    try:
        season = request.form['season']
        year = request.form['yearint']
        format = request.form['format']
        return redirect(f'{season}/{year}/{format}')
    except:
        return  404  #fix
    
@app.route ('/schedule', methods=['GET'])
def schedule():
        return render_template('schedule.html')
    
@app.route("/process_local_storage", methods=['POST'])
def process_local_storage():
    # Handle POST request
    data = request.get_json()
    anime_ids = data.get('animeIds', [])
    anime_list_data = graph.getAnimesInSchedule(anime_ids)

    processed_anime_data = graph.add_datetime_anime(anime_list_data['Page']['media'])

    return jsonify({
        'received_anime_ids': anime_ids,
        'anime_data': processed_anime_data,
        'message': 'Data received and processed successfully!'
    })

@app.route ('/about', methods=['GET'])
def about():
        return render_template('about.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', error= "NOT FOUND "), 404
