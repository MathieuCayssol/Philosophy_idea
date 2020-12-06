import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import pathlib
import ast

import plotly.graph_objects as go

from app import app

#Read csv file

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../").resolve()

df_link = pd.read_csv(DATA_PATH.joinpath("df_linked.csv"))
df_brut = pd.read_csv(DATA_PATH.joinpath("philo_brut.csv"), index_col=0)
df_simi = pd.read_csv(DATA_PATH.joinpath("simi_matrix.csv"), index_col=0)
#df_PCA = pd.read_csv("PCA.csv", index_col=0)



t_1 = []
t_2 = []
for i in range(0, len(df_link)):
    t_1.append(ast.literal_eval(df_link['influences'][i]))
    t_2.append(ast.literal_eval(df_link['influenced'][i]))

df_link['influences'] = t_1
df_link['influenced'] = t_2


t_3 = []
t_4 = []
for i in range(0, len(df_brut)):
    t_3.append(ast.literal_eval(df_brut['influences'][i]))
    t_4.append(ast.literal_eval(df_brut['influenced'][i]))

df_brut['influences'] = t_3
df_brut['influenced'] = t_4



divs = []
text_choice = []
nb_sub=0
text=0



# The Layout

layout = html.Div(id="general_dash_app", className='container-fluid', children=[
dbc.Row(className='',children=[
    dbc.Col(html.Div(id="left_menu", children=[
        dbc.FormGroup(
        [
            dbc.Label("Select a philosopher", html_for="choice_philosopher", style={
                'color': '#e3e3e3',
                'font-size': '1.8em'
            }),
            dcc.Dropdown(
                id="dropdown_select_philo",
                options=[
                    {"label": df_link.iloc[i]['Philosopher Name'], "value": df_link.iloc[i]['Philosopher Name']} for i in range(0, len(df_link))
                ],
            )
        ]
    ),
    html.Div(id="my-output", children=divs)
    ]), md=5, id="first_col"),
    
    
    dbc.Col(html.Div(id="subject_select", children=[
        dbc.FormGroup(
        [
            dbc.Label("Select a subject (number) :", html_for="choice_subject", style={
                'color': 'black',
                'font-size': '1.8em',
                'display': 'inline-block'
            }),
            dcc.Dropdown(
                id="dropdown_select_subject"
            )
        ]
    ),
    html.Div(id="div_text_choice", children=text_choice),
    html.Div(id="top_three_topic"),
    html.Div(id='graph-link-text'),
    html.Div(id='wiki-link-text')
    ]),md=7)
]
)
])


@app.callback(
    Output(component_id='my-output', component_property='children'),
    [Input(component_id='dropdown_select_philo', component_property='value')]
)
def update_output_div(input_value):
    name_p = list(df_link.loc[df_link['Philosopher Name'] == input_value, 'Name'])
    if (len(name_p)>=1):
        text = df_brut.loc[df_brut['Philosopher'] == name_p[0]]['Idea']
        name = df_brut.loc[df_brut['Philosopher'] == name_p[0]]['Title']
        text = text.reset_index(drop=True)
        name = name.reset_index(drop=True)
        divs = []
        divs.append(html.H3("We found "+str(len(name))+" results :"))
        for i in range(0, len(text)):
            divs.append(html.H2(str(i+1)+") "+name[i]))
            divs.append(html.P(text[i]))
        global var_test
        var_test = df_brut.loc[df_brut['Philosopher'] == name_p[0]]['Idea'].index
    else:
        divs = []
    return divs



@app.callback(
    Output(component_id='dropdown_select_subject', component_property='options'),
    [Input(component_id='my-output', component_property='children')]
)
def update_subject(input):
    if(input):
        calc = int(len(input)/2) +1
        return [{'label': i, 'value': i} for i in range(1, calc)]
    else:
        return []


