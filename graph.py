import requests
import json
from flask_caching import Cache
from functools import wraps

# Configure the cache
cache = Cache(config={'CACHE_TYPE': 'simple'})

url = 'https://graphql.anilist.co'

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
    
# handle errors
def handle_error(status_code: int):
    print(f"ERROR retrieving data. Status Code: {status_code}")


def get_anime_season_data(variables):
    
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
        media(season: $season, seasonYear: $seasonYear, format: $format, sort: POPULARITY_DESC) {
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
        def wrapper(season, year, page, format="TV"):
            variables = {
                'page': page,
                'seasonYear': year,
                'season': season.upper(),
                'format': format
            }
            cache_key = f'{season.lower()}-{year}'
            return func(variables, cache_key, timeout)
        return wrapper
    return decorator

@cached_anime_season()
def get_anime_season(season_variables, cache_key, timeout):
    return get_anime_season_data(season_variables)

def get_anime(search: str, page: int = 1, perPage: int = 50):
    query = '''
query ($id: Int, $page: Int, $perPage: Int, $search: String) {
    Page (page: $page, perPage: $perPage) {
        pageInfo {
            total
            currentPage
            lastPage
            hasNextPage
            perPage
        }
        media (id: $id, search: $search, sort: POPULARITY_DESC) {
            id
            title {
                romaji
                english
            }
            seasonYear
            episodes
            type
            coverImage {
            extraLarge
            large
            medium
            color
          }
        }
    }
}
'''
    variables = {
        'search': search,
        "page": page,
        "perPage": perPage
    }
    anime_data = []

    response = requests.post(url, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        data = response.json()['data']['Page']['media']
        for anime in data: 
            anime_data.append(anime)
        return anime_data
    else:
        print("not 200")

def get_anime_info(id: int):
    query = '''
    query ($id: Int){
        Media(id: $id) {
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
    variables = {
        'id': id,
    }

    response = requests.post(url, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        data = response.json()['data']['Media']
        return data
    else:
        print("f")