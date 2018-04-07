# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly.graph_objs import *
import sqlite3

conn = sqlite3.connect('snowfall.db')
cur = conn.cursor()

statement = 'SELECT * FROM Mountain_Locations JOIN Mountain_Snow ON'
statement+= " Mountain_Locations.Name=Mountain_Snow.MountainName AND"
statement+= " Mountain_Locations.State=Mountain_Snow.State "
statement+= 'JOIN Yelp ON Mountain_Locations.Name=Yelp.Name AND'
statement+= " Mountain_Locations.State=Yelp.State"

class Text:
    def __init__(self, name, total, state, rating):
        self.name = name
        self.total = total
        self.state = state
        self.rating = rating
    def __str__(self):
        return '{}: {} in<br>{}</br>Rating: {}'.format(self.name, self.total,
                self.state, self.rating)
class Rating:
    def __init__(self, rating):
        self.rating_info = rating

    def rating_unicode(self):
        if self.rating_info == '5.0' or self.rating_info == '4.5':
            rating = '\u2605'*5
        elif self.rating_info == '4.0' or self.rating_info == '3.5':
            rating = '\u2605'*4+'\u2606'*1
        elif self.rating_info == '3.0' or self.rating_info == '2.5':
            rating = '\u2605'*3+'\u2606'*2
        elif self.rating_info == '2.0' or self.rating_info == '1.5':
            rating = '\u2605'*2+'\u2606'*3
        elif self.rating_info == '1.0' or self.rating_info == '0.5':
            rating = '\u2605'*1+'\u2606'*4
        elif self.rating_info == '0.0':
            rating = '\u2606'*4
        else:
            rating = 'No Rating'
        return rating


data_list = []
cur.execute(statement)
for row in cur:
    data_list.append(row)
conn.close()
stateANDProvince = []
text_list = []
for c in data_list:
    name = c[0]
    total  = c[17]
    rating_class = Rating(c[20])
    rating = rating_class.rating_unicode()
    text = str(Text(name, total, c[1], rating))
    text_list.append(text)
    if c[1] not in stateANDProvince:
        stateANDProvince.append(c[1])

title = '<b>Predicted Snowfall for the Next 5 Days</b><br>'
title += 'Source: <a href="https://opensnow.com/">Open Snow</a></br>'
title += 'Ratings From: <a href="https://www.yelp.com/">Yelp</a>'

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(
        children='SI 206 Final',
        style={
            'textAlign': 'center',
            'font-family': 'Lato',
            'font-size': '4em',
        }
    ),
    html.H3(
        children='Cooper Seligson',
        style={
            'textAlign': 'center',
            'font-family': 'Lato',
            'font-size': '2.5em',
        }
    ),
    dcc.Graph(
        id='graph-1',
        style={
            'height': '1050'
            },
        figure={
            'data': [
                {'type': 'scattergeo',
                'text': [x for x in text_list],
                'locationmode':'USA-states',
                'lon': [x[3] for x in data_list],
                'lat': [x[2] for x in data_list],
                'hoverinfo': "text",
                'mode': 'markers',
                'marker': {
                    'size': [x[17] if float(x[17])>5 else 5 for x in data_list],
                    'opacity': 0.8,
                    'reversescale': True,
                    'autocolorscale': False,
                    'line': {
                        'width': 1,
                        'color': 'rgba(102, 102, 102)'
                        },
                    'colorscale': 'Jet',
                    'color': [x[17] for x in data_list],
                    'colorbar': {
                        'title': "Inches of Snow Forecasted",
                        'len': .5
                        }
                    }
                }
            ],
            'layout': {
                'title': title,
                'titlefont': {
                    'family': 'Lato',
                    'size': '18',
                    'color': 'rgb(0,0,0)'
                    },
                'geo': {
                    'scope': 'north america',
                    'showland': True,
                    'landcolor': "rgb(212, 212, 212)",
                    'subunitcolor': "rgb(255, 255, 255)",
                    'countrycolor': "rgb(255, 255, 255)",
                    'showlakes': True,
                    'lakecolor': "rgba(0, 0, 255, .35)",
                    'showsubunits': True,
                    'showcountries': True,
                    'resolution': 50,
                    'projection': {
                        'type': 'conic conformal',
                        'rotation': {
                            'lon': -100
                            }
                        },
                    'lonaxis': {
                        'showgrid': True,
                        'gridwidth': 0.5,
                        'range': [ -135.0, -60.0 ],
                        'dtick': 5
                        },
                    'lataxis':{
                        'showgrid': True,
                        'gridwidth': 0.5,
                        'range': [ 28.0, 68.0 ],
                        'dtick': 5
                        }
                    }
                }
            }
    ),
    html.H1(
        children='Individual States and Provinces',
        style={
            'textAlign': 'center',
            'font-family': 'Lato',
            'font-size': '4em',
        }
    ),
    html.Div([
            dcc.Dropdown(
                id='state-value',
                options=[{'label': i, 'value': i} for i in stateANDProvince],
                value='Colorado'
            )
        ],
        style={'width': '20%', 'display': 'inline-block', 'font-family': 'Lato',
                'font-size': '1.75em'}),

    dcc.Graph(
        id='indicator-graphic',
        style={'height': '600'}
        ),
    html.Div([
        html.P('\n \n ')
    ])
])
external_css = ["https://fonts.googleapis.com/css?family=Lato",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/2cc54b8c03f4126569a3440aae611bbef1d7a5dd/stylesheet.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('state-value', 'value')])

def update_graph(state_or_province):
    conn = sqlite3.connect('snowfall.db')
    cur = conn.cursor()

    statement = 'SELECT * FROM Mountain_Locations JOIN Mountain_Snow ON'
    statement+= " Mountain_Locations.Name=Mountain_Snow.MountainName AND"
    statement+= " Mountain_Locations.State=Mountain_Snow.State "
    statement+= 'JOIN Yelp ON Mountain_Locations.Name=Yelp.Name AND'
    statement+= " Mountain_Locations.State=Yelp.State "
    statement+= 'WHERE Mountain_Snow.State="'+state_or_province+'" '

    cur.execute(statement)
    snow_data = []
    for row in cur:
        snow_data.append(row)
    conn.close()

    trace1 = Bar(
        x=[x[0] for x in snow_data],
        y=[x[17] for x in snow_data]
        )
    return {
    'data': [trace1],
    'layout': Layout(
        title= '5 Day Forecasted Snow for '+state_or_province+'',
        titlefont = dict(
            family= 'Lato',
            size= 30,
            color='rgb(0,0,0)'
            ),
        barmode='group',
        yaxis= dict(
            title= 'Inches',
            titlefont = dict(
                family= 'Lato',
                size= 20,
                color='rgb(0,0,0)'
                ),
            automargin=True,
            rangemode= 'nonnegative'
            ),
        xaxis= dict(
            fixedrange = True,
            showticklabels=True,
            tickangle=45,
            tickfont= dict(
                family='Lato',
                color='black'
                )
            ),
        margin= Margin(
            l=75,
            r=75,
            b=150
        ),
        bargap= .35
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
