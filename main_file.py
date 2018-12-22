import sqlite3
import google_api
import opensnow
import datetime as dt
import google_api

today = dt.date.today().strftime('%Y-%m-%d')
db_name = 'data/snowfall_'+today+'.db'

def init_db():
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'Mountain_Snow';
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
            'Icon' TEXT NOT NULL,
            'Base' INTEGER,
            'day1D' FLOAT NOT NULL,
            'day1N' FLOAT NOT NULL,
            'day2D' FLOAT NOT NULL,
            'day2N' FLOAT NOT NULL,
            'day3D' FLOAT NOT NULL,
            'day3N' FLOAT NOT NULL,
            'day4D' FLOAT NOT NULL,
            'day4N' FLOAT NOT NULL,
            'day5D' FLOAT NOT NULL,
            'day5N' FLOAT NOT NULL,
            'day1TOT' FLOAT NOT NULL,
            'day2TOT' FLOAT NOT NULL,
            'day3TOT' FLOAT NOT NULL,
            'day4TOT' FLOAT NOT NULL,
            'day5TOT' FLOAT NOT NULL,
            'Total' FLOAT NOT NULL,
            'Latitude' FLOAT NOT NULL,
            'Longitude' FLOAT NOT NULL
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()

def insert_data():
    tomm = dt.datetime.now().day+1
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    state_list = opensnow.crawl_main()

    for state in state_list:
        for key, value in state.items():
            name = key
            state_name = value['State']
            snowfall = value['Snowfall']
            url = value['URL']
            icon = value['Icon']
            if snowfall:
                base_depth = snowfall[3].strip('"')
            else:
                base_depth = ''

            dates = value['Dates']
            forecast = value['Forecast']
            sel_forecast = [forecast[ind] for ind in range(len(dates)) if dates[ind]>=tomm]
            day1D,day1N,day2D,day2N,day3D,day3N,day4D,day4N,day5D,day5N = sel_forecast
            day1total = day1D+day1N
            day2total = day2D+day2N
            day3total = day3D+day3N
            day4total = day4D+day4N
            day5total = day5D+day5N
            total = sum(sel_forecast)

            # Fetch lat. and long. from google
            google_loc_info = google_api.get_lat_and_long(name, state_name)
            lat = google_loc_info[0]
            long = google_loc_info[1]

            insertion = (None, name, state_name, url, icon, base_depth, day1D, day1N, day2D,
                         day2N, day3D, day3N, day4D, day4N, day5D, day5N, day1total,
                         day2total, day3total, day4total, day5total, total, lat, long)
            statement = 'INSERT INTO "Mountain_Snow" '
            statement += 'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            cur.execute(statement, insertion)
            # break
        # break
        print(state_name, 'data inserted')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    insert_data()