@app.callback(
    [Output('top_three_topic', 'children'), Output('graph-link-text', 'children'), Output('wiki-link-text', 'children')],
    [Input(component_id='dropdown_select_subject', component_property='value')]
)
def create_fig(input):
    if(input):

        #Core algorithm for 

        ind_text = var_test[input-1]
        text_for_node = []
        N = 160 #30 better
        l = list(df_simi.iloc[ind_text].argsort()[-N:][::-1])
        text_for_node.append(l[0])
        current_p = df_brut['Philosopher'][ind_text]
        #print(current_p)
        #print(df_linked.loc[df_linked['Name'] == current_p]['influenced'].values[0])
        j=0
        stop = 0
        while(j<N and stop<15):
            if (df_brut['Philosopher'][l[j]] in df_link.loc[df_link['Name'] == current_p]['influenced'].values[0] or df_brut['Philosopher'][l[j]] in df_link.loc[df_link['Name'] == current_p]['influences'].values[0]):
                text_for_node.append(l[j])
                stop+=1
            j+=1
        

        print(text_for_node)

        # Create a DataFrame for the network

        df_sliced = pd.DataFrame()
        df_sliced = df_brut.iloc[text_for_node[0:]]
        df_sliced['index'] = [text_for_node[i] for i in range(0, len(text_for_node))]
        df_sliced = df_sliced.reset_index(drop=True)

        # Real name and Birth name
        phil_name = []
        phil_birth = []
        for i in range(0, len(df_sliced)):
            if(df_sliced['Philosopher'][i] in list(df_link['Name'])):
                phil_name.append(df_link.loc[df_link['Name'] == df_sliced['Philosopher'][i], 'Philosopher Name'].values[0])
                phil_birth.append(df_link.loc[df_link['Name'] == df_sliced['Philosopher'][i], 'Birth'].values[0])
            else:
                phil_name.append(str(df_sliced['Philosopher'][i])[30:])
                phil_birth.append(None)
        df_sliced['Philosopher Name'] = phil_name
        df_sliced['Birth'] = phil_birth

        #print(df_sliced['Philosopher'])
        #Add edges between each nodes

        all_edge = []
        for x in df_sliced['Philosopher']:
            for i in range(0, len(df_sliced)):
                if ((x in df_sliced['influences'][i]) or (x in df_sliced['influenced'][i])):
                    a = df_sliced.loc[df_sliced['Philosopher'] == x, 'Birth'].values[0]
                    b = df_sliced['Birth'][i]
                    all_edge += [(a, b)]


        # Figure construction

        X_data = [x for x in df_sliced['Birth']]
        Y_data = [0 for x in range(0, len(X_data))]
        text_plot = [x for x in df_sliced['Philosopher Name']]
        color_plot = ['black' for x in range(0, len(X_data))]
        color_plot[0] = 'red'
        for i in range(0, len(df_sliced)):
            text_plot[i] += ", "+df_sliced['Title'][i]


        

        fig = go.Figure(data={'hoverinfo': 'text',
                            'x': X_data,
                            'y': Y_data,
                            'text': text_plot,
                            'marker': {'size': 15,
                                        'color': color_plot,
                                        'line': {'width': 2,
                                                'color' : 'white'},
                                        },
                            
                            'mode': 'markers',
                            'marker_symbol': 'circle'
                            })

        x0_date=[]
        y0_date=[]
        x1_date=[]
        y1_date=[]

        for x in all_edge:
            if(x[0]<x[1]):
                y_pyth=(x[1]-x[0])/2
                x0_date.append(x[0])
                x1_date.append(x[1])
                y0_date.append(-y_pyth)
                y1_date.append(y_pyth)
            elif(x[0]>x[1]):
                y_pyth=(x[0]-x[1])/2
                x0_date.append(x[1])
                x1_date.append(x[0])
                y0_date.append(y_pyth)
                y1_date.append(-y_pyth)

        for i in range(0,len(x0_date)):
            fig.add_shape(type="circle",
                xref="x", yref="y",
                x0=x0_date[i], y0=y0_date[i], x1=x1_date[i], y1=y1_date[i],
                line_color="black",
                line_width=0.5
            )

        fig.update_layout(
            xaxis_title="Time Scale (in year)"
                )
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))
        
        # Set axes properties
        fig.update_xaxes(range=[min(X_data)-0.1*(max(X_data)-min(X_data)), max(X_data)+0.1*(max(X_data)-min(X_data))], zeroline=False, tickangle=45)
        fig.update_yaxes(range=[-0.0035*(max(X_data)-min(X_data)), (max(X_data)-min(X_data))/2], zeroline=False, showgrid=False)

        # Add circles


        # Set figure size
        fig.update_layout(height=500, yaxis=dict(visible=False))

        one_h4 = "No Result"
        two_h4 = "No Result"
        three_h4 = "No Result"
        h4_birth = []
        my_N = 4

        if(len(X_data) < 4):
            my_N = len(X_data)
    
        for i in range(1,my_N):
            if (X_data[i]==X_data[i]):
                h4_birth.append(str(int(X_data[i])))
            else:
                h4_birth.append("?")

        if(len(df_sliced) == 2):
            one_h4 = df_sliced['Philosopher Name'][1]+", "+df_sliced['Title'][1]+" (born in "+h4_birth[0]+")"
        elif(len(df_sliced) == 3):
            one_h4 = df_sliced['Philosopher Name'][1]+", "+df_sliced['Title'][1]+" (born in "+h4_birth[0]+")"
            two_h4 = df_sliced['Philosopher Name'][2]+", "+df_sliced['Title'][2]+" (born in "+h4_birth[1]+")"
        elif(len(df_sliced) > 3):
            one_h4 = df_sliced['Philosopher Name'][1]+", "+df_sliced['Title'][1]+" (born in "+h4_birth[0]+")"
            two_h4 = df_sliced['Philosopher Name'][2]+", "+df_sliced['Title'][2]+" (born in "+h4_birth[1]+")"
            three_h4 = df_sliced['Philosopher Name'][3]+", "+df_sliced['Title'][3]+" (born in "+h4_birth[2]+")"

        return [html.Div(children=[html.H3(id="h3_top_three",children=["Top 3 related Topics :"]), 
        html.H4(one_h4), html.H4(two_h4), html.H4(three_h4)]), 
        html.Div(children=[dcc.Graph(figure=fig), html.P('An arc represents a link of influence between two philosophers'),
        html.P('A dot represents the birth of a philosopher (red for the chosen philosopher)')]), 
        html.Div([html.A("> Wikipedia link to "+ df_sliced['Philosopher Name'][i]+" page's about "+df_sliced['Title'][i], href=df_brut['Philosopher'][df_sliced['index'][i]], target="_blank") for i in range(1, len(df_sliced))])
        ]
    else:
        return [None, None, None]

#[html.P("You have selected the subject : "+df_brut['Title'].iloc[var_test[input-1]])]