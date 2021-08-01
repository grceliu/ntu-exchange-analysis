import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objs as go
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
                {"name": "keywords", "content": "台灣大學, 校級, 交換, 統計, 人數"}]
)
app.title = "NTU exchange stats"
server = app.server

MAIN_COLOR = '#256ae5'

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)
df = pd.read_csv("./data/ntu_exchange.csv")
df = df.dropna()
df["學年"] = df["學年"].map(lambda x: int(x[:-2]))
years = df["學年"].sort_values(ascending=False).unique()

faculties = df["學院"].unique()
faculties_option = [{"label": faculty, "value": faculty} for faculty in faculties]

departments = df["學系"].unique()
departments_option = [{"label": dept, "value": dept} for dept in departments]

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div(
    className="page",
    children= [
        html.H1("台大校級交換人數", style={'text-align': 'center'}),
        html.Div(
            children=[
                dcc.RangeSlider(id="slct_year",
                                min=years[-1],
                                max=years[0],
                                step=1,
                                marks={str(year): str(year) for year in years},
                                value=[years[-1], years[0]]
                                )
            ],
            style={"width": "60%", "margin": "auto", "align-items": "center", "justify-content": "center"},
        ),
        html.Div(
            children=[
                dcc.Dropdown(id="slct_department",
                            options=departments_option,
                            multi=False,
                            value="經濟學系",
                            )
            ],
            style={"width": "30%", "margin": "auto", "align-items": "center", "justify-content": "center"},
        ),
        html.Div(
            className="pane-grid",
            children=[
                html.Div(
                    className="pane stats-grid",
                    children=[
                        html.Div(className="stats-card", children=[html.H1(id='one_sem_pct'), html.P("% 的學生交換一學期")]),
                        html.Div(className="stats-card", children=[html.H1(id='num_students'), html.P("個學生參加交換")]),
                        html.Div(className="stats-card", children=[html.H1(id='num_countries'), html.P("個國家")]),
                        html.Div(className="stats-card", children=[html.H1(id='num_schools'), html.P("個學校")]),
                    ]
                ),
                html.Div(className="pane", children=dcc.Graph(style={'height': '100%', 'width': '100%', 'max-height': '250px', 'max-width': '600px'}, id='hist_year', figure={}, responsive=True, config={'displayModeBar': False})),
                html.Div(className="pane", children=dcc.Graph(style={'height': '100%', 'width': '100%', 'max-height': '250px', 'max-width': '600px'}, id='hist_country', figure={}, responsive=True, config={'displayModeBar': False})),
                html.Div(className="pane", children=dcc.Graph(style={'height': '100%', 'width': '100%', 'max-height': '250px', 'max-width': '600px'}, id='hist_school', figure={}, responsive=True, config={'displayModeBar': False})),
            ]
        )
])
# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='one_sem_pct', component_property='children'),
     Output(component_id='num_students', component_property='children'),
     Output(component_id='num_countries', component_property='children'),
     Output(component_id='num_schools', component_property='children'),
     Output(component_id='hist_year', component_property='figure'),
     Output(component_id='hist_country', component_property='figure'),
     Output(component_id='hist_school', component_property='figure'),
     ],
    [Input(component_id='slct_year', component_property='value'),
     Input(component_id='slct_department', component_property='value')]
)
def update_graph(slct_year, slct_department):
    # dataframe
    dff = df.copy()
    dff = dff[(dff["學年"]>=slct_year[0]) & (dff["學年"]<=slct_year[1]) & (dff["學系"]==slct_department)]

    one_sem_pct = int(round((len(dff[dff["學期"]=="一學期"]) / len(dff))*100))
    num_students = len(dff)
    num_countries = dff["國家"].nunique()
    num_schools = dff['學校'].nunique()

    fig_year = px.histogram(dff, x="學年", title="{}歷年交換人數".format(slct_department), color_discrete_sequence=[MAIN_COLOR])
    fig_year.update_layout(title_x=0.5, title_y=0.95, margin_l=20, margin_r=20, margin_t=35, margin_b=10)
    fig_year.update_xaxes(fixedrange=True)
    fig_year.update_yaxes(fixedrange=True)

    fig_country = px.histogram(dff, x='國家', title="{}學生前往交換國家".format(slct_department), color_discrete_sequence=[MAIN_COLOR])
    fig_country.update_layout(title_x=0.5, title_y=0.95, margin_l=20, margin_r=20, margin_t=35, margin_b=10)
    fig_country.update_xaxes(tickangle=315, categoryorder="total descending", fixedrange=True)
    fig_country.update_yaxes(fixedrange=True)

    fig_school = px.histogram(dff, x='學校', title="{}學生前往交換學校".format(slct_department), color_discrete_sequence=[MAIN_COLOR])
    fig_school.update_layout(title_x=0.5, title_y=0.95, margin_l=20, margin_r=20, margin_t=35, margin_b=10)
    fig_school.update_xaxes(tickangle=315, categoryorder="total descending", fixedrange=True)
    fig_school.update_yaxes(fixedrange=True)

    return one_sem_pct, num_students, num_countries, num_schools, fig_year, fig_country, fig_school

if __name__ == '__main__':
    app.run_server(debug=True)
