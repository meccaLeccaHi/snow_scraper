region_options = {
    'Mid-west': ['Illinois', 'Indiana', 'Michigan', 'Minnesota', 'Ohio',
    'Wisconsin', 'Iowa', 'Kansas', 'Missouri', 'Nebraska', 'Oklahoma',
    'North Dakota', 'South Dakota'],
    'New England': ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire',
    'Rhode Island', 'Vermont', 'New Jersey', 'New York', 'Delaware',
    'District of Columbia', 'Maryland', 'Pennsylvania'],
    'South': ['Alabama', 'Florida', 'Georgia', 'Kentucky', 'Mississippi',
    'North Carolina', 'South Carolina', 'Tennessee', 'Virginia',
    'West Virginia', 'Puerto Rico', 'US Virgin Islands', 'Arkansas',
    'Louisiana', 'Texas'],
    'Rockies': ['New Mexico', 'Colorado', 'Montana', 'Utah', 'Wyoming', 'Idaho'],
    'West Coast': ['Arizona', 'California', 'Hawaii', 'Nevada',
    'American Samoa', 'Guam', 'Northern Mariana Islands', 'Alaska', 'Oregon',
    'Washington'],
    'Canadian West': ['British Columbia', 'Alberta', 'Saskatchewan', 'Yukon',
    'Northwest Territories'],
    'Canadian East': ['Manitoba', 'Ontario', 'Quebec', 'New Brunswick',
    'Nova Scotia', 'Prince Edward Island', 'Newfoundland and Labrador',
    'Nunavut'],
    'All': {}
}

import requests
import secrets
import json

for region in region_options:

    region_cache = {}

    for state in region_options[region]:

        google_geocode_url= 'https://maps.googleapis.com/maps/api/geocode/json?'
        params_geocode = {'address': (state),
                         'key':secrets.google_places_key}
        req = requests.Request(method = 'GET', url = google_geocode_url,
                         params = sorted(params_geocode.items()))
        prepped = req.prepare()
        response = requests.Session().send(prepped)
        region_cache[state] = json.loads(response.text)

    region_options[region] = region_cache
    region_options['All'] =  {**region_options['All'], **region_cache}

# Write to json file
with open('cache-geo.json', 'w') as outfile:
    json.dump(region_options, outfile)

print('All done :)')
