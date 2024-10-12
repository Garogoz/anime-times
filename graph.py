import requests
import json
from flask_caching import Cache
from functools import wraps
import time

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

# Function to make GraphQL queries
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
    animes = data['Page']['media']
    genres = data['GenreCollection']
    for anime in animes: 
        anime_data.append(anime)
        
    info = {
	'anime_data': anime_data,
	'genres': genres
	}
    return info 
"""
def get_genres():
    query = '''
    query{
      GenreCollection
    }
'''
    data = make_graphql_query(query, None)
    return data
"""
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


def get_anime_by_title(search: str, genre: str = None, page: int = 1, perPage: int = 50):
    query = '''
	query ($id: Int, $page: Int, $perPage: Int, $search: String, $genre: String) {
		Page (page: $page, perPage: $perPage) {
			pageInfo {
				total
				currentPage
				lastPage
				hasNextPage
				perPage
			}
			media (id: $id, search: $search, genre: $genre, sort: POPULARITY_DESC) {
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
		GenreCollection
	}
	'''        
    variables = {
        'search': search,
        'genre': genre,
        "page": page,
        "perPage": perPage,
    }
    if genre is not None:
        variables['genre'] = genre

    data = make_graphql_query(query, variables)
    
    return struct_data_multiple(data)
    
def get_anime_by_genre(genre: str, page: int = 1, perPage: int = 50):
    query = '''
    query ($genre: String, $page: Int, $perPage: Int){
  	Page (page: $page, perPage: $perPage) {
		pageInfo {
          total
          currentPage
          lastPage
          hasNextPage
          perPage
			}
  
        media(genre: $genre, type: ANIME, sort: POPULARITY_DESC) {
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
      GenreCollection
      
}
    '''
    variables = {
        'genre': genre
	}
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
 
        