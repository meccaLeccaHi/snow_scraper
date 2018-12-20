import requests
import json
from bs4 import BeautifulSoup
import re
import datetime as dt
import json

base = 'https://opensnow.com'

def crawl_state(url=base+'/state/MT'):

    print("Crawling: {}".format(url))

    resp = requests.get(url)
    state_soup = BeautifulSoup(resp.text, 'html.parser')

    # Get state name
    state_name = state_soup.find(class_='title').get_text()
    print("Scraping 'State name': {}".format(state_name))

    # Select page region to use
    big_column = state_soup.find(class_='col-lg-8')

    # Get icon for each resort
    icon_scrape = big_column.find_all('img', {'class': 'location-icon'})
    icons = [img['src'] for img in icon_scrape]
    print("Scraping 'Icons': {}".format(icons))

    # Get url for each resort
    resorts_scrape = big_column.find_all('div', {'class': 'title-location'})
    resorts = [resort.getText() for resort in resorts_scrape]
    urls = [base+resort.a['href'] for resort in resorts_scrape]
    print("Scraping 'urls': {}".format(urls))

    # Get forecast for each resort
    def average_string(string_input):
        hi_low = [float(re.findall('\d+',i)[0]) for i in string_input.split('-')]
        return sum(hi_low)/2
    table_scrape = big_column.find_all('table', {'class': 'tiny-graph'})
    forecasts = []
    for table in table_scrape:
        forecast_vals = [average_string(val['value']) for val in table.find_all('span')]
        forecasts.append(forecast_vals)
    print("Scraping 'Forecasts': {}".format(forecasts))

    # Get forecast dates
    if table_scrape:
        dates_scrape = table_scrape[0].find_all('div', {'class': 'day'})
        date_nums = [int(date.getText().strip()) for date in dates_scrape][:5]

        yday = date_nums[0]-1
        dates = [item for item in date_nums for i in range(2)]
        if dt.datetime.now().hour>=12:
            dates = [yday]+dates
        else:
            dates = [yday,yday]+dates
    else:
        dates = []

    ## Insert test for equal length of dates and forecast_vals[0]

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
        else:
            terrain = []
        snowfall.append([terrain.find_all(class_="data-cell")[i].getText().strip() for i in range(len(terrain))])

    # Assemble resort variables into dictionary
    state_dict = {}
    for ind in range(len(resorts)):
        state_dict[resorts[ind]] = {
            'URL': urls[ind], 'Forecast': forecasts[ind], 'Dates': dates, 'Snowfall': snowfall[ind], 'Icon': icons[ind],
            'State': state_name}

    return state_dict

def crawl_main():
    base = 'https://opensnow.com'
    # Load state geo data
    with open('data/cache-geo.json') as json_data:
        region_options = json.load(json_data)

    # State/province loop
    data = []
    for region in region_options:
        for state in region_options[region]:
            abbrev = region_options[region][state]['results'][0]['address_components'][0]['short_name']
            url = base+'/state/'+abbrev
            data.append(crawl_state(url))
        break

    return data

# print(crawl_state('https://opensnow.com/state/CO'))
