## Evolving from the basics

# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import secrets
from plotly import graph_objs as go
#from plotly.graph_objs import *
from dash.dependencies import Input, Output, State, Event

import sqlite3
import secrets
import pandas as pd
import datetime
import json

app = dash.Dash(__name__)
server = app.server
app.title = 'SnoDash'

# Load state geo data
with open('cache-geo.json') as json_data:
    region_options = json.load(json_data)

#title = '<b>Predicted Snowfall for the Next 5 Days</b><br>'
#title += 'Source: <a href="https://opensnow.com/">Open Snow</a></br>'
#title += "<a href='/about' target='_self'>About This Project</a>"

slider_style = {'font-size': '1.5em'}

def fetch_data():
    # Import snowfall data from db
    statement = 'SELECT Mountain_Snow.MountainName, Mountain_Snow.State, Mountain_Snow.Base, '
    statement+= 'Latitude, Longitude, TOTAL, day1D, day1N, day2D, day2N, day3D, '
    statement+= 'day3N, day4D, day4N, day5D, day5N, day1TOT, day2TOT, day3TOT, day4TOT, '
    statement+= 'day5TOT FROM Mountain_Locations '
    statement+= 'JOIN Mountain_Snow ON Mountain_Locations.Id=Mountain_Snow.Id '

    conn = sqlite3.connect('snowfall.db')
    # Sort by expected snowfall (greatest to least)
    resort_data = pd.read_sql_query(statement, conn).sort_values(by=['TOTAL'], ascending=False)
    # Set variable telling us which states/provinces are included
    stateANDProvince = resort_data.State.unique()

    region_vals = {}
    for k, v in region_options.items():
        region_vals[k] = [state for state in v if state in stateANDProvince]

    # Create text label for each resort on the map
    def text_label(row):
        if row.Base!=row.Base:
            base_str = ''
        else:
            base_str = '</br>{2}" base'
        if row.TOTAL==0.0:
            tot_str = ''
        else:
            tot_str = ': {1} in'
        out_str = '{0}'+tot_str+base_str+'<br>{3}'
        return out_str.format(row.MountainName, row.TOTAL,
                    row.Base, row.State)
    resort_data['text'] = resort_data.apply(text_label, axis=1)
    # Refine forecasted snowfall for each resort on the map
    def snow_forecast(row):
        return [row[['day1TOT', 'day2TOT', 'day3TOT', 'day4TOT', 'day5TOT']]]
    resort_data['forecast'] = resort_data.apply(snow_forecast, axis=1)
    # Set variable telling us when the database was last updated
    cur = conn.cursor()
    cur.execute('SELECT Time FROM Timestamp ORDER BY ID DESC LIMIT 1')
    scrape_time = cur.fetchone()[0]
    conn.close()

    return(resort_data, stateANDProvince, scrape_time, region_vals)

resort_data, stateANDProvince, scrape_time, region_vals = fetch_data()
# Set variables to be displayed in table
table_data = resort_data[['MountainName','State','Base','TOTAL']]


# Boostrap CSS
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})


#  Layouts
layout_table = dict(
    autosize=True,
    height=500,
    font=dict(color='#191A1A'),
    titlefont=dict(color='#191A1A', size='14'),
    margin=dict(
        l=5,
        r=5,
        b=5,
        t=5
    ),
    hovermode='closest',
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
)
layout_table['font-size'] = '12'
layout_table['margin-top'] = '20'

layout_map = dict(
    autosize=True,
    height=500,
    font=dict(color='#191A1A'),
    title='<b>Predicted Snowfall for the Next 5 Days</b>',
    titlefont=dict(color='#191A1A', size='14'),
    margin=dict(
        l=5,
        r=5,
        b=5,
        t=25
    ),
    hovermode='closest',
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
    mapbox=dict(
        accesstoken=secrets.mapbox_key,
        style='dark',
        center=dict(
            lon=-105.25,
            lat=50
        ),
        zoom=2,
    )
)

layout_state_bar = dict(
    barmode='group',
    xaxis=dict(
        fixedrange=True,
        showticklabels=True,
        tickangle=45
    ),
    yaxis= dict(
        title='Inches',
        automargin=True,
        rangemode='nonnegative'
    ),
    margin=go.layout.Margin(
        l=5,
        r=5,
        b=150
    ),
    bargap=.35
)


