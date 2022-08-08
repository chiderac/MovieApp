import requests
import pprint
#from movieapp import converted_search

api_key = "uzu13kT8WvZRP6gZBExRhs183M2g7tiGdL74Rn57"

url0 = f"https://api.watchmode.com/v1/search/?apiKey={api_key}&search_field=name&search_value={converted_search}"

# return movie_id
def check_response(response):
    if response.status_code < 200 or response.status_code >= 300:
        print('API error')
        print(f'Response code: {response.status_code}')
        if response.status_code == 402:
            print('New API Key Required')
        return False
    else:
        print('API connection successful')
        # print(f'API response code: {response.status_code}')
        return True
        
try:
    def get_movie_id(url0):
        response = requests.get()
        if not check_response(response):
                    exit(2)

        else:
            show = response.json()
            movie_id = show["title_results"][0]["id"]
            print(f'Movie ID retrieved:{movie_id}')
            return movie_id

    movie_id = get_movie_id(url0)
    streaming_links = []
    #url1 = f"https://api.watchmode.com/v1/title/{movie_id}/details/?apiKey={api_key}&append_to_response=sources"

    def get_show_info(url1):
        response = requests.get()

        if not check_response(response):
            exit(2)

        else:
            show = response.json()
            
    def get_links(d, l):
        if len(l) == 1: return d[l[0]]
        return get_links(d[l[0]], l[1:])

    maplist1 = ["sources"]
    a = get_links(show, maplist1)
    for d in a:
        streaming_links.append(d['web_url'])

    class Show:
        def __init__(self, id=movie_id, title="", type="", year=0, genre="", user_rating=0, poster="", trailer=""):
                self.id = id
                self.title = title
                self.type = type
                self.year = year
                self.genre = genre
                self.user_rating = user_rating
                self.poster = poster
                self.trailer = trailer
                # self.sources = sources (streaming_links)

        def __str__(self):
            response = requests.get(url1)
            show = response.json()
            print(f"Your movie results are:"
                f"\nTitle: {show['title']}"
                f"\nType: {show['type']}"
                f"\nYear: {show['year']}"
                f"\nGenre: {show['genre_names']}"
                f"\nUser Rating: {show['user_rating']}"
                f"\nPoster URL: {show['poster']}"
                f"\nTrailer URL: {show['trailer']}"
                f"\nStreaming Links:")
            # {streaming_links}")
            pp = pprint.PrettyPrinter(indent=1)
            pp.pprint(streaming_links)

    user_results = Show(get_show_info())
    print(user_results)

except IndexError:
    print("The movie you are looking for is not in the database. Please check your entry or search for another show")

except TypeError:
    pass
#A type error is appearing and I can't find the problem. Passing until solution found