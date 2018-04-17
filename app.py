# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly.graph_objs import *
import sqlite3
from flask import Flask, render_template

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

conn = sqlite3.connect('snowfall.db')
cur = conn.cursor()

statement = 'SELECT Mountain_Snow.MountainName, Mountain_Snow.State, Latitude, '
statement+= 'Longitude, TOTAL, Yelp.Rating FROM Mountain_Locations '
statement+= "JOIN Mountain_Snow ON Mountain_Locations.Id=Mountain_Snow.Id "
statement+= 'JOIN Yelp ON Mountain_Locations.Id=Yelp.Id'

data_list = []
cur.execute(statement)
for row in cur:
    data_list.append(row)
conn.close()
stateANDProvince = []
text_list = []
for c in data_list:
    name = c[0]
    total  = c[4]
    rating_class = Rating(c[5])
    rating = rating_class.rating_unicode()
    text = str(Text(name, total, c[1], rating))
    text_list.append(text)
    if c[1] not in stateANDProvince:
        stateANDProvince.append(c[1])

title = '<b>Predicted Snowfall for the Next 5 Days</b><br>'
title += 'Source: <a href="https://opensnow.com/">Open Snow</a></br>'
title += 'Ratings From: <a href="https://www.yelp.com/">Yelp</a></br>'


colors = {
'background': 'rgb(236,236,236)',
'water': "rgba(0, 0, 255, .20)",
'black': 'rgb(0,0,0)',
'line_color': 'rgba(102, 102, 102)',
'land': "rgb(212, 212, 212)",
'white': 'rgb(255,255,255)'
}

server = Flask(__name__)

title += "<a href='/about' target='_self'>About This Project</a>"
@server.route('/about')
def about():
    return render_template('about.html')


app = dash.Dash(server=server, url_base_pathname='/')

app.layout = html.Div(style={'backgroundColor': colors['background'], 'margin-bottom': '0px'},children=[
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
                    'size': [x[4] if float(x[4])>5 else 5 for x in data_list],
                    'opacity': 0.8,
                    'reversescale': True,
                    'autocolorscale': False,
                    'line': {
                        'width': 1,
                        'color': colors['line_color']
                        },
                    'colorscale': 'Jet',
                    'color': [x[4] for x in data_list],
                    'colorbar': {
                        'title': "Inches of Snow<br>Forecasted",
                        'titlefont':{
                            'family': 'Lato',
                            'color': colors['black']
                            },
                        'len': .5,
                        'xpad': 40,
                        'ticksuffix': ' in.'
                        }
                    }
                }
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'title': title,
                'titlefont': {
                    'family': 'Lato',
                    'size': '18',
                    'color': colors['black']
                    },
                'margin': {
                    't':150
                    },
                'geo': {
                    'scope': 'north america',
                    'showland': True,
                    'landcolor': colors['land'],
                    'subunitcolor': colors['white'],
                    'countrycolor': colors['white'],
                    'showlakes': True,
                    'lakecolor': colors['water'],
                    'showocean': True,
                    'oceancolor': colors['water'],
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
                        'range': [ -135.0, -65.0 ],
                        'dtick': 5
                        },
                    'lataxis':{
                        'showgrid': True,
                        'gridwidth': 0.5,
                        'range': [ 30.0, 68.0 ],
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
    html.H1(
        children='Choose a Different Area',
        style={
            'margin-left': '60px',
            'font-family': 'Lato',
            'font-size': '2em',
            }),
    html.Div([
        dcc.Dropdown(
            id='state-value',
            options=[{'label': i, 'value': i} for i in stateANDProvince],
            value='Colorado'
            )
        ],
        style={'width': '20%', 'display': 'inline-block', 'font-family': 'Lato',
                'font-size': '1.75em', 'margin-left': '50px'
                }),

    dcc.Graph(
        id='indicator-graphic1',
        style={'height': '600', 'margin-left': '20px', 'margin-right': '20px',
            'margin-bottom':'50px'}
        ),
    dcc.Graph(id='graph-with-slider'),
    html.Div([
        dcc.Slider(
            id='value-slider',
            min=1,
            max=30,
            value=15,
            marks={1:'1',5:'5',10:'10',15:'15',20:'20',25:'25',30:'30'},
            )
        ],
        style={'margin': '0 auto', 'width': '400px', 'margin-bottom': '50px'}
        )
    ])

long_css_url = 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2cc54b8c03f'
long_css_url += '4126569a3440aae611bbef1d7a5dd/stylesheet.css'
external_css = ["https://fonts.googleapis.com/css?family=Lato",long_css_url]

for css in external_css:
    app.css.append_css({"external_url": css})

@app.callback(
    dash.dependencies.Output('indicator-graphic1', 'figure'),
    [dash.dependencies.Input('state-value', 'value')])

def update_graph(state_or_province):
    conn = sqlite3.connect('snowfall.db')
    cur = conn.cursor()

    statement='SELECT Mountain_Snow.MountainName, Mountain_Snow.State, Latitude,'
    statement+=' Longitude, TOTAL, Yelp.Rating FROM Mountain_Locations '
    statement+="JOIN Mountain_Snow ON Mountain_Locations.Id=Mountain_Snow.Id "
    statement+='JOIN Yelp ON Mountain_Locations.Id=Yelp.Id '
    statement+='WHERE Mountain_Snow.State="'+state_or_province+'" '

    cur.execute(statement)
    snow_data = []
    for row in cur:
        snow_data.append(row)
    conn.close()

    trace1 = Bar(
        x=[x[0] for x in snow_data],
        y=[x[4] for x in snow_data]
        )
    return {
    'data': [trace1],
    'layout': Layout(
        plot_bgcolor= colors['background'],
        paper_bgcolor= colors['background'],
        title= '5 Day Forecasted Snow for '+state_or_province+'',
        titlefont = dict(
            family= 'Lato',
            size= 30,
            color= colors['black']
            ),
        barmode='group',
        yaxis= dict(
            title= 'Inches',
            titlefont = dict(
                family= 'Lato',
                size= 20,
                color= colors['black']
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
@app.callback(
    dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('value-slider', 'value')])

def update_graph1(limit):
    conn = sqlite3.connect('snowfall.db')
    cur = conn.cursor()

    statement='SELECT Mountain_Snow.MountainName, Mountain_Snow.State, Latitude,'
    statement+=' Longitude, TOTAL, Yelp.Rating FROM Mountain_Locations '
    statement+="JOIN Mountain_Snow ON Mountain_Locations.Id=Mountain_Snow.Id "
    statement+='JOIN Yelp ON Mountain_Locations.Id=Yelp.Id '
    statement+= 'ORDER BY TOTAL DESC LIMIT "'+str(limit)+'" '

    cur.execute(statement)
    snow_data = []
    for row in cur:
        snow_data.append(row)
    conn.close()
    title = ''+str(limit)+' Mountains with the Most Predicted Snowfall<br>'
    title += '(Use slider below to change #)'
    trace1 = Bar(
        x=[x[0] for x in snow_data],
        y=[x[4] for x in snow_data]
        )
    return {
    'data': [trace1],
    'layout': Layout(
        plot_bgcolor= colors['background'],
        paper_bgcolor= colors['background'],
        title= title,
        titlefont = dict(
            family= 'Lato',
            size= 30,
            color= colors['black']
            ),
        barmode='group',
        yaxis= dict(
            title= 'Inches',
            titlefont = dict(
                family= 'Lato',
                size= 20,
                color= colors['black']
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
