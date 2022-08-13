import requests
import pprint
import json
import itertools


streaming_links = set()

api_key = "uzu13kT8WvZRP6gZBExRhs183M2g7tiGdL74Rn57"



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
        response = requests.get(url0)
        if not check_response(response):
                    exit(2)

        else:
            show = response.json()
            movie_id = show["title_results"][0]["id"]
            print(f'Movie ID retrieved:{movie_id}')
            return movie_id

    
    def get_links(d, l):
        if len(l) == 1: return d[l[0]]
        return get_links(d[l[0]], l[1:])
    
    maplist1 = ["sources"]
    
    def get_show_info(url1):
        response = requests.get(url1)
        listed = []
        if not check_response(response):
            exit(2)

        else:
            show = json.loads(response.text)
            print("everything")
            t = show['id']
            listed.append(t)
            b = show['title']
            listed.append(b)
            c = show['year']
            listed.append(c)
            d = show['genre_names']
            dd = "".join(d)
            listed.append(dd)
            e = show['user_rating']
            listed.append(e)
            f = show['poster']
            listed.append(f)
            ff = show['original_language']
            listed.append(ff)
            g = show['trailer']
            listed.append(g)
        print(listed)
        a = get_links(show, maplist1)
        for d in a:
            streaming_links.add(d['web_url'])   
        print(streaming_links)
        return listed
            

except IndexError:
    print("The movie you are looking for is not in the database. Please check your entry or search for another show")

except TypeError:
    pass
