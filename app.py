import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State, Event
from plotly import graph_objs as go
import sqlite3
import secrets
import pandas as pd
import datetime
import json
import glob

app = dash.Dash(__name__)
server = app.server
app.title = 'FreshyFinder'
numdays = 5
data_dir = 'data/'
snowboard_img = 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Snowboarding.jpg/250px-Snowboarding.jpg'

# Load state data for controls
with open(data_dir+'cache-geo.json') as json_data:
    region_options = json.load(json_data)

# Create text label for each resort on the map
def text_label(row):

    if row.Base:
        base_str = '</br>{2}" base'
    else:
        base_str = ''
    if row.TotalExpected==0.0:
        tot_str = ''
    else:
        tot_str = ': {1} in'
    out_str = '{0}'+tot_str+base_str+'<br>{3}'

    return out_str.format(row.MountainName, row.TotalExpected,
                row.Base, row.State)

# Refine forecasted snowfall for each resort on the map
def snow_forecast(row):
    return [row[['day1TOT', 'day2TOT', 'day3TOT', 'day4TOT', 'day5TOT']]]

# Import snowfall data from db
def fetch_data(resort_id='All'):

    # Select newest database
    date_list = [filename[14:24] for filename in glob.glob("data/*.db")]
    scrape_date = sorted(date_list, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))[-1]
    db_name = data_dir+'snowfall_'+scrape_date+'.db'
    conn = sqlite3.connect(db_name)
    #print('db:', db_name)

    statement = 'SELECT MountainName, State, Base, TotalExpected, URL, Icon,'
    statement+= 'Latitude, Longitude, day1D, day1N, day2D, day2N, day3D, '
    statement+= 'day3N, day4D, day4N, day5D, day5N, day1TOT, day2TOT, day3TOT, day4TOT, '
    statement+= 'day5TOT FROM Mountain_Snow'

    # Sort by expected snowfall (greatest to least)
    resort_data = pd.read_sql_query(statement, conn).sort_values(by=['TotalExpected'], ascending=False)

    if resort_id!='All':
        # Select single resort
        resort_data = resort_data.iloc[resort_id]
        return(resort_data, scrape_date)
    else:
        # Set variable telling us which states/provinces are included
        stateANDProvince = resort_data.State.unique()

        region_vals = {}
        for k, v in region_options.items():
            region_vals[k] = [state for state in v if state in stateANDProvince]

        # Create text label for each resort on the map
        resort_data['text'] = resort_data.apply(text_label, axis=1)

        # Refine forecasted snowfall for each resort on the map
        resort_data['Forecast'] = resort_data.apply(snow_forecast, axis=1)

        # Close connection to database
        conn.close()

        return(resort_data, stateANDProvince, scrape_date, region_vals)

# Fetch the data
resort_data, stateANDProvince, scrape_date, region_vals = fetch_data()

# Boostrap CSS
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})

## Layouts
# Slider configuration
layout_slider = dict(
    min=10,
    max=100,
    step_size=10,
    value=50,
)
marks = range(layout_slider['min'],
            layout_slider['max']+layout_slider['step_size'],
            layout_slider['step_size'])
layout_slider['marks'] = {
        val:{'label':str(val),'style':{'font-size': '1.5em'}} for val in marks}

# Table configuration
layout_table = dict(
    autosize=True,
    height=500,
    width=900,
    font=dict(color='#191A1A', size='12'),
    titlefont=dict(color='#191A1A', size='14'),
    margin=dict(
        l=5,
        r=5,
        b=5,
        t=10
    ),
    hovermode='closest',
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
)
layout_table['padding-left']=50

# Map configuration
layout_map = dict(
    #autosize=True,
    height=500,
    font=dict(color='#191A1A'),
    title='<b>Predicted Snowfall for the Next 5 Days</b>',
    titlefont=dict(color='#191A1A', size='14'),
    margin=dict(
        l=5,
        r=0,
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
            lon=-110, # wVe, more is west
            lat=52.5 # nVs, more is north
        ),
        zoom=1.9,
    )
)

# Bar chart configurations
layout_indiv_bar = dict(
    height=400,
    width=400,
    barmode='group',
    xaxis=dict(
        showticklabels=True,
        tickangle=45,
        automargin=True,
        tickformat='%m/%d',
        tickmode='linear',
    ),
    yaxis= dict(
        title='Inches',
        automargin=True,
        rangemode='nonnegative',
        side='right'
    ),
    # margin=go.layout.Margin(
    #     #r=50,
    #     b=35
    # ),
    bargap=.25
)

layout_state_bar = dict(
    barmode='group',
    xaxis=dict(
        showticklabels=True,
        tickangle=45,
        automargin=True,
        tickformat='%m/%d',
        tickmode='linear',
    ),
    yaxis= dict(
        title='Inches',
        automargin=True,
        rangemode='nonnegative',
        side='left'
    ),
    bargap=.25
)

