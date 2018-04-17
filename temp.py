import sqlite3
def function(limit):
    conn = sqlite3.connect('snowfall.db')
    cur = conn.cursor()

    statement = 'SELECT * FROM Mountain_Locations JOIN Mountain_Snow ON'
    statement+= " Mountain_Locations.Name=Mountain_Snow.MountainName AND"
    statement+= " Mountain_Locations.State=Mountain_Snow.State "
    statement+= 'JOIN Yelp ON Mountain_Locations.Name=Yelp.Name AND'
    statement+= " Mountain_Locations.State=Yelp.State ORDER BY TOTAL "
    statement+= 'LIMIT "'+str(limit)+'" '
    # print(statement)
    cur.execute(statement)
    for c in cur:
        print(c)

function(10)
