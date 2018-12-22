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
    if row.Total==0.0:
        tot_str = ''
    else:
        tot_str = ': {1} in'
    out_str = '{0}'+tot_str+base_str+'<br>{3}'
    #out_str += '<br><a href="{4}">Link</a>' # , row.URL
    # out_str += '<br><img src="{5}" alt="Resort Logo">' # hovertext
    return out_str.format(row.MountainName, row.Total,
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

    statement = 'SELECT MountainName, State, Base, URL, Icon,'
    statement+= 'Total, Latitude, Longitude, day1D, day1N, day2D, day2N, day3D, '
    statement+= 'day3N, day4D, day4N, day5D, day5N, day1TOT, day2TOT, day3TOT, day4TOT, '
    statement+= 'day5TOT FROM Mountain_Snow'

    # Sort by expected snowfall (greatest to least)
    resort_data = pd.read_sql_query(statement, conn).sort_values(by=['Total'], ascending=False)

    if resort_id!='All':
        # Select single resort
        resort_data = resort_data.iloc[resort_id]
        return(resort_data, scrape_date)
    else:
        # # Rename columns for pretty tables
        # resort_data.rename(index=str, columns={'TOTAL': 'Total'}, inplace=True)

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

# Set up slider configuration
s_conf = dict(
    min=10,
    max=100,
    step_size=10,
    value=50)
marks=range(s_conf['min'],s_conf['max']+s_conf['step_size'],s_conf['step_size'])
s_conf['marks']={val:{'label':str(val),'style':{'font-size': '1.5em'}} for val in marks}

# Layouts
layout_table = dict(
    autosize=True,
    height=500,
    width=1000,
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
#layout_table['margin-top'] = '10'

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
    geode=dict(scope='north america'),
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
    bargap=.25
)

layout_individual_bar = dict(
    barmode='group',
    xaxis=dict(
        showticklabels=True,
        tickangle=45,
        tickformat='%m/%d',
        tickmode='linear',
        #fixedrange=True,
    ),
    yaxis= dict(
        side='right',
        title='Inches',
        automargin=True,
        rangemode='nonnegative'
    ),
    margin=go.layout.Margin(
        l=0,
        r=15,
        b=50
    ),
    bargap=.25
)

def gen_map(resort_data, colorbar=False, zoom=2, location='USA-states'):
    # groupby returns a dictionary mapping the values of the first field
    # 'classification' onto a list of record dictionaries with that
    # classification value.

    # if resort_data['MountainName'].empty:
    #     map_data = resort_data
    # else:
    #     map_data = resort_data[resort_data['MountainName'].isin(table_data['MountainName'])]

    # ## FIX THIS
    # layout_map['mapbox']['center']['lon'] = map_data['Longitude'].mean()
    # layout_map['mapbox']['center']['lat'] = map_data['Latitude'].mean()
    # layout_map['mapbox']['zoom'] = zoom

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
                'lat': resort_data['Latitude'],
                'lon': resort_data['Longitude'],
                'hoverinfo': 'text',
                'hovertext': resort_data['text'],
                'mode': 'markers',
                'name': resort_data['MountainName'],
                'marker': {
                    'size':resort_data['Total'],
                    'opacity': 0.5,
                    'colorscale': 'Jet',
                    'reversescale': True,
                    'color': resort_data['Total'],
                    'colorbar': cb
                }
        }],
        'layout': layout_map
    }