def gen_map(table_data, colorbar=False, zoom=2, location='USA-states'):
    # groupby returns a dictionary mapping the values of the first field
    # 'classification' onto a list of record dictionaries with that
    # classification value.

    if table_data['MountainName'].empty:
        map_data = resort_data
    else:
        map_data = resort_data[resort_data['MountainName'].isin(table_data['MountainName'])]

    # ## FIX THIS
    # layout_map['mapbox']['center']['lon'] = map_data['Longitude'].mean()
    # layout_map['mapbox']['center']['lat'] = map_data['Latitude'].mean()
    layout_map['mapbox']['zoom'] = zoom

    if colorbar:
        cb = dict(
            title='Inches of Snow<br>Forecasted',
            len=.35,
            xpad=10,
            ticksuffix=' in.')
    else:
        cb = []

    return {
        'data': [{
                'type': 'scattermapbox',
                'locationmode':location,
                'lat': map_data['Latitude'],
                'lon': map_data['Longitude'],
                'hoverinfo': 'text',
                'hovertext': map_data['text'],
                'mode': 'markers',
                'name': map_data['MountainName'],
                'marker': {
                    'size':map_data['TOTAL'],
                    'opacity': 0.5,
                    'colorscale': 'Jet',
                    'reversescale': True,
                    'color': map_data['TOTAL'],
                    'colorbar': cb
                }
        }],
        'layout': layout_map
    }

app.layout = html.Div(
    html.Div([
        # Header
        html.Div(
            [
                html.H1(children='SnoDash',
                        className='nine columns'),
                html.Img(
                    src='https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Snowboarding.jpg/250px-Snowboarding.jpg',
                    className='three columns',
                    style={
                        'height': '16%',
                        'width': '16%',
                        'float': 'right',
                        'position': 'relative',
                        'padding-top': 0,
                        'padding-right': 0
                    },
                ),
                html.Div(children='Last Updated: {}'.format(scrape_time),
                        className='nine columns',
                           style = {'fontSize': 14, 'padding-top': 0}
                )
            ], className='row'
        ),

        # Contact info
        html.Div(
            [
                html.Div(
                    [
                        html.P('Developed by some guy - ', style = {'display': 'inline'}),
                        html.A('guy@email.com', href = 'mailto:guy@email.com')
                    ], className = 'twelve columns',
                       style = {'fontSize': 16, 'padding-top': 0}
                )
            ], className='row'
        ),

        # Snowfall map
        html.Div([
            dcc.Graph(id='snow-map',
                    animate=True,
                    style={'width': '100%'},
                    figure=gen_map(resort_data, colorbar=True)),
                ], className='row'
            ),

        # State selector + Region radio buttons
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
                    style={'margin-top': '0'}
                ),
                html.Div(
                    [
                        html.P('Choose Region:'),
                        dcc.RadioItems(
                                id = 'region-value',
                                options=[{'label': k, 'value': k} for k in region_vals.keys()],
                                value='All',
                                labelStyle={'display': 'inline-block'}
                        ),
                    ],
                    className='six columns',
                    style={'margin-top': '0'}
                )
            ],
            className='row'
        ),

        # State snowfall bar chart
        html.Div(
            [
                dcc.Graph(
                id='state-snow-bar',
                style={'margin-left': '0', 'margin-right': '0',
                    'margin-bottom':'0'}
                ),
            ],
            className='row'
        ),

        # Snowfall table + state map
        html.Div(
            [
                html.Div(
                    [
                        dt.DataTable(
                            rows=table_data.to_dict('records'),
                            columns=table_data.columns,
                            row_selectable=True,
                            filterable=True,
                            sortable=True,
                            selected_row_indices=[],
                            id='snow-table'),
                    ],
                    style = layout_table,
                    className='six columns'
                ),
                html.Div(
                    [
                        dcc.Graph(id='state-snow-map',
                                  animate=True,
                                  style={'margin-top': '0'})
                    ], className = 'six columns'
                )
            ],
            className='row'
        ),

        # Precipitation bar chart
        html.Div(
            [
                dcc.Graph(
                id='forecast-bar',
                style={'margin-left': '0', 'margin-right': '0',
                    'margin-bottom':'0'}
                ),
            ],
            className='row'
        ),

        # N greatest snowfall bar chart
        html.Div(
            [
                dcc.Graph(
                    id='slider-bar',
                    style={'margin-left': '0', 'margin-right': '0',
                        'margin-bottom':'0'}
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
                        'margin-bottom':'0','margin-left': '35%',
                        'margin-right':'35%'}
                    )
            ], className='row'
        )
    ], className='ten columns offset-by-one'))

