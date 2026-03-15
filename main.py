import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Algunos datos para tirar relleno de lista.
data = [
    {"Responsable": "DIR. PROV. DE PUERTOS", "Concepto": "Gastos en Personal", "Corrientes": 13751890027.08, "Capital": 0, "Financieras": 5355437595.11},
    {"Responsable": "DIR. PROV. DE PUERTOS", "Concepto": "Bienes y Servicios", "Corrientes": 3166333506.85, "Capital": 8396149248.84, "Financieras": 0},
    {"Responsable": "AGENCIA DE INNOVACIÓN", "Concepto": "Operativos e Insumos", "Corrientes": 9829004556, "Capital": 203555475, "Financieras": 0},
    {"Responsable": "AGENCIA DE INNOVACIÓN", "Concepto": "Servicios y Otros", "Corrientes": 4749572582, "Capital": 0, "Financieras": 0},
    {"Responsable": "INST. PROV. VIVIENDA", "Concepto": "Gestión y Sueldos", "Corrientes": 9442148173, "Capital": 700000000, "Financieras": 700000000},
    {"Responsable": "INST. PROV. VIVIENDA", "Concepto": "Obras y Viviendas", "Corrientes": 713033301, "Capital": 10895591658, "Financieras": 0},
]
df = pd.DataFrame(data)

df_melted = df.melt(
    id_vars=['Responsable'], 
    value_vars=['Corrientes', 'Capital', 'Financieras'],
    var_name='Clasificación', value_name='Monto'
).groupby(['Responsable', 'Clasificación']).sum().reset_index()

mapa_nombres = {'Corrientes': 'GASTOS CORRIENTES', 'Capital': 'GASTOS DE CAPITAL', 'Financieras': 'APLICACIONES FINANCIERAS'}
df_melted['Clasificación'] = df_melted['Clasificación'].map(mapa_nombres)

colores_corp = {'GASTOS CORRIENTES': '#2E5A88', 'GASTOS DE CAPITAL': '#4F81BD', 'APLICACIONES FINANCIERAS': '#95B3D7'}

# --- APP ---
app = dash.Dash(__name__)

app.layout = html.Div(style={'backgroundColor': '#1A1A1B', 'minHeight': '100vh', 'padding': '40px'}, children=[
    
    # Contenedor Principal (Max-width para que no se estire infinito)
    html.Div(style={'maxWidth': '1200px', 'margin': '0 auto'}, children=[
        
        html.H1("Gestión de Organismos Descentralizados", 
                style={'textAlign': 'center', 'color': '#FFFFFF', 'fontWeight': 'bold', 'marginBottom': '40px'}),

        # Gráfico Superior (Barras)
        html.Div([
            dcc.Graph(
                id='bar-chart-principal',
                figure=px.bar(
                    df_melted, y="Responsable", x="Monto", color="Clasificación",
                    orientation='h', title="<b>Ejecución Presupuestaria por Clasificación</b>",
                    color_discrete_map=colores_corp, template="plotly_dark"
                ).update_layout(
                    height=450, paper_bgcolor='#1A1A1B', plot_bgcolor='#1A1A1B',
                    margin=dict(l=20, r=20, t=60, b=20),
                    legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
                )
            )
        ], style={'marginBottom': '50px'}),

        # Sección Media: Filtro y Sunburst
        html.Div([
            html.Div([
                html.H3("Desglose Detallado", style={'color': '#95B3D7', 'marginBottom': '10px'}),
                html.P("Seleccione el organismo:", style={'color': '#ccc'}),
                dcc.Dropdown(
                    id='organismo-dropdown',
                    options=[{'label': i, 'value': i} for i in df['Responsable'].unique()],
                    value=df['Responsable'].unique()[0],
                    clearable=False,
                    style={'width': '100%', 'color': '#000'}
                ),
            ], style={'width': '35%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '5%'}),

            html.Div([
                dcc.Graph(id='sunburst-gastos')
            ], style={'width': '60%', 'display': 'inline-block'})
        ], style={'marginBottom': '60px', 'display': 'flex', 'alignItems': 'center'}),

        # Tabla inferior
        html.Div([
            html.H3("Resumen de Datos Ejecutados", style={'color': '#FFFFFF', 'marginBottom': '20px'}),
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_table={'borderRadius': '10px', 'overflow': 'hidden'},
                style_header={'backgroundColor': '#2E5A88', 'color': 'white', 'fontWeight': 'bold', 'textAlign': 'center'},
                style_cell={'backgroundColor': '#262626', 'color': '#eee', 'textAlign': 'center', 'padding': '12px', 'border': '1px solid #333'},
            )
        ])
    ])
])

@app.callback(
    Output('sunburst-gastos', 'figure'),
    [Input('organismo-dropdown', 'value')]
)
def update_sunburst(selected_org):
    df_filtered = df[df['Responsable'] == selected_org]
    fig = px.sunburst(
        df_filtered, path=['Responsable', 'Concepto'], values='Corrientes',
        title=f"Estructura de Gastos: {selected_org}",
        template="plotly_dark", color_discrete_sequence=['#4F81BD', '#2E5A88', '#95B3D7']
    )
    fig.update_layout(height=400, margin=dict(t=40, l=0, r=0, b=0), paper_bgcolor='#1A1A1B')
    return fig

if __name__ == '__main__':
    app.run(debug=True)
