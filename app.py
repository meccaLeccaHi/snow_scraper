## Evolving from the basics

# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import secrets
from plotly import graph_objs as go
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State, Event

import sqlite3
import secrets
import pandas as pd
import time

app = dash.Dash(__name__)
server = app.server
app.title = 'SnoDash'

title = '<b>Predicted Snowfall for the Next 5 Days</b><br>'
title += 'Source: <a href="https://opensnow.com/">Open Snow</a></br>'
#title += "<a href='/about' target='_self'>About This Project</a>"

colors = {
'background': 'rgb(236,236,236)',
'water': "rgba(0, 0, 255, .20)",
'black': 'rgb(0,0,0)',
'line_color': 'rgba(102, 102, 102)',
'land': "rgb(212, 212, 212)",
'white': 'rgb(255,255,255)'
}

slider_style = {'color': colors['black'], 'font-size': '1.5em',
                'font-family': 'Lato',}

def fetch_data():
    # Import snowfall data from db
    statement = 'SELECT Mountain_Snow.MountainName, Mountain_Snow.State, Latitude, '
    statement+= 'Longitude, TOTAL FROM Mountain_Locations '
    statement+= "JOIN Mountain_Snow ON Mountain_Locations.Id=Mountain_Snow.Id "
    #statement+= 'JOIN Yelp ON Mountain_Locations.Id=Yelp.Id'
    conn = sqlite3.connect('snowfall.db')
    # Sort by expected snowfall (greatest to least)
    resort_df = pd.read_sql_query(statement, conn).sort_values(by=['TOTAL'], ascending=False)
    # Set variable telling us which states/provinces are included
    stateANDProvince = resort_df.State.unique()
    # Create text label for each resort on the map
    def text_label(row):
        return '{}: {} in<br>{}</br>'.format(row.MountainName, row.TOTAL,
                    row.State)  ## Add <base_inches> here, once it exists
    resort_df['text'] = resort_df.apply(text_label, axis=1)
    # Set variable telling us when the database was last updated
    cur = conn.cursor()
    cur.execute('SELECT Time FROM Timestamp ORDER BY ID DESC LIMIT 1')
    scrape_time = time.ctime(cur.fetchone()[0])
    conn.close()

    return(resort_df, stateANDProvince, scrape_time)

resort_df, stateANDProvince, scrape_time = fetch_data()

# Boostrap CSS
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})


#  Layouts
layout_table = dict(
    autosize=True,
    height=500,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
)
layout_table['font-size'] = '12'
layout_table['margin-top'] = '20'

layout_map = dict(
    autosize=True,
    height=500,
    font=dict(color="#191A1A"),
    title=title,
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
    mapbox=dict(
        accesstoken=secrets.mapbox_key,
        style="dark",
        center=dict(
            lon=-105.25,
            lat=50
        ),
        zoom=1.75,
    )
)