app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.Div(
                    [
                        html.H1(children='FreshyFinder'),
                        html.Div(children='Last Updated: {}'.format(scrape_date),
                                style = {'fontSize': 14,
                                        'padding-top': 0}
                        )
                    ],
                    className='three columns'
                ),
                # html.Img(
                #         src='https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Snowboarding.jpg/250px-Snowboarding.jpg',
                #         className='three columns',
                #         style={
                #             'height': '16%',
                #             'width': '16%',
                #             'float': 'right',
                #             'position': 'relative',
                #             'padding-top': 10,
                #             'padding-right': 30
                #         },
                # )
            ], className='row'
        ),

        # Snowfall map + Individual bar chart
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='snow-map',
                                animate=True,
                                style={'width': '100%'},
                                figure=gen_map(resort_data, colorbar=True)
                        )
                    ],
                    className='nine columns'
                ),
                html.Div(
                    [
                        html.A([
                            html.Img(
                                id='resort_logo',
                                # src='https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Snowboarding.jpg/250px-Snowboarding.jpg',
                                style={
                                    'height': '50%',
                                    'width': '50%',
                                    'float': 'center',
                                    #'position': 'relative',
                                    # 'padding-top': 10,
                                    #'padding-right': 30,
                                    'padding-left': 30
                                }),
                        ],
                        id='resort_link',
                        href='https://www.google.com'
                        ),
                        dcc.Graph(id='individual-bar',
                                style={'margin-left': '5',
                                    'margin-right': '5',
                                    'margin-bottom':'5'}
                        )
                    ],
                    className='three columns'
                ),
            ], className='row'
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
                    className='six columns',
                    style={'margin-top': '0'}
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
                    style={'margin-top': '0'}
                )
            ],
            className='row'
        ),

        # Resort bar chart
        html.Div(
            [
                dcc.Graph(
                    id='resort-bar',
                    style={'margin-left': '10', 'margin-right': '10',
                        'margin-bottom':'10'}
                    ),
            ], className='row'
        ),

        # Resort number slider
        html.Div(
            [
                html.Div([
                    html.P('Number of resorts to include:'),
                    dcc.Slider(
                        id='value-limit',
                        min=s_conf['min'],
                        max=s_conf['max'],
                        value=s_conf['value'],
                        marks=s_conf['marks'],
                        updatemode='drag'
                        )
                    ],
                    className='five columns',
                    style={'display': 'inline-block','margin': 'auto', 'width': '30%',
                        'margin-bottom':'10','margin-left': '5%',
                        'margin-right':'5%'}
                ),
                # html.Div([
                #     html.P('Number of days to forecast:'),
                #     dcc.Slider(
                #         id='value-days',
                #         min=s_conf['min'],
                #         max=s_conf['max'],
                #         value=s_conf['value'],
                #         marks=s_conf['marks'],
                #         updatemode='drag'
                #         )
                #     ],
                #     className='five columns',
                #     style={'display': 'inline-block','margin': 'auto', 'width': '30%',
                #         'margin-bottom':'10','margin-left': '5%',
                #         'margin-right':'5%'}
                # )
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

    resort_data = resort_data.sort_values(by=['Total'], ascending=False)
    resort_data = resort_data.iloc[0:limit]

    def hotlinker(url_string):
        return '<a href="{}">{}</a>'.format(url_string,url_string)
    resort_data['URL'] = resort_data['URL'].apply(hotlinker)

    return resort_data.to_dict('records')

# Main graph -> resort icon
@app.callback(
    dash.dependencies.Output('resort_logo', 'src'),
    [dash.dependencies.Input('snow-map', 'hoverData')])
def update_image_src(main_graph_hover):
    if main_graph_hover!=None:
        resort_pick = main_graph_hover['points'][0]['pointNumber']
        resort_data, scrape_date = fetch_data(resort_id=resort_pick)
        return resort_data['Icon']
    else:
        return snowboard_img

# Main graph -> resort link
@app.callback(
    dash.dependencies.Output('resort_link', 'href'),
    [dash.dependencies.Input('snow-map', 'hoverData')])
def update_image_src(main_graph_hover):
    if main_graph_hover!=None:
        resort_pick = main_graph_hover['points'][0]['pointNumber']
        resort_data, scrape_date = fetch_data(resort_id=resort_pick)
        return resort_data['URL']
    else:
        return 'https://opensnow.com/'

# Main graph -> individual graph
@app.callback(Output('individual-bar', 'figure'),
              [Input('snow-map', 'hoverData')])
def update_individual_bar(main_graph_hover):

    if main_graph_hover!=None:
        resort_pick = main_graph_hover['points'][0]['pointNumber']
        resort_data, scrape_date = fetch_data(resort_id=resort_pick)

        layout_individual_bar['title'] = resort_data['MountainName']

        # Create list of dates for x-axis
        ts = datetime.datetime.strptime(scrape_date, '%Y-%m-%d')
        precip_forecast = resort_data[['day1TOT', 'day2TOT', 'day3TOT', 'day4TOT', 'day5TOT']]
    else:
        layout_individual_bar['title'] = 'Select resort<br>to see forecast'
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
    'layout': layout_individual_bar
    }

@app.callback(
    Output('resort-bar', 'figure'),
    [Input('snow-table', 'rows'),
     Input('snow-table', 'selected_row_indices'),
     Input('value-limit', 'value'),
     Input('state-value', 'value')])
def update_resort_bar(rows, selected_row_indices, limit, state_or_province):

    # Impose table selections
    if len(selected_row_indices) == 0:
        temp_df = pd.DataFrame(rows)
    else:
        temp_df = pd.DataFrame(rows).ix[selected_row_indices, :]

    # Impose state selection
    if state_or_province:
        #resort_data = resort_data.loc[resort_data['State'].isin(state_or_province)]
        title = 'Snow Forecast for '+', '.join(state_or_province)
    else:
        title = str(limit)+' Mountains with the Most Predicted Snowfall'
    layout_state_bar['title'] = title

    trace1 = go.Bar(
        x=temp_df['MountainName'],
        y=temp_df['Total']
        )
    return {
    'data': [trace1],
    'layout': layout_state_bar
    }


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
