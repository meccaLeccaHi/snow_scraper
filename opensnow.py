import requests
import json
from bs4 import BeautifulSoup

'''
def make_request_using_cache(url):
    try:
        cache_file = open('cache-opensnow.json', 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

    unique_ident = url
    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]
    else:
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw1 = open('cache-opensnow.json', 'w')
        fw1.write(dumped_json_cache)
        fw1.close()
        return CACHE_DICTION[unique_ident]
'''

def crawl_state(url):
    '''
    Scrape state page
    Usage: >>> crawl_state('https://opensnow.com/state/CO')
    '''
    # start_data = make_request_using_cache(url)
    resp = requests.get(url)
    start_data = resp.text
    state_soup = BeautifulSoup(start_data, 'html.parser')
    state_name = state_soup.find(class_='title').get_text()
    state_name_table = state_soup.find(class_='location-names-table')
    state_names = state_name_table.find_all(class_='name')
    
    # Use 2 dictionaries to contain our results:
    # 1. Resort dictionary (resort_dict)
    resort_dict = {}
    for c in state_names:
        resort_url = c.find('a')['href']
        resort_name = c.find('a').get_text()
        resort_dict[resort_name] = {
            'URL': 'https://opensnow.com' + resort_url, 'Snowfall': [], 'State': ''}
    state_resort_snow_table = state_soup.find(
        class_='scrolling-forecast-table')
    # 2. Dates dictionary (dates)
    dates = []
    for c in state_resort_snow_table.find(class_='fdate-row'):
        try:
            dates.append(c.get_text())
        except:
            continue
    
    # Scrape forecasted snowfall from page
    resort_total_snowfall = []
    for c in state_resort_snow_table.find_all('tr')[2:]:
        individual_resort_snowfall = []
        for d in c:
            try:
                individual_resort_snowfall.append(d.get_text())
            except:
                continue
        resort_total_snowfall.append(individual_resort_snowfall)
    
    # Refine result dicts
    count = 0
    for c in resort_dict.items():
        c[1]['State'] = state_name
    for c in resort_dict.items():
        c[1]['Snowfall'] = resort_total_snowfall[count]
        count += 1
    return (dates, resort_dict, state_name)


def crawl_main():
    pre_url = 'https://opensnow.com'
    start_url = 'https://opensnow.com/forecasts'
    resp = requests.get(start_url)
    cache_data_start = resp.text
    #cache_data_start = make_request_using_cache(start_url)
    start_soup = BeautifulSoup(cache_data_start, 'html.parser')
    table_data = start_soup.find(class_='col-md-8')
    table_data2 = table_data.find(class_='forecast-col')
    count = 0
    data = []
    for c in table_data2.find_all('a'):
        try:
            end_url = c['href']
            if '-' in end_url:
                break
            elif 'region' not in end_url:
                crawl_state_data = crawl_state(pre_url + end_url)
                data.append(crawl_state_data)
            elif end_url == '/state/WY':
                break
        except:
            continue
    return data