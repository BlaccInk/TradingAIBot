import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# 1. Initialize app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

header_height, footer_height = "6rem", "10rem"
sidebar_width, adbar_width = "12rem", "12rem"

HEADER_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "right": 0,
    "height": header_height,
    "padding": "2rem 1rem",
    "background-color": "white",
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": header_height,
    "left": 0,
    "bottom": footer_height,
    "width": sidebar_width,
    "padding": "1rem 1rem",
    "background-color": "Lightgreen",
}

ADBAR_STYLE = {
    "position": "fixed",
    "top": header_height,
    "right": 0,
    "bottom": footer_height,
    "width": adbar_width, 
    "padding": "1rem 1rem",
    "background-color": "lightblue",
}

CONTENT_STYLE = {
    "margin-top": header_height,
    "margin-left": sidebar_width,
    "margin-right": adbar_width,
    "margin-bottom": footer_height,
    "padding": "1rem 1rem", 
}

FOOTER_STYLE = {
    "position": "fixed",
    "bottom": 0,
    "left": 0,
    "right": 0,
    "height": footer_height,
    "padding": "2rem 1rem",
    "background-color": "lightgray",
}

header = html.Div([
    html.H2("Trading AI Dashboard")], style=HEADER_STYLE
    )

fdivs = [html.H2("footer")]
for f in range(5):
    fdivs.append(html.P(f'Footer line {f}'))
footer = html.Div(fdivs, style=FOOTER_STYLE)

adbar = html.Div([
    html.H2("Adbar"),
    html.P("Advertisements Go Here")], style=ADBAR_STYLE
    )

sidebar = html.Div([
    html.H2("Sidebar"),
    html.Hr(),
    html.P("A Simple sidebar layout with navigation links", className="Lead"),
    dbc.Nav([
        dbc.NavLink("Page 1", href="/page-1", id="page-1-Link"),
        dbc.NavLink("Page 2", href="/page-2", id="page-2-Link"),
        dbc.NavLink("Page 3", href="/page-3", id="page-3-Link"),
    ], vertical=True, pills=True,
    )],
        style =SIDEBAR_STYLE
)
# 2. Mock Data
df = pd.DataFrame({
    "Category": ["A", "B", "C"], 
    "Values": [10, 25, 15]})

# 3. Layout (Frontend definition in Python)
app.layout = html.Div([
    header,
    sidebar,
    adbar,
    html.Div([
        html.H1("Interactive Trading Dashboard"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.Label("Select Category:"),
                dcc.Dropdown(
                    id='selector', 
                    options=[{'label': i, 'value': i} for i in df['Category']], 
                    value='A',
                    style={"width": "100%"}
                ),
            ], width=12),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='main-graph')
            ], width=12),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.Label("Select Multiple Categories:"),
                dcc.Checklist(
                    id='multi-selector',
                    options=[{'label': f" {i}", 'value': i} for i in df['Category']],
                    value=['A'],
                    style={"display": "flex", "gap": "2rem"}
                ),
            ], width=12),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='multi-graph')
            ], width=12),
        ]),
    ], style=CONTENT_STYLE),
    footer,
])

#4. Interactivity (Callbacks)
@app.callback(Output('main-graph', 'figure'), [Input('selector', 'value')])
def update_graph(selected_val):
    filtered_df = df[df['Category'] == selected_val]
    return px.bar(filtered_df, x='Category', y='Values', title=f'Values for Category {selected_val}')

@app.callback(Output('multi-graph', 'figure'), [Input('multi-selector', 'value')])
def update_multi_graph(selected_vals):
    if not selected_vals:
        selected_vals = ['A']
    filtered_df = df[df['Category'].isin(selected_vals)]
    return px.bar(filtered_df, x='Category', y='Values', title='Values for Selected Categories')

if __name__ == '__main__':
    app.run_server(debug=True)