@app.callback(
    Output('state-value', 'options'),
    [Input('region-value', 'value')])
def set_regions(selected_region):
    #resort_data, stateANDProvince, scrape_time, region_vals = fetch_data()
    return [{'label': i, 'value': i} for i in region_vals[selected_region]]

@app.callback(
    Output('state-snow-bar', 'figure'),
    [Input('state-value', 'value'),
    Input('region-value', 'value')])
def update_graph(state_or_province, selected_region):
    resort_data, stateANDProvince, scrape_time, region_vals = fetch_data()
    if state_or_province!=None:
        resort_data = resort_data.loc[resort_data['State'].isin(state_or_province)]
        layout_state_bar['graph_title'] = '5 Day Forecasted Snow for '+', '.join(state_or_province)
    else:
        layout_state_bar['graph_title'] = '5 Day Forecasted Snow'

    resort_data = resort_data.loc[resort_data['State'].isin(region_vals[selected_region])]

    trace1 = go.Bar(
        x=resort_data['MountainName'],
        y=resort_data['TOTAL']
        )

    return {
    'data': [trace1],
    'layout': layout_state_bar
    }

@app.callback(
    Output('snow-table', 'rows'),
    [Input('state-value', 'value'),
    Input('region-value', 'value')])
def update_snow_table(state_or_province, selected_region):
    resort_data, stateANDProvince, scrape_time, region_vals = fetch_data()
    table_data = resort_data[['MountainName','State','Base','TOTAL']]
    if state_or_province!=None:
        table_data = table_data.loc[table_data['State'].isin(state_or_province)]
    table_data = table_data.loc[table_data['State'].isin(region_vals[selected_region])]
    return table_data.to_dict('records')

@app.callback(
    Output('state-snow-map', 'figure'),
    [Input('snow-table', 'rows'),
     Input('snow-table', 'selected_row_indices')])
def update_state_map(rows, selected_row_indices):
    aux = pd.DataFrame(rows)
    temp_df = aux.ix[selected_row_indices, :]
    if len(selected_row_indices) == 0:
        return gen_map(aux, zoom=3, location='Florida')
    return gen_map(temp_df, zoom=3)


@app.callback(
    Output('forecast-bar', 'figure'),
    [Input('snow-table', 'rows'),
     Input('snow-table', 'selected_row_indices')])
def update_forecast_bar(rows, selected_row_indices):

    numdays = 5

    if len(selected_row_indices) == 0:
        temp_df = pd.DataFrame(rows)
    else:
        temp_df = pd.DataFrame(rows).ix[selected_row_indices, :]

    line_data = resort_data[resort_data['MountainName'].isin(temp_df['MountainName'])]

    graph_title = '{}-Day Forecasted Snowfall'.format(numdays)

    ts = datetime.datetime.strptime(scrape_time, '%Y-%m-%d %H:%M:%S')
    ts = ts.replace(hour=0, minute=0, second=0, microsecond=0)

    # Create list of dates for x-axis
    date_list = [(ts + datetime.timedelta(days=x)) for x in range(1, numdays+1)]

    traces = []
    for index, row in line_data.iterrows():

        traces.append(go.Bar(
            x=date_list,
            y=row['forecast'][0],
            text=row['text'],
            textposition = 'auto',
            name=row['MountainName']
        ))

    return {
    'data': traces,
    'layout': go.Layout(
        title=graph_title,
        yaxis=dict(
            title='Inches',
        ),
        xaxis=dict(
            tickformat='%m/%d',
            tickangle=45
        )
    )
    }

@app.callback(
    Output('slider-bar', 'figure'),
    [Input('value-slider', 'value')])
def update_slider_graph(limit):
    resort_data, stateANDProvince, scrape_time, region_vals = fetch_data()
    resort_data = resort_data.iloc[range(limit)]

    title = ''+str(limit)+' Mountains with the Most Predicted Snowfall<br>'
    title += '(Use slider below to change #)'
    trace1 = go.Bar(
        x=resort_data['MountainName'],
        y=resort_data['TOTAL']
        )
    return {
    'data': [trace1],
    'layout': go.Layout(
        title= title,
        barmode='group',
        yaxis= dict(
            title= 'Inches',
            automargin=True,
            rangemode= 'nonnegative'
            ),
        xaxis= dict(
            fixedrange = True,
            showticklabels=True,
            tickangle=45
            ),
        margin= go.layout.Margin(
            l=75,
            r=75,
            b=180
        ),
        bargap= .35
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
