import secrets
import requests
import json


def make_request_using_cache(url, params, headers, unique_ident):
    try:
        cache_file = open('cache-yelp.json', 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

    unique_ident = unique_ident
    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]
    else:
        resp = requests.get(url, params=params, headers=headers)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw1 = open('cache-yelp.json', 'w')
        fw1.write(dumped_json_cache)
        fw1.close()
    return CACHE_DICTION[unique_ident]

def yelp_individual_request(term, lat, long):
    headers = {'Authorization': 'Bearer ' + secrets.yelp_api_key}
    params = {}
    params['limit'] = 1
    params['category'] = 'skiresorts'
    params['term'] = term
    params['location'] = ('{}, {}'.format(lat, long))
    unique_ident = '{}-{}-{}'.format(term, lat, long)
    url = 'https://api.yelp.com/v3/businesses/search'
    response = make_request_using_cache(url, params, headers, unique_ident)
    data = json.loads(response)
    rating = 'No Rating'
    for c in data['businesses']:
        rating = c['rating']
    return(term, rating)

# yelp_individual_request('Beaver Creek', '39.6019', '-106.5167')
