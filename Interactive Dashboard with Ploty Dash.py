import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(id='site-dropdown', options=[
        {'label': 'All sites', 'value': 'ALL'},
        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
    ], value='ALL', placeholder='Select a Launch Site here', searchable=True),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider', min=min_payload, max=max_payload, step=1000, value=[min_payload, max_payload],
                    marks={str(min_payload): {'label': str(min_payload), 'style': {'transform': 'rotate(-45deg)'}},
                           str(max_payload): {'label': str(max_payload), 'style': {'transform': 'rotate(-45deg)'}}}),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value')]
)
def update_pie_chart(entered_site):
    if entered_site == 'ALL':
        pie_chart_data = spacex_df['Launch Site'].value_counts()
        names = pie_chart_data.index.tolist()
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        pie_chart_data = filtered_df['class'].value_counts()
        names = ['Success', 'Failed']
    fig = px.pie(
        pie_chart_data,
        values=pie_chart_data.values,
        names=names,
        title='Total Successful Launches by Site' if entered_site == 'ALL' else f'Success vs. Failed for {entered_site}'
    )

    # Save the pie chart as an HTML file
    fig.write_html("success_pie_chart.html")

    return fig

# Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

    min_payload, max_payload = payload_range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= min_payload) & (filtered_df['Payload Mass (kg)'] <= max_payload)]
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload vs. Success for All Launch Site' if selected_site == 'ALL' else f'Payload vs. Success for {selected_site}'
    )

    # Save the scatter chart as an HTML file
    fig.write_html("success_payload_scatter_chart.html")

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