layout_map2 = {
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

#TODO: COLLAPSE THESE 2 FUNCTIONS INTO ONE
# functions
def gen_map(map_data):
    # groupby returns a dictionary mapping the values of the first field
    # 'classification' onto a list of record dictionaries with that
    # classification value.

    ## FIX THIS
    layout_map['mapbox']['center']['lon'] = map_data['Longitude'][0:10].mean()
    layout_map['mapbox']['center']['lat'] = map_data['Latitude'][0:10].mean()
    layout_map['mapbox']['zoom'] = 4-(map_data.Latitude[0:10].max()-map_data.Latitude[0:10].min())/15

    return {
        "data": [{
                "type": "scattermapbox",
                "lat": map_data['Latitude'],
                "lon": map_data['Longitude'],
                "hoverinfo": "text",
                "hovertext": map_data['text'],
                "mode": "markers",
                "name": map_data['MountainName'],
                "marker": {
                    'size':map_data['TOTAL'],
                    'opacity': 0.5,
                    'colorscale': 'Jet',
                    'reversescale': True,
                    'color': map_data['TOTAL']
                }
        }],
        "layout": layout_map
    }

# functions
def gen_map2(map_data):
    # groupby returns a dictionary mapping the values of the first field
    # 'classification' onto a list of record dictionaries with that
    # classification value.
    return {
        'data': [{
            'type': 'scattergeo',
            'text': map_data['text'],
            'locationmode':'USA-states',
            'lon': map_data['Longitude'],
            'lat': map_data['Latitude'],
            'hoverinfo': "text",
            'mode': 'markers',
            'marker': {
                'size':map_data['TOTAL'],
                'opacity': 0.8,
                'reversescale': True,
                'autocolorscale': False,
                'line': {
                    'width': 1,
                    'color': colors['line_color']
                    },
                'colorscale': 'Jet',
                'color': map_data['TOTAL'],
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
        ], "layout": layout_map2
    }

app.layout = html.Div(
    html.Div([
        html.Div(
            [
                html.H1(children='SnoDash',
                        className='nine columns'),
                html.Img(
                    src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Snowboarding.jpg/250px-Snowboarding.jpg",
                    className='three columns',
                    style={
                        'height': '16%',
                        'width': '16%',
                        'float': 'right',
                        'position': 'relative',
                        'padding-top': 12,
                        'padding-right': 0
                    },
                ),
                html.Div(children='Last Updated: {}'.format(scrape_time),
                        className='nine columns'
                )
            ], className="row"
        ),

        # Map + table + Histogram
        html.Div(
            [
                html.Div(
                    [
                        html.P('Developed by some guy - ', style = {'display': 'inline'}),
                        html.A('guy@email.com', href = 'mailto:guy@email.com')
                    ], className = "twelve columns",
                       style = {'fontSize': 18, 'padding-top': 20}
                )
            ], className="row"
        ),

        # Snowfall map
        html.Div([
            dcc.Graph(id='snow-map',
                    animate=True,
                    style={'height': '1050'},
                    figure=gen_map2(resort_df)),
                ], className="row"
            ),

        # State selector
        html.Div(
            [
                html.Div(
                    [
                        html.P('Choose a State:'),
                        dcc.Dropdown(
                                id='state-value',
                                options=[{'label': i, 'value': i} for i in stateANDProvince],
                                multi=True
                        ),
                    ],
                    className='six columns',
                    style={'margin-top': '10'}
                )
            ],
            className='row'
        ),

        html.Div(
            [
                dcc.Graph(
                id='state-snow-bar',
                style={'height': '600', 'margin-left': '4%', 'margin-right': '4%',
                    'margin-bottom':'50px'}
                ),
            ],
            className='row'
        ),

        html.Div(
            [
                html.Div(
                    [
                        dt.DataTable(
                            rows=resort_df.to_dict('records'),
                            columns=resort_df.columns,
                            row_selectable=True,
                            filterable=True,
                            sortable=True,
                            selected_row_indices=[],
                            id='snow-table'),
                    ],
                    style = layout_table,
                    className="six columns"
                ),
                html.Div(
                    [
                        dcc.Graph(id='map-graph',
                                  animate=True,
                                  style={'margin-top': '20'})
                    ], className = "six columns"
                )
            ],
            className='row'
        ),

        html.Div(
            [
                dcc.Graph(
                    id='graph-with-slider',
                    style={'height': '600', 'margin-left': '4%', 'margin-right': '4%',
                        'margin-bottom':'50px'}
                    ),
                html.Div([
                    dcc.Slider(
                        id='value-slider',
                        min=10,
                        max=100,
                        value=50,
                        marks= {
                                10:{'label': '10', 'style': slider_style},
                                20:{'label': '20', 'style': slider_style},
                                30:{'label': '30', 'style': slider_style},
                                40:{'label': '40', 'style': slider_style},
                                50:{'label': '50', 'style': slider_style},
                                60:{'label': '60', 'style': slider_style},
                                70:{'label': '70', 'style': slider_style},
                                80:{'label': '80', 'style': slider_style},
                                90:{'label': '90', 'style': slider_style},
                                100:{'label': '100', 'style': slider_style}
                                },
                        updatemode='drag'
                        )
                    ],
                    style={'display': 'inline-block','margin': 'auto', 'width': '30%',
                        'margin-bottom':'150px','margin-left': '35%',
                        'margin-right':'35%'}
                    )
            ], className='row'
        )
    ], className='ten columns offset-by-one'))


@app.callback(
    Output('map-graph', 'figure'),
    [Input('snow-table', 'rows'),
     Input('snow-table', 'selected_row_indices')])
def map_selection(rows, selected_row_indices):
    aux = pd.DataFrame(rows)
    temp_df = aux.ix[selected_row_indices, :]
    if len(selected_row_indices) == 0:
        return gen_map(aux)
    return gen_map(temp_df)


@app.callback(
    Output('snow-table', 'rows'),
    [Input('state-value', 'value')])
def update_selected_row_indices1(state_or_province):
    resort_df, stateANDProvince, scrape_time = fetch_data()
    if state_or_province!=None:
        resort_df = resort_df.loc[resort_df['State'].isin(state_or_province)]
    return resort_df.to_dict('records')


@app.callback(
    Output('state-snow-bar', 'figure'),
    [Input('state-value', 'value')])
def update_graph(state_or_province):
    resort_df, stateANDProvince, scrape_time = fetch_data()

    if state_or_province!=None:
        resort_df = resort_df.loc[resort_df['State'].isin(state_or_province)]
        graph_title = '5 Day Forecasted Snow for '+', '.join(state_or_province)
    else:
        graph_title = '5 Day Forecasted Snow'

    trace1 = Bar(
        x=resort_df['MountainName'],
        y=resort_df['TOTAL']
        )
    return {
    'data': [trace1],
    'layout': Layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        title=graph_title,
        titlefont=dict(
            family='Lato',
            size=30,
            color=colors['black']
            ),
        barmode='group',
        yaxis= dict(
            title='Inches',
            titlefont=dict(
                family='Lato',
                size=20,
                color=colors['black']
                ),
            automargin=True,
            rangemode='nonnegative'
            ),
        xaxis=dict(
            fixedrange=True,
            showticklabels=True,
            tickangle=45,
            tickfont=dict(
                family='Lato',
                color='black'
                )
            ),
        margin=layout.Margin(
            l=75,
            r=75,
            b=180
        ),
        bargap=.35
        )
    }

@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('value-slider', 'value')])
def update_graph1(limit):
    resort_df, stateANDProvince, scrape_time = fetch_data()
    resort_df = resort_df.iloc[range(limit)]

    title = ''+str(limit)+' Mountains with the Most Predicted Snowfall<br>'
    title += '(Use slider below to change #)'
    trace1 = Bar(
        x=resort_df['MountainName'],
        y=resort_df['TOTAL']
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
        margin= layout.Margin(
            l=75,
            r=75,
            b=180
        ),
        bargap= .35
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
