import requests
import json
from flask_caching import Cache
from functools import wraps
import time
import bleach
from datetime import datetime

# List of allowed tags and attributes
allowed_tags = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul', 'p', 'br'
]
allowed_attributes = {
    'a': ['href', 'title'],
    'abbr': ['title'],
    'acronym': ['title']
}
#To avoid errors while rendering html due to bad tags
def sanitize_html(raw_data):
    clean_data = bleach.clean(raw_data, tags=allowed_tags, attributes=allowed_attributes)
    return clean_data

#get today's date
def get_date() -> dict:
    current_date = datetime.now()
    month = current_date.month
    if 3 <= month <= 5:
        season = 'spring'
    elif 6 <= month <= 8:
        season = 'summer'
    elif 9 <= month <= 11:
        season = 'autumn'
    else:
        season = 'winter'
    dict_date = {
        'year': current_date.year,
        'month': month,
        'day': current_date.day,
        'season': season
    }
    return dict_date
    
def create_datetime_dict(unix_timestamp):
    # Convert Unix timestamp to datetime object
    dt = datetime.fromtimestamp(unix_timestamp)
    
    # Create the dictionary with required fields
    datetime_dict = {
        'day': dt.day,
        'weekday': dt.strftime('%A'),  # Full weekday name
        'hour': dt.hour,
        'minutes': dt.minute
    }
    
    return datetime_dict

def add_datetime_anime(animelist :list):
    for anime in animelist:
            try:
                anime['datetime'] = create_datetime_dict(anime['nextAiringEpisode']['airingAt'])
            except Exception as e:
                print('error, ', e)
    return animelist
                        

# Configure the cache
cache = Cache(config={'CACHE_TYPE': 'simple'})

url = 'https://graphql.anilist.co'

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)



# handle errors
def handle_error(status_code: int, response_headers):
    if status_code == 429:
        print(f"ratelimiting, please try again after {response_headers['Retry-After']} segs")
    
    print(f"ERROR retrieving data. Status Code: {status_code}")


def make_graphql_query(query: str, variables: dict = None, max_retries: int = 3, retry_delay: int = 5):
    for attempt in range(max_retries): 
        try:
            response = requests.post(url, json={'query': query, 'variables': variables})
            response.raise_for_status()
            # If the request was successful, break out of the loop
            break
        except requests.HTTPError as e:
            if e.response.status_code == 500:
                print(f"Attempt {attempt+1}: Received 500 Internal Server Error. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            elif e.response.status_code == 429:  # Too Many Requests
              print("Rate limit exceeded. Waiting and retrying...")
              time.sleep(60)  # Wait for some time before retrying
              return make_graphql_query(query, variables)  # Retry the request
            else:
                # Handle other HTTP errors
                print(f"HTTP error {e.response.status_code}: {e.response.reason}")
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
    else:
        # If all retries fail, notify the user or handle the situation accordingly
        print("Maximum number of retries reached. Unable to complete the request.")
    return response.json()['data']

#struct information for querys with multiple results
def struct_data_multiple(data):
    if not data:
        return None
    anime_data = []
    page_info = data['Page']['pageInfo']
    animes = data['Page']['media']
    genres = data['GenreCollection']
    
    for anime in animes: 
        try:
          if anime['description']:
              anime['description'] = sanitize_html(anime['description'])
        except KeyError:
            pass
        except Exception as e:
            print("Something went wrong with the description sanitazer", e)
        
        anime_data.append(anime)
        
    info = {
  'page_info': page_info,
	'anime_data': anime_data,
	'genres': genres
	}
    return info 

def get_anime_season_data(variables: dict):
      
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
          status
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
      GenreCollection
    }

    '''
    data = make_graphql_query(query, variables)

    return struct_data_multiple(data)
    

def cached_anime_season(timeout=86400):
    def decorator(func):
        @wraps(func)
        def wrapper(variables):
            
            cache_key = f"{ variables['season'].lower() }-{variables['seasonYear']}-{variables['format']}-{variables['page']}"
            return func(variables, cache_key, timeout)
        return wrapper
    return decorator

@cached_anime_season()
def get_anime_season(variables: dict, cache_key, timeout):
    return get_anime_season_data(variables)


def get_anime_search(search: str = None, genre: str = None, sort: str = None, format: str = None, page: int = 1, perPage: int = 25):
    query = '''
	query ($id: Int, $page: Int, $perPage: Int, $search: String, $genre: String, $format: MediaFormat, $sort: [MediaSort]) {
		Page (page: $page, perPage: $perPage) {
			pageInfo {
				total
				currentPage
				lastPage
				hasNextPage
				perPage
			}
			media (id: $id, search: $search, genre: $genre, format: $format, sort: $sort) {
				id
				title {
					romaji
					english
				}
				seasonYear
        popularity
        averageScore
				episodes
				type
        format
        status
				coverImage {
				large
			}
			}
		}
		GenreCollection
	}
	'''        
    variables = {
        'search': search,
        'genre': genre,
        "page": page,
        "perPage": perPage,
        'sort': sort,
    }
    if format:
        variables['format'] = format

    data = make_graphql_query(query, variables)
    
    return struct_data_multiple(data)


    
def get_anime_info(id: int):
    query = '''
    query ($id: Int){
        Media(id: $id) {
          id
          title {
            romaji
            english
            native
          }
          startDate {
            year
            month
            day
          }
          endDate {
            year
            month
            day
          }
          episodes
          chapters
          season
          seasonYear
          format
          type
          duration
          genres
          averageScore
          status
          popularity
          coverImage {
            extraLarge
            large
            medium
            color
          }
          bannerImage
          description
          source
          relations {
          edges {
            node {
              id
              coverImage{
                medium
              }
              title {
                romaji
              }
              format
              episodes
              chapters
            }
          }
        }
          studios {
          edges {
            id
            node{
              name
              isAnimationStudio
            }
          }
        }
      }
    }
    '''
    variables = {
        'id': id,
    }

    data = make_graphql_query(query, variables)

    return data['Media']
 
def getAnimesInSchedule(idlist: list):
    
    query = '''
    query ($ids: [Int]) {
      Page(page: 1, perPage: 50) {
        media(id_in: $ids) {
          id
          title {
            romaji
            english
          }
          coverImage {
            large
          }
          nextAiringEpisode {
            id
            episode
            airingAt
          }
        }
      }
    }
    '''
    variables = {
        'ids': idlist
    }
    
    data = make_graphql_query(query, variables)

    return data


def getAnimeForSchedule(variables: dict):
      
    # Here we define our query as a multi-line string
    query = '''
    query($search: String){
    Page(page: 1, perPage: 5) {
      pageInfo {
            total
            perPage
            currentPage
            lastPage
            hasNextPage
          }
      media(search: $search, type: ANIME) {
        id
        title{
          romaji
        }
        type
        format
          coverImage {
          medium
        }
        averageScore
        episodes
    }
  }
}
    '''
    data = make_graphql_query(query, variables)

    return data