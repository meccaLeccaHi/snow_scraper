import plotly.plotly as py
from plotly.graph_objs import *
import sqlite3

def state_province_chart(state_or_province):
    conn = sqlite3.connect('snowfall.db')
    cur = conn.cursor()

    statement = 'SELECT * FROM Mountain_Locations JOIN Mountain_Snow ON'
    statement+= " Mountain_Locations.Name=Mountain_Snow.MountainName AND"
    statement+= " Mountain_Locations.State=Mountain_Snow.State "
    statement+= 'JOIN Yelp ON Mountain_Locations.Name=Yelp.Name AND'
    statement+= " Mountain_Locations.State=Yelp.State "
    statement+= 'WHERE Mountain_Snow.State="'+state_or_province+'" '
    # print(statement)
    cur.execute(statement)
    snow_data = []
    for row in cur:
        snow_data.append(row)
    conn.close()

    trace1 = Bar(
        x=[x[0] for x in snow_data],
        y=[x[17] for x in snow_data],
        name='5 day predicted snowfall for '+state_or_province+''
        )
    data = [trace1]
    layout = Layout(
        barmode='group'

    )

    fig = Figure(data=data, layout=layout)
    py.plot(fig, filename='5 day predicted snowfall for '+state_or_province+'')

state_province_chart(input("Enter State or Province: "))
