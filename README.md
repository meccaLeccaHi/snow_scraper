# snow_scraper
FreshyFinder: Illegitimate son of FreshyMap
- a Webscraping/Visualization Tool for Ski Bums

This software scrapes weather data from every resort in North America (provided by the good folks at [opensnow.com](https://opensnow.com)). It also provides a highly-interactive visualization tool, "FreshyFinder", to search the scraped snowfall data in anticipation of your next getaway. This app was initially an attempt to replace the late, great [FreshyMap.com](https://en.wikipedia.org/wiki/FreshyMap).

[INSERT SCREENSHOT]
[ADD HEROKU LINK HERE]

### Built With:
This app use a [Python client library](https://github.com/googlemaps/google-maps-services-python) for Google Maps API Web Services to look-up the lat. and long. of each resort. Fortunately, it's super easy to install, just run:
`$ pip install -U googlemaps`

The front end was made using [Plotly Dash](https://dash.plot.ly/). I relied on several sources of information including:
- Plotly Dash Tutorials by [Adriano M. Yoshino](https://github.com/amyoshino)
- As well as the highly-instructive [examples](https://dash.plot.ly/gallery) provided by Plotly itself.

### Keys
This app also uses [MapBox](https://www.mapbox.com/) for the map, which requires a user-specific [access token](https://www.mapbox.com/help/how-access-tokens-work/) to use. 
In addition, each Google Maps Web Service request requires an API key or client ID. API keys are freely available with a Google Account at https://developers.google.com/console. The type of API key you need is a *Server* key.
Both keys will need to be placed in a file called secrets.py, which is placed in `/snow_scraper`. It should be organized as follows (with the single quotes around the strings):

#### secrets.py
```
mapbox_key = 'API_KEY_HERE'
google_places_key = 'API_KEY_HERE'
```

### To run:
1. Install requirements:  
`$ pip install -r requirements.txt` (or see 'requirements' below)
1. Scrape 'opensnow.com':  
`$ python main_file.py`
1. Visualize via app:  
`$ python app.py`
1. Enjoy!

Dependencies:
```
pip install numpy
pip install pandas
pip install dash
pip install dash-html-components
pip install dash-core-components
pip install dash-table
pip install dash-table-experiments
pip install -U googlemaps
pip install beautifulsoup4
```
