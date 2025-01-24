import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np



from utils import  (first_row_calculation, alcance_standart_calculation, index_dup,
                     alcance_ajustado_calculation, plot_preprocessing,create_annotations)


st. title("Multimedia Reach")
#Listas con los targets de referencia
targets = ["Personas", "Amas", "HM +25", "HM +25 nse 3-6", "HM +25 nse 2-3", 
           "HM +25 nse 4-6", "HM +18", "HM 12-24", "HM 25 -39"]
#Lista con las frecuencias de referencia
frecuencias_lst = ["1+", "2+", "3+", "4+" , "5+" , "6+" , "7+" ]
#Lista de medios
medios_lst =  ["Tv Nacional", "Tv Regional", "Tv Suscripción", "Radio", "Prensa", "Prensa OnLine",
               "Revistas", "Revistas On Line", "T. Digital", "Cine", "Google Search", "Facebook", 
                "Instagram", "Tik Tok", "Twitter", "Youtube", "Spotify", "Vallas", "Medios de Transporte",
                "Paraderos", "Valla Movil", "Taxi", "Centros Comerciales", "Aeropuertos"]

#Inicializacion del session state
widgets = {
    'selected_freq': "1+",  # Valor predeterminado para el campo de texto
    'selected_target': "Personas"  # Valor predeterminado para el slider
}
for widget_name, default_value in widgets.items():
    if widget_name not in st.session_state:
        st.session_state[widget_name] = default_value

#Ingreso de la frecuencia y el target
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Frecuencia de alcance")
    selected_freq = st.selectbox("Selecciona la frecuencia de alcance", frecuencias_lst)
with col2:
    st.markdown("### Target de referencia")
    selected_target = st.selectbox("Selecciona el target de referencia", targets)

#Define start dataframe
start_df= pd.DataFrame({"Medio":["Tv Nacional", "Radio", "Youtube"] , 
                        "Porcentaje": [41.0, 11.0,14.0],
                        "Alcance Multimedia Standart": [None, None,None],
                        "Alcance Multimedia Ajustado":[None, None,None],
                         "Indice de duplicación": [None, None, None] })
#First row calculations
start_df = first_row_calculation(start_df, selected_freq)
#Next rows calcularion
start_df = alcance_standart_calculation(start_df, selected_freq)
start_df = index_dup(start_df, selected_target)
start_df = alcance_ajustado_calculation(start_df, selected_freq)

    

if 'start_df' not in st.session_state:
    st.session_state['start_df'] = pd.DataFrame(start_df)
    #st.session_state['start_df']['Porcentaje'] = pd.to_numeric(st.session_state['start_df']['Porcentaje'], errors='coerce')
edited_df = st.data_editor(st.session_state['start_df'],
                           column_config={
                               "Medio": st.column_config.SelectboxColumn(
                                   "Medio",
                                   help="Medio de comunicación",
                                   options=medios_lst,
                                   default= medios_lst[0],
                                   width=150,
                               ),
                               "Porcentaje": st.column_config.NumberColumn(
                                   "Porcentaje",
                                   help="Porcentaje de alcance",
                                   min_value=0.0,
                                   max_value=100,
                                   #default=1,
                                   width=100,
                                   format= "%.2f"
                               ),
                               "Alcance Multimedia Standart": st.column_config.NumberColumn(
                                   "Alcance Multimedia Standart",
                                   help="Alcance standart",
                                   width=180,
                                   disabled= True,
                                   format= "%.2f"
                               ),
                               "Alcance Multimedia Ajustado": st.column_config.NumberColumn(
                                   "Alcance Multimedia Ajustado",
                                   help="Alcande ajustado",
                                   width=180,
                                   disabled=True,
                                   format= "%.2f"
                               ),
                               "Indice de duplicación": st.column_config.NumberColumn(
                                   "Indice de duplicación",
                                   help="Indice de duplicación",
                                   width=150,
                                   disabled=True,
                                   format= "%.2f",
                                   
                               )
                           },
                           hide_index=True,
                           column_order=("Medio", "Porcentaje", "Alcance Multimedia Standart", "Alcance Multimedia Ajustado"),
                           num_rows="dynamic")

if edited_df.empty:  
    st.stop()
elif edited_df.iloc[0,0] != None and edited_df.iloc[0,1] == None:
    st.session_state['start_df'] = edited_df
    st.stop()
else:
    if (st.session_state['start_df'] is not None) and ((not st.session_state['start_df'].equals(edited_df)) or ( st.session_state['selected_freq']!=selected_freq) or ( st.session_state['selected_target']!=selected_target)):
        st.session_state['start_df'] = edited_df
        st.session_state['selected_freq'] = selected_freq
        st.session_state['selected_target'] = selected_target
        st.session_state['start_df'] = first_row_calculation(st.session_state['start_df'], st.session_state['selected_freq'])
        st.session_state['start_df'] = alcance_standart_calculation(st.session_state['start_df'], st.session_state['selected_freq'])
        st.session_state['start_df'] = index_dup(st.session_state['start_df'], st.session_state['selected_target'])
        st.session_state['start_df'] = alcance_ajustado_calculation(st.session_state['start_df'], st.session_state['selected_freq'])
        st.rerun()


grafica = st.checkbox("Mostrar graficas")
if grafica:
    if  st.session_state['start_df']['Porcentaje'].isna().any():
        st.warning("Debe llenar todos los campos")
        st.stop()
    if  st.session_state['start_df']['Medio'].duplicated(keep=False).any():
        st.warning("No deben haber medios duplicados")
        st.stop()
    #Plots
    tab1, tab2 = st.tabs(["Alcance standart", "Alcance ajustado"])
    # Gráfico de barras
    with tab1:
        colors = px.colors.qualitative.Prism
        df2 = st.session_state['start_df'][['Medio', 'Alcance Multimedia Standart']]
        st.write(df2)
        df2 = plot_preprocessing(df2, 'Alcance Multimedia Standart')
        fig = px.bar(df2, y="Medios acumulados", x = "Porcentaje", color="Medio",
                    title='Alcance Multimedia Standart', orientation='h', text_auto=True,
                     color_discrete_sequence=colors)
        fig.update_traces(texttemplate='%{x:.2f}')
        fig.update_layout(yaxis={'categoryorder': 'total descending'},
                        xaxis=dict(range=[0, 100]),
                        xaxis_title='Porcentaje de alcance multimedia standart',
                        yaxis_title='Medios')
        annotations = create_annotations(st.session_state['start_df'], df2, 'Alcance Multimedia Standart')
        fig.update_layout(annotations=annotations)
        # Mostrar en streamlit
        st.plotly_chart(fig)

    with tab2:
        colors = px.colors.qualitative.Dark2
        df2 = st.session_state['start_df'][['Medio', 'Alcance Multimedia Ajustado']]
        df2 = plot_preprocessing(df2, 'Alcance Multimedia Ajustado')
        fig = px.bar(df2, y="Medios acumulados", x = "Porcentaje", color="Medio",
                    title='Alcance Multimedia Ajustado', orientation='h', text_auto=True,
                    color_discrete_sequence=colors)
        fig.update_traces(texttemplate='%{x:.2f}')
        fig.update_layout(yaxis={'categoryorder': 'total descending'},
                        xaxis=dict(range=[0, 100]),
                        xaxis_title='Porcentaje de alcance multimedia ajustado',
                        yaxis_title='Medios')
        annotations = create_annotations(st.session_state['start_df'], df2, 'Alcance Multimedia Ajustado')
        fig.update_layout(annotations=annotations)
        # Mostrar en streamlit
        st.plotly_chart(fig)


