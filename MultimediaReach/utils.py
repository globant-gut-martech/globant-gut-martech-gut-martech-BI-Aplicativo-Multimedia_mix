import pandas as pd
import streamlit as st


df_permutaciones = pd.read_csv("MultimediaReach/datasets/permutationIndex.csv")

df_frecuencias = pd.read_csv("MultimediaReach/datasets/frecuencias.csv")



def get_permutation_index(perm):
    try:
        filtered_permutation= df_permutaciones[df_permutaciones['Permutaciones'] == perm]['INDICES'].iloc[0]
        return float(filtered_permutation)
    except Exception as e:
        print(f"An error occurred: {e}")
    


def get_frecuencia(perm):
    try:
        filtered_frecuencia= df_frecuencias[df_frecuencias['Frecuencia de Alcance'] == perm]['proporcion'].values[0]
    except Exception as e:
        print(f"An error occurred: {e}")
    return float(filtered_frecuencia)


def first_row_calculation(df: pd.DataFrame, selected_freq: str):
    try:
     #Calcular el valor de la primera fila
     df.iloc[0, 2] = df.iloc[0,1]*get_frecuencia(selected_freq)
     df.iloc[0, 3] = df.iloc[0,1]*get_frecuencia(selected_freq)
    except Exception as e:
       print(f"An error occurred: {e}")
    return df

def alcance_standart_calculation(df: pd.DataFrame, selected_freq: str):
    try:
     #Calcular el valor de la segunda filaen adelante
     for i in range(1, len(df)):
            if (df.iloc[i,0] is not None) and (df.iloc[i,1] is not None):
                j=i-1
                previous_value = df.iloc[j, 2]  # Get value from the previous row in the same column
                adjustment = (100 - previous_value)/100 * df.iloc[i, 1] * get_frecuencia(selected_freq)
                df.iloc[i, 2] = previous_value + adjustment
            else:
                df.iloc[i,2] = None
     return df
    except Exception as e:
        print(f"An error occurred: {e}")

def index_dup(df: pd.DataFrame, selected_target: str):
    try:
        for i in range(1, len(df)):
            if (df.iloc[i,0] is not None) and (df.iloc[i,1] is not None):
                permutacion = selected_target + df.iloc[i,0]
                df.iloc[i,4] =get_permutation_index(permutacion)
            else:
                df.iloc[i,4] = None
        return df       
    except Exception as e:
        print(f"An error occurred: {e}")
    

def alcance_ajustado_calculation(df: pd.DataFrame, selected_freq: str):
    try:
     #Calcular el valor de la segunda filaen adelante
     for i in range(1, len(df)):
            if (df.iloc[i,0] is not None) and (df.iloc[i,1] is not None):
                j=i-1
                previous_value = df.iloc[j, 3]  # Get value from the previous row in the same column
                per1 = get_frecuencia(selected_freq)
                per2 = 100- df.iloc[i,4]
                per3 = (100-previous_value)/100
                df.iloc[i, 3] = previous_value +(1-per1*per2/100)*per3*df.iloc[i,1]
            else:
                df.iloc[i,3] = None
     return df
    except Exception as e:
       print(f"An error occurred: {e}")


def plot_preprocessing(df: pd.DataFrame, alcance : str):
    df['Porcentaje por medio'] = df[alcance] - df[alcance].shift()
    df['Porcentaje por medio'].iloc[0] = df[alcance].iloc[0]
    #Initialize the 'Medio acumulado' column
    df['Medios Acumulados'] = ''
     # Create the accumulated string
    df['Medios Acumulados'].iloc[0] = df['Medio'].iloc[0] 
    # Loop through each row to create the accumulated string from second row onwards
    for i in range(1,len(df)):
        df['Medios Acumulados'].iloc[i] = df['Medios Acumulados'].iloc[i-1] + '+' + df['Medio'].iloc[i]

    #Calculate the percentage of each medio
    for index,medio in enumerate(df['Medio']):
        df[medio] = 0
        df[medio].iloc[index:]=df['Porcentaje por medio'].iloc[index]
    
    df = df.loc[:, 'Medios Acumulados':]
    df = df.set_index('Medios Acumulados').stack(level=-1)
    df = df.reset_index()
    df.columns= ["Medios acumulados", "Medio", "Porcentaje"]
    return df


def create_annotations(start_df: pd.DataFrame, df2:pd.DataFrame, column: str):
    j=0
    annotations = []
    for i, row in start_df.iterrows():
        annotations.append(dict(x=6, 
                                y=df2['Medios acumulados'].iloc[j], 
                                text=str(round(row[column],2))+"%", 
                                font = dict(size=10, family="Arial Black", color = "black"),
                                #textangle=-90,
                                   showarrow=False))
        j+=len(start_df)
    return annotations
