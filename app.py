import pandas as pd
import plotly.express as px  # (version 4.7.0)
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
app = dash.Dash(__name__)
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

# print(df[:5])
# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.H1("台大校級交換人數 NTU Outbound Exchange", style={'text-align': 'center'}),
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
    html.Section (
        id="container",
        children=[
            html.Section(
                id="sum-stat-pane",
                className="pane",
                children=[
                    html.Div(className="sum_stat", children=[html.H1(id='one_sem_pct'), html.P("% 的學生交換一學期")]),
                    html.Div(className="sum_stat", children=[html.H1(id='num_students'), html.P("個學生參加交換")]),
                    html.Div(className="sum_stat", children=[html.H1(id='num_countries'), html.P("個國家")]),
                    html.Div(className="sum_stat", children=[html.H1(id='num_schools'), html.P("個學校")]),
                    # html.Div(className="sum_stat", id='num_students', children=[]),
                    # html.Div(className="sum_stat", id='num_countries', children=[]),
                    # html.Div(className="sum_stat", id='num_schools', children=[]),
                ]
            ),
            html.Div(className="pane", children=dcc.Graph(id='hist_year', figure={})),
            html.Div(className="pane", children=dcc.Graph(id='hist_country', figure={})),
            html.Div(className="pane", children=dcc.Graph(id='hist_school', figure={})),
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

    fig_year = px.histogram(dff, x="學年", title="{}歷年交換人數".format(slct_department), color_discrete_sequence=['#256ae5'])
    fig_year.update_layout(title_x=0.5, title_y=0.95, margin_l=20, margin_r=20, margin_t=50, margin_b=10)

    fig_country = px.histogram(dff, x='國家', title="{}學生前往交換國家".format(slct_department), color_discrete_sequence=['#256ae5'])
    fig_country.update_layout(title_x=0.5, title_y=0.95, margin_l=20, margin_r=20, margin_t=50)
    fig_country.update_xaxes(tickangle=315, categoryorder="total descending")

    fig_school = px.histogram(dff, x='學校', title="{}學生前往交換學校".format(slct_department), color_discrete_sequence=['#256ae5'])
    fig_school.update_layout(title_x=0.5, title_y=0.95, margin_l=20, margin_r=20, margin_t=50)
    fig_school.update_xaxes(tickangle=315, categoryorder="total descending")

    return one_sem_pct, num_students, num_countries, num_schools, fig_year, fig_country, fig_school
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.title = "NTU exchange stats"
    app.run_server(debug=True)
