import requests
import json
import secrets

try:
	cache_file1 = open('cache-google.json', 'r')
	cache_contents1 = cache_file1.read()
	CACHE_DICTION1 = json.loads(cache_contents1)
	cache_file1.close()
except:
	CACHE_DICTION1 = {}


def make_request_using_cache_Google(url, params):
	req = requests.Request(method = 'GET', url = url,
							params = sorted(params.items()))
	prepped = req.prepare()
	unique_ident = prepped.url
	if unique_ident not in CACHE_DICTION1:
		response = requests.Session().send(prepped)
		CACHE_DICTION1[unique_ident] = {'data': response.text}
		cache_file = open('cache-google.json', 'w')
		cache_file.write(json.dumps(CACHE_DICTION1))
		cache_file.close()
		return CACHE_DICTION1[unique_ident]['data']
	else:
		return CACHE_DICTION1[unique_ident]['data']

def get_lat_and_long(ski_name, ski_state):
	google_geocode_url= 'https://maps.googleapis.com/maps/api/geocode/json?'
	params_geocode = {'address': (ski_name+' '+ski_state),
						'key':secrets.google_places_key,}
	geocode_data = make_request_using_cache_Google(google_geocode_url,
													params_geocode)
	geocoding_results = json.loads(geocode_data)
	if geocoding_results['status'] == 'OK':
		information = geocoding_results['results'][0]
		lattitude = information['geometry']['location']['lat']
		longitude = information['geometry']['location']['lng']
		return(lattitude, longitude)
	else:
		print('Error')
		return('Error', 'Error')



# print(get_lat_and_long('Beaver Creek', 'Colorado'))
