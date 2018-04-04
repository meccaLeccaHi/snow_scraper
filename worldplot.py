import plotly.plotly as py
from plotly.graph_objs import *
import sqlite3


def graph():
    conn = sqlite3.connect('snowfall.db')
    cur = conn.cursor()

    statement = 'SELECT * FROM Mountain_Locations JOIN Mountain_Snow ON'
    statement+= " Mountain_Locations.Name=Mountain_Snow.MountainName AND"
    statement+= " Mountain_Locations.State=Mountain_Snow.State "
    statement+= 'JOIN Yelp ON Mountain_Locations.Name=Yelp.Name AND'
    statement+= " Mountain_Locations.State=Yelp.State"

    data_list = []
    cur.execute(statement)
    for row in cur:
        data_list.append(row)
    conn.close()

    text_list = []
    for c in data_list:
        name = c[0]
        total  = c[17]
        rating_info = c[20]
        if rating_info == '5.0' or rating_info == '4.5':
            rating = '\u2605'*5
        elif rating_info == '4.0' or rating_info == '3.5':
            rating = '\u2605'*4+'\u2606'*1
        elif rating_info == '3.0' or rating_info == '2.5':
            rating = '\u2605'*3+'\u2606'*2
        elif rating_info == '2.0' or rating_info == '1.5':
            rating = '\u2605'*2+'\u2606'*3
        elif rating_info == '1.0' or rating_info == '0.5':
            rating = '\u2605'*1+'\u2606'*4
        elif rating_info == '0.0':
            rating = '\u2606'*4
        else:
            rating = 'No Rating'
        # text = '<a href="{}" style="color:black"><b>{}</b></a>: {} in<br>{}</br>'.format(c[2], name, total, c[1])
        text = '{}: {} in<br>{}</br>'.format(name, total, c[1])
        text += 'Rating: {}'.format(rating)
        text_list.append(text)
        title = '<b>Predicted Snowfall for the Next 5 Days</b><br>'
        title += 'Source: <a href="https://opensnow.com/">Open Snow</a></br>'
        title += 'Source: <a href="https://www.yelp.com/">Yelp</a>'
    data = [ dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = [x[3] for x in data_list],
            lat = [x[2] for x in data_list],
            text = [x for x in text_list],
            hoverinfo = "text",
            mode = 'markers',
            marker = dict(
                size = [x[17] if float(x[17])>5 else 5 for x in data_list],
                opacity = 0.8,
                reversescale = True,
                autocolorscale = False,
                line = dict(
                    width=1,
                    color='rgba(102, 102, 102)'
                ),
                colorscale = 'Jet',
                color = [x[17] for x in data_list],
                colorbar=dict(
                    title="Inches of Snow Forecasted",
                    len= .5
                )
            ))]


    # layout = dict(
    #         title = 'Predicted Snowfall for the Next 5 Days',
    #         geo = dict(
    #             showland = True,
    #             landcolor = "rgb(212, 212, 212)",
    #             subunitcolor = "rgb(255,255, 255)",
    #             countrycolor = "rgb(255, 255, 255)",
    #             showlakes = True,
    #             lakecolor = "rgba(0, 0, 255, .65)",
    #             showsubunits = True,
    #             showcountries = True,
    #             scope= 'usa',
    #             # lataxis = dict(
    #             #     range = [ 20, 80 ],
    #             #     # showgrid = True,
    #             #     # tickmode = "linear",
    #             #     # dtick = 10
    #             # ),
    #             # lonaxis = dict(
    #             #     range = [-170, -50],
    #             #     # showgrid = True,
    #             #     # tickmode = "linear",
    #             #     # dtick = 20),
    #         ))
    layout = dict(
        title = title,
        geo = dict(
            scope = 'north america',
            showland = True,
            landcolor = "rgb(212, 212, 212)",
            subunitcolor = "rgb(255, 255, 255)",
            countrycolor = "rgb(255, 255, 255)",
            showlakes = True,
            lakecolor = "rgba(0, 0, 255, .35)",
            showsubunits = True,
            showcountries = True,
            resolution = 50,
            projection = dict(
                type = 'conic conformal',
                rotation = dict(
                    lon = -100
                )
            ),
            lonaxis = dict(
                showgrid = True,
                gridwidth = 0.5,
                range= [ -135.0, -60.0 ],
                dtick = 5
            ),
            lataxis = dict (
                showgrid = True,
                gridwidth = 0.5,
                range= [ 28.0, 68.0 ],
                dtick = 5
            )
        ))

    fig = dict(data=data, layout=layout)
    py.plot( fig, filename='5_day_snowfall' )
