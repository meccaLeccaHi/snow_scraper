import sqlite3
import google_api
import yelp
import opensnow

def init_db():
    conn = sqlite3.connect('snowfall.db')
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'Mountain_Snow';
    '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        DROP TABLE IF EXISTS 'Mountain_Locations';
    '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        DROP TABLE IF EXISTS 'Yelp';
    '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE 'Mountain_Snow' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'MountainName' TEXT NOT NULL,
            'State' TEXT NOT NULL,
            'URL' TEXT NOT NULL,
            'day1M' TEXT NOT NULL,
            'day1N' TEXT NOT NULL,
            'day2M' TEXT NOT NULL,
            'day2N' TEXT NOT NULL,
            'day3M' TEXT NOT NULL,
            'day3N' TEXT NOT NULL,
            'day4M' TEXT NOT NULL,
            'day4N' TEXT NOT NULL,
            'day5M' TEXT NOT NULL,
            'day5N' TEXT NOT NULL,
            'TOTAL' INTEGER NOT NULL
        );
    '''
    cur.execute(statement)
    statement = '''
        CREATE TABLE 'Mountain_Locations' (
            'Id' INTEGER,
            'Name' TEXT NOT NULL,
            'State' TEXT NOT NULL,
            'Latitude' INTEGER NOT NULL,
            'Longitude' INTEGER NOT NULL
        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Yelp' (
            'Id' INTEGER,
            'Name' TEXT NOT NULL,
            'State' TEXT NOT NULL,
            'Rating' TEXT NOT NULL
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()

def avg_snow(inches):
    a = inches.split('"')[0]
    if '-' in a:
        num1 = float(a.split('-')[0])
        num2 = float(a.split('-')[1])
        return float((num1+num2)/2)
    else:
        return float(a)

def insert_snow_data():
    conn = sqlite3.connect('snowfall.db')
    cur = conn.cursor()

    data = opensnow.crawl_main()

    for c in data:
        for d in c[1].items():
            name = d[0]
            snowfall = d[1]['Snowfall']
            url = d[1]['URL']
            state_name = d[1]['State']
            d1m = snowfall[0]
            d1n = snowfall[1]
            d2m = snowfall[2]
            d2n = snowfall[3]
            d3m = snowfall[4]
            d3n = snowfall[5]
            d4m = snowfall[6]
            d4n = snowfall[7]
            d5m = snowfall[8]
            d5n = snowfall[9]
            total = avg_snow(d1m)+avg_snow(d1n)+avg_snow(d2m)+avg_snow(d2n)
            total += avg_snow(d3m)+avg_snow(d3n)+avg_snow(d4m)+avg_snow(d4n)
            total += avg_snow(d5m)+avg_snow(d5n)
            insertion = (None, name, state_name, url, d1m, d1n, d2m,
                         d2n, d3m, d3n, d4m, d4n, d5m, d5n, total)
            statement = 'INSERT INTO "Mountain_Snow" '
            statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)
    conn.commit()
    
    conn.close()
    
    return data

def insert_place_data(data):
    conn = sqlite3.connect('snowfall.db')
    cur = conn.cursor()

    google_data_list = []
    for c in data:
        for d in c[1].items():
            name = d[0]
            state_name = d[1]['State']
            google_location_info = google_api.get_lat_and_long(name, state_name)
            lat = google_location_info[0]
            long = google_location_info[1]
            insertion = (None, name, state_name, lat, long)
            statement = 'INSERT INTO "Mountain_Locations" '
            statement += 'VALUES (?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)
            google_data_list.append((name, lat, long, state_name))
    conn.commit()
    
    count = 1
    for c in google_data_list:
        yelp_data = yelp.yelp_individual_request(c[0], c[1], c[2])
        insertion = (None, c[0], c[3], yelp_data[1])
        statement = 'INSERT INTO "Yelp" '
        statement += 'VALUES (?, ?, ?, ?)'
        cur.execute(statement, insertion)
        conn.commit()
        count +=1
    conn.commit()
    
    statement = '''
    UPDATE Mountain_Locations
    SET Id = (SELECT Id FROM Mountain_Snow
                            WHERE MountainName = Mountain_Locations.Name AND State=
                            Mountain_Locations.State)
    WHERE EXISTS (SELECT Id
                  FROM Mountain_Snow
                  WHERE Name = Mountain_Locations.Name AND State=
                  Mountain_Locations.State)
    '''
    cur.execute(statement)
    conn.commit()
    
    statement = '''
    UPDATE Yelp
    SET Id = (SELECT Id FROM Mountain_Snow
                            WHERE MountainName=Yelp.Name AND State=Yelp.State)
    WHERE EXISTS (SELECT Id
                  FROM Mountain_Snow
                  WHERE MountainName=Yelp.Name AND State=Yelp.State)
    '''
    cur.execute(statement)
    conn.commit()
    
    conn.close()

if __name__ == "__main__":
    init_db()
    data = insert_snow_data()
    insert_place_data(data)
