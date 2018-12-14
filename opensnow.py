import requests
import json
from bs4 import BeautifulSoup

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

def crawl_forecast(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    data = []
    table = soup.find('table', attrs={'class':'scrolling-forecast-table'})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])

    return data

def crawl_state(url):
    start_data = make_request_using_cache(url)
    state_soup = BeautifulSoup(start_data, 'html.parser')
    state_name = state_soup.find(class_='title').get_text()
    state_name_table = state_soup.find(class_='location-names-table')
    state_names = state_name_table.find_all(class_='name')
    resort_dict = {}
    for c in state_names:
        resort_url = 'https://opensnow.com' + c.find('a')['href']
        resort_name = c.find('a').get_text()
        resort_dict[resort_name] = {
            'URL': resort_url, 'Snowfall': [], 'State': ''}
        # resort_dict[resort_name] = {
        #     'URL': resort_url, 'Base': '--', 'Snowfall': [], 'State': ''}
    state_resort_snow_table = state_soup.find(
        class_='scrolling-forecast-table')
    dates = []
    for c in state_resort_snow_table.find(class_='fdate-row'):
        try:
            dates.append(c.get_text())
        except:
            continue
    resort_total_snowfall = []
    for c in state_resort_snow_table.find_all('tr')[2:]:
        individual_resort_snowfall = []
        for d in c:
            try:
                individual_resort_snowfall.append(d.get_text())
            except:
                continue
        resort_total_snowfall.append(individual_resort_snowfall)
    count = 0
    for c in resort_dict.items():
        c[1]['State'] = state_name
    for c in resort_dict.items():
        c[1]['Snowfall'] = resort_total_snowfall[count]
        count += 1

    # Crawl for forecast
    forecast = crawl_forecast(url+'/reports')
    for v, f in zip(resort_dict.values(),forecast):
        try:
            v['Base'] = int(f[3].strip('"'))
        except:
            v['Base'] = float('NaN')

    return (dates, resort_dict, state_name)

def crawl_main():
    pre_url = 'https://opensnow.com'
    start_url = 'https://opensnow.com/forecasts'
    cache_data_start = make_request_using_cache(start_url)
    start_soup = BeautifulSoup(cache_data_start, 'html.parser')
    table_data = start_soup.find(class_='col-md-8')
    table_data2 = table_data.find(class_='forecast-col')
    #count = 0
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


# print(crawl_state('https://opensnow.com/state/CO'))
