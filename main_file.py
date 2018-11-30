import sqlite3
import google_api
import opensnow
import time

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
        DROP TABLE IF EXISTS 'timestamp';
    '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE 'Mountain_Snow' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'MountainName' TEXT NOT NULL,
            'State' TEXT NOT NULL,
            'URL' TEXT NOT NULL,
            'Base' TEXT NOT NULL,
            'day1D' TEXT NOT NULL,
            'day1N' TEXT NOT NULL,
            'day2D' TEXT NOT NULL,
            'day2N' TEXT NOT NULL,
            'day3D' TEXT NOT NULL,
            'day3N' TEXT NOT NULL,
            'day4D' TEXT NOT NULL,
            'day4N' TEXT NOT NULL,
            'day5D' TEXT NOT NULL,
            'day5N' TEXT NOT NULL,
            'day1TOT' INTEGER NOT NULL,
            'day2TOT' INTEGER NOT NULL,
            'day3TOT' INTEGER NOT NULL,
            'day4TOT' INTEGER NOT NULL,
            'day5TOT' INTEGER NOT NULL,
            'TOTAL' INTEGER NOT NULL
        );
    '''
    cur.execute(statement)
    statement = '''
        CREATE TABLE 'Mountain_Locations' (
            'Id' INTEGER,
            'Name' TEXT NOT NULL,
            'State' TEXT NOT NULL,
            'Latitude' INTEGER,
            'Longitude' INTEGER
        );
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Timestamp' (
            'Id' INTEGER,
            'Time' FLOAT NOT NULL
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

def insert_data():
    conn = sqlite3.connect('snowfall.db')
    cur = conn.cursor()

    data = opensnow.crawl_main()

    for c in data:
        for d in c[1].items():
            name = d[0]
            snowfall = d[1]['Snowfall']
            url = d[1]['URL']
            state_name = d[1]['State']
            base_depth = d[1]['Base']
            day1D = snowfall[0]
            day1N = snowfall[1]
            day2D = snowfall[2]
            day2N = snowfall[3]
            day3D = snowfall[4]
            day3N = snowfall[5]
            day4D = snowfall[6]
            day4N = snowfall[7]
            day5D = snowfall[8]
            day5N = snowfall[9]
            day1total = avg_snow(day1D)+avg_snow(day1N)
            day2total = avg_snow(day2D)+avg_snow(day2N)
            day3total = avg_snow(day3D)+avg_snow(day3N)
            day4total = avg_snow(day4D)+avg_snow(day4N)
            day5total = avg_snow(day5D)+avg_snow(day5N)
            total = avg_snow(day1D)+avg_snow(day1N)+avg_snow(day2D)+avg_snow(day2N)
            total += avg_snow(day3D)+avg_snow(day3N)+avg_snow(day4D)+avg_snow(day4N)
            total += avg_snow(day5D)+avg_snow(day5N)
            insertion = (None, name, state_name, url, base_depth, day1D, day1N, day2D,
                         day2N, day3D, day3N, day4D, day4N, day5D, day5N, day1total,
                         day2total, day3total, day4total, day5total, total)
            statement = 'INSERT INTO "Mountain_Snow" '
            statement += 'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            cur.execute(statement, insertion)
    conn.commit()
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

    insertion = (None, time.time())
    statement = 'INSERT INTO "timestamp" '
    statement += 'VALUES (?, ?)'
    cur.execute(statement, insertion)
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
    conn.close()

if __name__ == "__main__":
    init_db()
    insert_data()
