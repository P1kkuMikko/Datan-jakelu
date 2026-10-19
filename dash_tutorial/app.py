"""
Dash in 20 Minutes -tutoriaali
Tämä sovellus yhdistää Dash-tutoriaalin keskeiset vaiheet:
1. Hello World & HTML-komponentit (html)
2. Datan lataaminen (Pandas & Gapminder-aineisto) ja esittäminen taulukkona (dash_table)
3. Datan visualisointi Plotly Express -kuvaajalla (dcc.Graph)
4. Vuorovaikutteisuus Callback-toiminnolla (@callback, Input, Output) ja ohjaimilla (dcc.RadioItems, dcc.Dropdown)
"""

from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

# 1. Ladataan Gapminderin vuoden 2007 maakohtainen aineisto
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv")

# 2. Alustetaan Dash-sovellus
app = Dash(__name__)

# 3. Määritellään sovelluksen ulkoasu (Layout)
app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "maxWidth": "1000px", "margin": "0 auto", "padding": "20px"},
    children=[
        html.H1(
            children="Ensimmäinen Dash-sovellukseni: Datan visualisointi ja ohjaimet",
            style={"textAlign": "center", "color": "#2c3e50"}
        ),
        html.P(
            children="Tämä sovellus pohjautuu Dashin 'Dash in 20 Minutes' -tutoriaaliin. "
                     "Voit suodattaa maanosia ja valita tarkasteltavan mittarin.",
            style={"textAlign": "center", "color": "#555"}
        ),
        html.Hr(),

        # Ohjaimet (Controls): Maanosan suodatus ja mittarin valinta
        html.Div(
            style={"display": "flex", "gap": "40px", "marginBottom": "20px", "backgroundColor": "#f8f9fa", "padding": "15px", "borderRadius": "8px"},
            children=[
                html.Div(
                    style={"flex": "1"},
                    children=[
                        html.Label("1. Valitse tarkasteltava mittari (Y-akseli):", style={"fontWeight": "bold"}),
                        dcc.RadioItems(
                            options=[
                                {"label": "Eliniänodote (lifeExp)", "value": "lifeExp"},
                                {"label": "Väkiluku (pop)", "value": "pop"},
                                {"label": "BKT asukasta kohden (gdpPercap)", "value": "gdpPercap"},
                            ],
                            value="lifeExp",
                            id="controls-and-radio-item",
                            style={"marginTop": "8px"}
                        ),
                    ]
                ),
                html.Div(
                    style={"flex": "1"},
                    children=[
                        html.Label("2. Suodata maanosan mukaan:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            options=[{"label": "Kaikki maanosat", "value": "ALL"}] + [
                                {"label": c, "value": c} for c in sorted(df["continent"].unique())
                            ],
                            value="ALL",
                            clearable=False,
                            id="continent-dropdown",
                            style={"marginTop": "8px"}
                        ),
                    ]
                ),
            ]
        ),

        # Interaktiivinen kuvaaja (Graph)
        dcc.Graph(figure={}, id="controls-and-graph"),

        html.H3("Aineisto taulukkomuodossa (DataTable)", style={"marginTop": "30px"}),
        # Interaktiivinen taulukko (DataTable)
        dash_table.DataTable(
            id="data-table",
            data=df.to_dict("records"),
            page_size=8,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px"},
            style_header={"backgroundColor": "#2c3e50", "color": "white", "fontWeight": "bold"}
        ),
    ]
)


# 4. Callback-funktio, joka yhdistää ohjaimet (Input) kuvaajaan ja taulukkoon (Output)
@callback(
    Output(component_id="controls-and-graph", component_property="figure"),
    Output(component_id="data-table", component_property="data"),
    Input(component_id="controls-and-radio-item", component_property="value"),
    Input(component_id="continent-dropdown", component_property="value")
)
def update_view(col_chosen, continent_chosen):
    # Suodatetaan data valitun maanosan perusteella
    if continent_chosen == "ALL":
        filtered_df = df
        title_suffix = "kaikissa maanosissa"
    else:
        filtered_df = df[df["continent"] == continent_chosen]
        title_suffix = f"maanosassa {continent_chosen}"

    # Luodaan histogrammi (keskiarvo maanosittain tai maittain)
    if continent_chosen == "ALL":
        fig = px.histogram(
            filtered_df,
            x="continent",
            y=col_chosen,
            histfunc="avg",
            color="continent",
            title=f"Keskimääräinen {col_chosen} {title_suffix} (Gapminder 2007)"
        )
    else:
        fig = px.bar(
            filtered_df.sort_values(by=col_chosen, ascending=False).head(15),
            x="country",
            y=col_chosen,
            color="country",
            title=f"Top 15 maata mittarilla {col_chosen} {title_suffix} (Gapminder 2007)"
        )

    return fig, filtered_df.to_dict("records")


# 5. Sovelluksen käynnistys
if __name__ == "__main__":
    app.run(debug=True)
