import requests
import json
from flask_caching import Cache
from functools import wraps

# Configure the cache
cache = Cache(config={'CACHE_TYPE': 'simple'})


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
    
# handle errors
def handle_error(status_code: int):
    print(f"ERROR retrieving data. Status Code: {status_code}")


def get_anime_season_data(variables):
    url = 'https://graphql.anilist.co'
    anime_data = []
    # Here we define our query as a multi-line string
    query = '''
    query ($page: Int, $season: MediaSeason, $seasonYear: Int, $format: MediaFormat){
      Page(perPage: 50, page: $page) {
        pageInfo {
          total
          perPage
          currentPage
          lastPage
          hasNextPage
        }
        media(season: $season, seasonYear: $seasonYear, format: $format) {
          id
          title {
            romaji
            english
          }
          startDate {
            year
            month
            day
          }
          episodes
          season
          seasonYear
          type
          duration
          genres
          averageScore
          popularity
          coverImage {
            extraLarge
            large
            medium
            color
          }
          bannerImage
          description
          
        }
      }
    }


    '''

  # Make the HTTP Api request
    while True:
        response = requests.post(url, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            data = response.json()['data']['Page']['media']
            for anime in data:
                anime_data.append(anime)
            variables['page'] += 1
            if response.json()['data']['Page']['pageInfo']['hasNextPage'] is False:
                break
        else:
            handle_error(response.status_code)
        break
    return anime_data

def cached_anime_season(timeout=86400):
    def decorator(func):
        @wraps(func)
        def wrapper(season, year):
            variables = {
                'page': 1,
                'seasonYear': year,
                'season': season.upper(),
                'format': 'TV'
            }
            cache_key = f'{season.lower()}-{year}'
            return func(variables, cache_key, timeout)
        return wrapper
    return decorator

@cached_anime_season()
def get_anime_season(season_variables, cache_key, timeout):
    return get_anime_season_data(season_variables)
