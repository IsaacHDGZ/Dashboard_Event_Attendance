import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import time
from streamlit_gsheets import GSheetsConnection
import json
from urllib.request import urlopen
#Title
st.title("Dashboard Event Attendance")
st.subheader("By José Isaac Hernández Gámez")
#Trend line graph builder
def trend_graph(dataframe_name,column_dates,date_originalFormat,date_newFormat):
    try:
        #Read the records
        interactions = pd.to_datetime(dataframe_name[column_dates].values, format=date_originalFormat)
        cleaned_interactions = interactions.strftime(date_newFormat)
        data_interaction = pd.DataFrame({'Dates': cleaned_interactions})
        #Set the range
        start_date = pd.to_datetime(cleaned_interactions.min())
        end_date = pd.to_datetime(cleaned_interactions.max())
        dates = pd.date_range(start_date,end_date).strftime(date_newFormat)
        date_range = pd.DataFrame({'Dates': dates})
        interaction_counts = data_interaction['Dates'].value_counts().sort_index()
        date_range["Records"] = date_range["Dates"].map(interaction_counts).fillna(0).astype(int)
        date_range["Dates"] = pd.to_datetime(date_range["Dates"])
        #set the trend line
        x = np.arange(len(date_range))
        y = date_range["Records"].values
        coefficients = np.polyfit(x, y, deg=1)
        trendline = np.polyval(coefficients, x)
        #Build the figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=date_range['Dates'], y=date_range['Records'], mode='lines+markers', name="Records"))
        # Add the trendline
        fig.add_trace(go.Scatter(x=date_range['Dates'], y=trendline, mode='lines', name="Trend Line", line=dict(dash="dot")))
        # Customize layout
        fig.update_layout(title="Records Trend Line",
                        xaxis_title="Dates",
                        yaxis_title="Records")
        containerTrend = st.container(border=True)
        containerTrend.plotly_chart(fig)
    except:
        print("Error")
#Data Frames
conn1 = st.connection("gsheets_preregistro", type=GSheetsConnection)
all_users = conn1.read(worksheet="RespuestasPRegistro").query("Duplicados != 'Duplicado'")
conn2 = st.connection("gsheets_pagosregistrados", type=GSheetsConnection)
paid_users = conn2.read(worksheet="RespuestasPago").query("Confirmado == 'si'")
#Display Data Frame for trend graph
columns_selected = paid_users[["Marca temporal","QRenviado","TipoDeUsuario","Folio"]]
containerDataTrend = st.container(border=True)
containerDataTrend.dataframe(columns_selected)
#Display trend graph #1
trend_graph_1 = trend_graph(paid_users,"Marca temporal","%d/%m/%Y %H:%M:%S","%Y-%m-%d")
#Display Data Frame for Map
users_count = all_users['Procedencia Final'].value_counts()
containerDataMap = st.container(border=True)
containerDataMap.dataframe(users_count)
#Display Map
with urlopen('https://raw.githubusercontent.com/angelnmara/geojson/refs/heads/master/mexicoHigh.json') as response:
    counties = json.load(response)
map_dataframe  = pd.DataFrame({
    "City": users_count.index,
    "Attendance": users_count.values,
})
fig = px.choropleth_map(map_dataframe, geojson=counties, locations="City", 
                           featureidkey="properties.name",
                           color="Attendance",
                           color_continuous_scale="Sunsetdark",
                           map_style="carto-positron",
                           zoom=3, center = {"lat": 23.6345, "lon": -102.5527},
                           opacity=0.5,
                           labels={'unemp':'unemployment rate'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)