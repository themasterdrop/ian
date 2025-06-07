
import pandas as pd
from flask import Flask
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Cargar los datos
file_id = "1PWTw-akWr59Gu7MoHra5WXMKwllxK9bp"
url = f"https://drive.google.com/uc?export=download&id={file_id}"
df = pd.read_csv(url)

# Clasificación por edad
def clasificar_edad(edad):
    if edad < 13:
        return "Niño"
    elif edad < 19:
        return "Adolescente"
    elif edad < 30:
        return "Joven"
    elif edad < 61:
        return "Adulto"
    elif edad < 200:
        return "Adulto mayor"

df['Rango de Edad'] = df['EDAD'].apply(clasificar_edad)

# Clasificación por días de espera
def clasificar_dias(dias):
    if dias < 10:
        return "0-9"
    elif dias < 20:
        return "10-19"
    elif dias < 30:
        return "20-29"
    elif dias < 40:
        return "30-39"
    elif dias < 50:
        return "40-49"
    elif dias < 60:
        return "50-59"
    elif dias < 70:
        return "60-69"
    elif dias < 80:
        return "70-79"
    elif dias < 90:
        return "80-89"
    else:
        return "90+"

df['RANGO_DIAS'] = df['DIFERENCIA_DIAS'].apply(clasificar_dias)

# Crear servidor Flask compartido
server = Flask(__name__)

# Ruta raíz
@server.route('/')
def index():
    return """<h2>Bienvenido</h2>
<p>Visita <a href="/edad/">/edad/</a> o <a href="/espera/">/espera/</a></p>"""

# App 1: Por Rango de Edad
app_edad = dash.Dash(__name__, server=server, url_base_pathname='/edad/')
app_edad.layout = html.Div([
    html.H1("Distribución por Rango de Edad"),
    dcc.Graph(id='histogram-edad', figure=px.histogram(
        df,
        x='Rango de Edad',
        category_orders={'Rango de Edad': ["Niño", "Adolescente", "Joven", "Adulto", "Adulto mayor"]},
        title='Distribución de edades de los pacientes del hospital María Auxiliadora',
        labels={'Rango de Edad': 'Rango de Edad'},
        template='plotly_white'
    )),
    dcc.Graph(id='pie-chart-edad', figure=px.pie(
        names=[], values=[], title="Seleccione una barra en el histograma"
    ))
])

@app_edad.callback(
    Output('pie-chart-edad', 'figure'),
    Input('histogram-edad', 'clickData')
)
def update_pie_chart_edad(clickData):
    if clickData is None:
        return px.pie(names=[], values=[], title="Seleccione una barra en el histograma", height=500)

    selected_range = clickData['points'][0]['x']
    filtered_df = df[df['Rango de Edad'] == selected_range].copy()

    top_especialidades = filtered_df['ESPECIALIDAD'].value_counts().nlargest(5)
    filtered_df['ESPECIALIDAD_AGRUPADA'] = filtered_df['ESPECIALIDAD'].apply(
        lambda x: x if x in top_especialidades.index else 'Otras'
    )

    grouped = filtered_df['ESPECIALIDAD_AGRUPADA'].value_counts().reset_index()
    grouped.columns = ['ESPECIALIDAD', 'CUENTA']
    return px.pie(
        grouped,
        names='ESPECIALIDAD',
        values='CUENTA',
        title=f"Top 5 Especialidades para el rango de edad '{selected_range}'",
        height=600
    )

# App 2: Por Rango de Días de Espera
app_espera = dash.Dash(__name__, server=server, url_base_pathname='/espera/')
app_espera.layout = html.Div([
    html.H1("Distribución por Tiempo de Espera"),
    dcc.Graph(id='histogram-espera', figure=px.histogram(
        df,
        x='RANGO_DIAS',
        category_orders={'RANGO_DIAS': ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90+"]},
        title='Distribución de la Cantidad de Pacientes según su Tiempo de Espera',
        labels={'RANGO_DIAS': 'Rango de Días'},
        template='plotly_white'
    )),
    dcc.Graph(id='pie-chart-espera', figure=px.pie(
        names=[], values=[], title="Seleccione una barra en el histograma"
    ))
])

@app_espera.callback(
    Output('pie-chart-espera', 'figure'),
    Input('histogram-espera', 'clickData')
)
def update_pie_chart_espera(clickData):
    if clickData is None:
        return px.pie(names=[], values=[], title="Seleccione una barra en el histograma", height=500)

    selected_range = clickData['points'][0]['x']
    filtered_df = df[df['RANGO_DIAS'] == selected_range].copy()

    top_especialidades = filtered_df['ESPECIALIDAD'].value_counts().nlargest(5)
    filtered_df['ESPECIALIDAD_AGRUPADA'] = filtered_df['ESPECIALIDAD'].apply(
        lambda x: x if x in top_especialidades.index else 'Otras'
    )

    grouped = filtered_df['ESPECIALIDAD_AGRUPADA'].value_counts().reset_index()
    grouped.columns = ['ESPECIALIDAD', 'CUENTA']
    return px.pie(
        grouped,
        names='ESPECIALIDAD',
        values='CUENTA',
        title=f"Top 5 Especialidades para el rango de espera '{selected_range}' días",
        height=600
    )

# Ejecutar el servidor
if __name__ == '__main__':
    server.run(debug=True)