def gen_map(resort_data, location='USA-states'):

    cb = dict(
            title='Inches of Snow<br>Forecasted',
            len=.35,
            xpad=2,
            ticksuffix=' in.')

    return {
        'data': [{
                'type': 'scattermapbox',
                'locationmode':location,
                'lat': resort_data['Latitude'],
                'lon': resort_data['Longitude'],
                'hoverinfo': 'text',
                'hovertext': resort_data['text'],
                'mode': 'markers',
                'name': resort_data['MountainName'],
                'marker': {
                    'size':resort_data['TotalExpected'],
                    'opacity': 0.5,
                    'colorscale': 'Jet',
                    'reversescale': True,
                    'color': resort_data['TotalExpected'],
                    'colorbar': cb
                }
        }],
        'layout': layout_map
    }

app.layout = html.Div(
    [
        # Header
        html.Div(
        className='row',
        children=[
            html.Div(
                className='three columns',
                children=[
                    html.Div(
                        children=[
                            html.H1(
                                children='FreshyFinder'
                            ),
                            html.Div(
                                children='Last Updated: {}'.format(scrape_date),
                                style = {'fontSize': 14}
                            )
                        ],
                    ),
                ],
            ),
        ]),

        # Snowfall map + Individual bar chart
        html.Div(
            className='row',
            children=[
                html.Div(
                    className='eight columns',
                    children=[
                        html.Div(
                            children=dcc.Graph(id='snow-map',
                                    animate=True,
                                    style={'width': '100%'},
                                    figure=gen_map(resort_data)
                            )
                        )
                    ]
                ),
                html.Div(
                    className='three columns',
                    children=html.Div([
                        html.A([
                            html.Img(
                                id='resort_logo',
                                style={
                                    'height': '50%',
                                    'width': '50%',
                                    'padding-left': 135,
                                }
                            ),
                        ],
                        id='resort_link',
                        href='https://www.google.com'
                        ),
                        dcc.Graph(id='individual-bar',
                             style={
                                'display': 'inline-block',
                                 'width': 350,
                            }
                        )
                    ])
                )
            ]
        ),

        # Region radio buttons + State selector
        html.Div(
            [
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
                    className='six columns'
                ),
                html.Div(
                    [
                        html.P('Choose a State:'),
                        dcc.Dropdown(
                                id='state-value',
                                options=[{'label': i, 'value': i} for i in sorted(stateANDProvince)],
                                multi=True
                        ),
                    ],
                    className='five columns',
                    style={'margin-left': '75'}
                )
            ],
            style={'padding': 10},
            className='row'
        ),

        # Resort bar chart
        html.Div(
            [
                dcc.Graph(
                    id='resort-bar',
                    style={'margin-left': '10',
                            'margin-right': '10',
                            'margin-bottom':'10'}
                ),
            ], className='row'
        ),

        # Resort number slider
        html.Div(
            [
                #html.Div(className='two columns', style={'display': 'inline-block'}),
                html.Div([
                    html.P('Number of resorts to include:'),
                    dcc.Slider(
                        id='value-limit',
                        min=layout_slider['min'],
                        max=layout_slider['max'],
                        value=layout_slider['value'],
                        marks=layout_slider['marks'],
                        updatemode='drag'
                    )
                ],
                className='five columns',
                style={'display': 'inline-block',
                        'margin': 'auto',
                         'width': '30%',
                         'margin-bottom':'10',
                         'margin-left': '35%',
                         'margin-right':'35%'}
                )
            ], className='row'
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

        # Snowfall table
        html.Div(
            [
                dt.DataTable(
                    rows=resort_data.to_dict('records'),
                    columns=resort_data.columns,
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    id='snow-table',
                    column_widths = [230,230,230,230]),
            ],
            style = layout_table,
            className='row'
        ),

        # Contact info
        html.Div(
            [
                html.Div(
                    [
                        html.P('Developed by - ', style = {'display': 'inline'}),
                        html.A('Adam Jones', href = 'http://www.adam-p-jones.com')
                    ], className = 'twelve columns',
                       style = {'fontSize': 16, 'padding-bottom': 30}
                )
            ], className='row'
        ),
    ], className='ten columns offset-by-one')

# Create callbacks
# State drop-down selector
@app.callback(
    Output('state-value', 'options'),
    [Input('region-value', 'value')])
def set_regions(selected_region):
    return [{'label': i, 'value': i} for i in sorted(region_vals[selected_region])]

# Table
@app.callback(
    Output('snow-table', 'rows'),
    [Input('state-value', 'value'),
    Input('region-value', 'value'),
    Input('value-limit', 'value')])
def update_snow_table(state_or_province, selected_region, limit):
    resort_data, stateANDProvince, scrape_date, region = fetch_data()

    # Impose 'region' selection
    resort_data = resort_data.loc[resort_data['State'].isin(region[selected_region])]

    # Impose 'state' selection
    if state_or_province:
        # Check if state(s) are within the selected region (ignore, otherwise)
        if [i for i in state_or_province if i in region[selected_region]]:
            resort_data = resort_data.loc[resort_data['State'].isin(state_or_province)]

    # Sort
    resort_data = resort_data.sort_values(by=['TotalExpected'], ascending=False)
    # Filter
    resort_data = resort_data.iloc[0:limit]

    return resort_data.to_dict('records')

