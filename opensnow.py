import requests
import json
from bs4 import BeautifulSoup
import re
import datetime as dt
import json
import sys

base = 'https://opensnow.com'

def average_string(string_input):
    hi_low = [float(re.findall('\d+',i)[0]) for i in string_input.split('-')]
    return sum(hi_low)/2

def crawl_state(url=base+'/state/MT'):

    print("Crawling: {}".format(url))

    state_dict = {}
    resp = requests.get(url)
    state_soup = BeautifulSoup(resp.text, 'html.parser')

    title = state_soup.find("meta",  property="og:title")
    if title['content'].strip()=='Page Not Found':
        # No page for you
        print('No page for',url)
    else:
        # Get state name
        state_name = state_soup.find('h1', {'class': 'title'}).get_text()
        print("Scraping 'State name': {}".format(state_name))

        # Select page region to use
        big_column = state_soup.find(class_='col-lg-8')

        # Get icon for each resort
        icon_scrape = big_column.find_all('img', {'class': 'location-icon'})
        icons = [base+img['src'] for img in icon_scrape]
        print("Scraping 'Icons': {}".format(icons))

        # Get url for each resort
        resorts_scrape = big_column.find_all('div', {'class': 'title-location'})
        resorts = [resort.getText() for resort in resorts_scrape]
        urls = [base+resort.a['href'] for resort in resorts_scrape]
        print("Scraping 'urls': {}".format(urls))

        # Scrape table
        table_scrape = big_column.find_all('table', {'class': 'tiny-graph'})

        # Get forecast dates
        if table_scrape:
            dates_scrape = table_scrape[0].find_all('span', {'class': 'day'})
            date_nums = [int(date.getText().strip()) for date in dates_scrape]
            dates = [item for item in date_nums for i in range(2)]

        else:
            print('No dates found for {}'.format(state_name))
            dates = []

        # Get forecast for each resort
        forecasts = []
        for table in table_scrape:
            daily_snow = table.find_all('span')
            forecast_n = [average_string(val['value']) for val in daily_snow if val.has_attr('value')]
            if len(forecast_n)==(len(dates)+1):
                forecast_n = forecast_n[-len(dates):]
            forecasts.append(forecast_n)

        print("Scraping 'Forecasts': {}".format(forecasts))

        if forecasts:
            # Test for equivalence of length of 'dates' and 'forecasts'
            if len(dates)!=len(forecasts[0]):
                warn_string = 'Length of dates ({0}) and number of forecasts ({1}) do not match.'
                warn_string = warn_string.format(len(dates),len(forecasts[0]))
                print(warn_string)
                sys.quit()
        else:
            print('No forecasts found for {}'.format(state_name))
            dates = []

        # Get base (inches) for each resort
        snowfall = []
        for link in urls:
            print("Scraping 'Snowfall' from: {}".format(link))
            resp = requests.get(link)
            resort_soup = BeautifulSoup(resp.text, 'html.parser')
            terrain_position = [i for i, x in enumerate(resort_soup.find_all('h3', {'class': 'sidebar-title'})) \
                          if x.getText()=='Terrain']

            if any(terrain_position):
                terrain = resort_soup.find_all(class_='data-container')[terrain_position[0]]
                data_out = terrain.find_all(class_="data-cell")
                data_out = [data_out[i].getText().strip() for i in range(len(data_out))]
            else:
                data_out = []

            snowfall.append(data_out)

        # Assemble resort variables into dictionary
        for ind in range(len(resorts)):
            state_dict[resorts[ind]] = {
                'URL': urls[ind], 'Forecast': forecasts[ind], 'Dates': dates, 'Snowfall': snowfall[ind], 'Icon': icons[ind],
                'State': state_name}

    return state_dict

def crawl_main():
    # Load state geo data
    with open('data/cache-geo.json') as json_data:
        region_options = json.load(json_data)

    # State/province loop
    data = []
    for state in region_options['All']:
        abbrev = region_options['All'][state]['results'][0]['address_components'][0]['short_name']
        url = base+'/state/'+abbrev
        data.append(crawl_state(url))
    return data

# print(crawl_state('https://opensnow.com/state/CO'))
