from bs4 import BeautifulSoup
import requests
import json

def make_request_using_cache(url):
    try:
        cache_file = open('cache-skiresortinfo.json', 'r')
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
        fw1 = open('cache-skiresortinfo.json', 'w')
        fw1.write(dumped_json_cache)
        fw1.close()
    return CACHE_DICTION[unique_ident]

def crawl_resort(url, resort_info):
    resort_data = make_request_using_cache(url)
    resort_soup = BeautifulSoup(resort_data, 'html.parser')
    name = resort_soup.find(class_='fn').get_text().split('Ski resort')[1].strip()
    state_search1 = resort_soup.find_all(class_='with-drop')
    state = state_search1[3].find(itemprop='name').get_text()
    slope_percentage = resort_soup.find(class_='detail-links link-img shaded no-pad-bottom chart')
    trail_info = []
    for c in slope_percentage.find(class_='run-table'):
        try:
            trail_info.append(c.get_text())
        except:
            continue
    resort_info[name] = [state, trail_info]
    # print((name, state))
    return resort_info

# crawl_resort('http://www.skiresort.info/ski-resort/vail/')

def crawl_US(url, resort_info):
    start_data = make_request_using_cache(url)
    start_soup = BeautifulSoup(start_data, 'html.parser')
    country_list = start_soup.find(id='resortList')
    count = 0
    for c in country_list:
        try:
            individ_url = c.find('a')['href']
            resort_info_final = crawl_resort(individ_url, resort_info)
        except:
            continue
    return resort_info_final
def main():
    count = 1
    resort_info = {}
    for c in range(4):
        url = 'http://www.skiresort.info/ski-resorts/usa/page/{}/'.format(count)
        resort_info_final = crawl_US(url, resort_info)
        count +=1
    count = 1
    for c in range(3):
        url = 'http://www.skiresort.info/ski-resorts/canada/page/{}/'.format(count)
        resort_info_final = crawl_US(url, resort_info)
        count +=1
    return(resort_info_final)

# main()