# # Map
# @app.callback(
#     Output('snow-map', 'figure'),
#     [Input('snow-table', 'rows'),
#      Input('snow-table', 'selected_row_indices')])
# def map_selection(rows, selected_row_indices):
#     aux = pd.DataFrame(rows)
#     temp_df = aux.ix[selected_row_indices, :]
#     if len(selected_row_indices) == 0:
#         return gen_map(aux)
#     return gen_map(temp_df)

# Map -> resort icon
@app.callback(
    dash.dependencies.Output('resort_logo', 'src'),
    [dash.dependencies.Input('snow-map', 'hoverData')])
def update_image_src(main_graph_hover):
    if main_graph_hover!=None:
        str_end = main_graph_hover['points'][0]['hovertext'].find(':')
        resort_name = main_graph_hover['points'][0]['hovertext'][:str_end]
        name_bool = resort_data['MountainName']==resort_name
        return resort_data['Icon'].loc[name_bool]
    else:
        return snowboard_img

# Map -> resort link
@app.callback(
    dash.dependencies.Output('resort_link', 'href'),
    [dash.dependencies.Input('snow-map', 'hoverData')])
def update_image_src(main_graph_hover):
    if main_graph_hover!=None:
        str_end = main_graph_hover['points'][0]['hovertext'].find(':')
        resort_name = main_graph_hover['points'][0]['hovertext'][:str_end]
        name_bool = resort_data['MountainName']==resort_name
        return resort_data['URL'].loc[name_bool]
    else:
        return 'https://opensnow.com/'

# Map -> individual bar graph
@app.callback(Output('individual-bar', 'figure'),
              [Input('snow-map', 'hoverData')])
def update_individual_bar(main_graph_hover):

    if main_graph_hover!=None:
        str_end = main_graph_hover['points'][0]['hovertext'].find(':')
        resort_name = main_graph_hover['points'][0]['hovertext'][:str_end]
        name_bool = resort_data['MountainName']==resort_name
        graph_data = resort_data.loc[name_bool]
        layout_indiv_bar['title'] = resort_name

        # Create list of dates for x-axis
        ts = datetime.datetime.strptime(scrape_date, '%Y-%m-%d')
        precip_forecast = graph_data['Forecast'].tolist()[0][0]

    else:
        layout_indiv_bar['title'] = 'Select resort<br>to see forecast'
        ts = datetime.datetime.today()
        precip_forecast = [0,0,0,0,0]

    # Create date list for x-axis
    date_list = [(ts + datetime.timedelta(days=x)) for x in range(1, numdays+1)]
    trace1 = go.Bar(
         x=date_list,
         y=precip_forecast
         )

    return {
    'data': [trace1],
    'layout': layout_indiv_bar
    }

# Resort bar graph
@app.callback(
    Output('resort-bar', 'figure'),
    [Input('snow-table', 'rows'),
     Input('snow-table', 'selected_row_indices'),
     Input('value-limit', 'value'),
     Input('state-value', 'value')])
def update_resort_bar(rows, selected_row_indices, limit, state_or_province):
    aux = pd.DataFrame(rows)
    if len(selected_row_indices) == 0:
        temp_df = aux
    else:
        temp_df = aux.ix[selected_row_indices, :]

    # Update title to include state selection
    if state_or_province:
        title = 'Snow Forecast for '+', '.join(state_or_province)
    else:
        title = str(limit)+' Mountains with the Most Predicted Snowfall'
    layout_state_bar['title'] = title

    trace1 = go.Bar(
      x=temp_df['MountainName'],
      y=temp_df['TotalExpected']
    )
    return {
      'data': [trace1],
      'layout': layout_state_bar
    }

# Forecast bar graph
@app.callback(
    Output('forecast-bar', 'figure'),
    [Input('snow-table', 'rows'),
     Input('snow-table', 'selected_row_indices')])
def update_forecast_bar(rows, selected_row_indices):

    if len(selected_row_indices) == 0:
        temp_df = pd.DataFrame(rows)
    else:
        temp_df = pd.DataFrame(rows).ix[selected_row_indices, :]

    graph_title = '{}-Day Forecasted Snowfall'.format(numdays)

    # Convert string to timestamp object
    ts = datetime.datetime.strptime(scrape_date, '%Y-%m-%d')

    # Create list of dates for x-axis
    date_list = [(ts + datetime.timedelta(days=x)) for x in range(1, numdays+1)]

    traces = []
    for index, row in temp_df.iterrows():
        row['Text'] = text_label(row)
        traces.append(go.Bar(
            x=date_list,
            y=row['Forecast'][0],
            text=row['Text'],
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
    )}

if __name__ == '__main__':
    app.run_server(debug=True)
