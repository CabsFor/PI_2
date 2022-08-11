import pandas as pd
import streamlit as st
import altair as alt
#import requests
import pydeck as pdk
from datetime import date, datetime
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="COVID 19 en Estados Unidos")

#response = requests.get('https://healthdata.gov/resource/g62h-syeh.json?$limit=50000&$offset=0').json()
#response = json.dumps(response)
#df = pd.read_json(response)

df = pd.read_csv('COVID-19_Reported_Patient_Impact_and_Hospital_Capacity_by_State_Timeseries.csv')
df['date'] = pd.to_datetime(df['date'])
df34 = pd.read_csv('statelatlong.csv')
Estados1 = df34.sort_values(by='State')
#df['state'] = df['state'].replace(Estados1.State.values,Estados1.City.values)
df_map1 = pd.read_csv('df_map1.csv',sep='\t')
# State Latitude Longitude City inpatient_beds_used_covid total_camas_UCI_COVID

###################### MAPA #####################################

view_state = pdk.ViewState(latitude=38.498779,
                           longitude=-98.320078,
                           zoom=4,
                           pitch=0)

tooltip = {
    "html":
        "<b>Ciudad:</b> {City} <br/>"
        "<b>Hospitalizados debido al COVID-19 :</b> {inpatient_beds_used_covid} Casos <br/>"
        "<b>Uso de camas UCI por pacientes COVID-19 :</b> {total_camas_UCI_COVID} camas <br/>",
    "style": {
        "backgroundColor": "steelblue",
        "color": "black",
    }
}

slayer = pdk.Layer(
    type='ScatterplotLayer',
    data=df_map1,
    pickable=True,
    get_position=["Longitude", "Latitude"],
    get_radius=1000,
    get_line_color=[75, 65, 148],
    get_line_width=4000,
    stroked=True,
    onClick=True,
    filled=True,
    line_width_min_pixels=50,
    opacity=0.5,
)

layert1 = pdk.Layer(
    type="TextLayer",
    data=df_map1,
    pickable=True,
    get_position=["Longitude", "Latitude"],
    get_text="City",
    get_size=18,
    sizeUnits='meters',
    get_color=[0, 0, 0],
    get_angle=0,
    getTextAnchor= '"middle"',
    get_alignment_baseline='"center"'
)

pp = pdk.Deck(
    initial_view_state=view_state,
    map_provider='mapbox',
    map_style=pdk.map_styles.MAPBOX_ROAD,
    layers=[
        slayer,
        layert1,
    ],
    tooltip=tooltip
)

deckchart = st.pydeck_chart(pp)

####################### BARRA LATERAL ############################
df_ocupoacion = df[["state", "date",'inpatient_beds_used_covid','deaths_covid']]
df_ocupoacion.rename(columns={'date':'fecha','inpatient_beds_used_covid':'Pacientes (COVID-19) Hospitalizados', 'deaths_covid':'Muertes'},inplace=True)

start_date = st.sidebar.date_input("Fecha Inicial", value=pd.to_datetime(df_ocupoacion.fecha.min(), format="%Y/%m/%d"))
end_date = st.sidebar.date_input("Fecha Final", value=pd.to_datetime(df_ocupoacion.fecha.max(), format="%Y/%m/%d"))

linea = st.sidebar.radio("Linea de tiempo",('Fallecidos', 'Hospitalizados', 'Fallecidos/Hospitalizados'))

eventos = st.sidebar.radio("Fechas con Mayor/Menor No. De Hospitalizaciones",('Mayor', 'Menor'))

genre = st.sidebar.radio("Camas Unidad Cuidados Intensivos",('Total', 'COVID-POSITIVOS'))

paci = st.sidebar.radio("Pacientes",('Adultos', 'Pediatricos'))

start = start_date.strftime("%Y/%m/%d")
end = end_date.strftime("%Y/%m/%d")

Estados = ['Todos'] + list(df['state'].drop_duplicates())
option = st.sidebar.selectbox('Selecciona un Estado:', Estados)

df_global = df[["state", "date",'inpatient_beds_used_covid','deaths_covid']]
df_global.rename(columns={'inpatient_beds_used_covid':'Pacientes (COVID-19) Hospitalizados', 'deaths_covid':'Muertes'},inplace=True)
df_global = df_global.groupby('date').sum('inpatient_beds_used_covid')
df_global['fecha'] = df_global.index
df_global.reset_index(level=0, drop=True,inplace=True)

df_etario = pd.read_csv('Rango_etario.csv')
df_etario['date'] = pd.to_datetime(df_etario['date'])
df_etario.rename(columns={'previous_day_admission_pediatric_covid_confirmed_0_4':'0_4','previous_day_admission_pediatric_covid_confirmed_5_11':'5_11','previous_day_admission_pediatric_covid_confirmed_12_17':'12_17','previous_day_admission_adult_covid_confirmed_18_19':'18_19','previous_day_admission_adult_covid_confirmed_20_29':'20_29','previous_day_admission_adult_covid_confirmed_30_39':'30_39','previous_day_admission_adult_covid_confirmed_40_49':'40_49','previous_day_admission_adult_covid_confirmed_50_59':'50_59','previous_day_admission_adult_covid_confirmed_60_69':'60_69','previous_day_admission_adult_covid_confirmed_70_79':'70_79','previous_day_admission_adult_covid_confirmed_80':'+80'},inplace=True)
df_etario.fillna(0,inplace=True)
df_etario['state'] = df_etario['state'].replace(Estados1.State.values,Estados1.City.values)
df_etario = df_etario.groupby('date').sum()
df_etario['fecha'] = df_etario.index
df_etario.reset_index(level=0, drop=True,inplace=True)

df_relacion = df[['state',"date",'critical_staffing_shortage_today_yes','deaths_covid']]
df_relacion['date'] = pd.to_datetime(df_relacion['date'])
df_relacion.rename(columns={'critical_staffing_shortage_today_yes':'Falta de Personal','deaths_covid':'Muertes'},inplace=True)
df_relacion.fillna(0,inplace=True)
df_relacion['state'] = df_relacion['state'].replace(Estados1.State.values,Estados1.City.values)
df_relacion = df_relacion.groupby('date').sum()
df_relacion['fecha'] = df_relacion.index
df_relacion.reset_index(level=0, drop=True,inplace=True)
df_relacion = df_relacion.loc[(df_relacion['fecha'] >= start) & (df_relacion['fecha'] <= end)].sort_values(by='fecha').melt(id_vars=['fecha'],value_vars=['Falta de Personal','Muertes'])

if option == 'Todos':
    df_etario = df_etario.loc[(df_etario['fecha'] >= start) & (df_etario['fecha'] <= end)].sort_values(by='fecha').melt(id_vars=['fecha'],value_vars=['0_4','5_11','12_17','18_19','20_29','30_39','40_49','50_59','60_69','70_79','+80'])
else:
    df_etario = df_etario.loc[(df_ocupoacion['state'] == option) & (df_etario['fecha'] >= start) & (df_etario['fecha'] <= end)].sort_values(by='fecha').melt(id_vars=['fecha'],value_vars=['0_4','5_11','12_17','18_19','20_29','30_39','40_49','50_59','60_69','70_79','+80'])


########################### LINEA DE TIEMPO  TODOS###############################
if linea == 'Fallecidos/Hospitalizados':
    if option == 'Todos':
        df_flitrado = df_global.loc[(df_global['fecha'] >= start) & (df_global['fecha'] <= end)].sort_values(by='fecha').melt(id_vars=['fecha'],value_vars=['Muertes','Pacientes (COVID-19) Hospitalizados'])
        titulo = f"""<p style="font-family:arial; color:black; text-align: center; font-size: 42px;">Pacientes {linea} (COVID-19) {df_flitrado.value.sum()}</p>"""""
        st.markdown(titulo, unsafe_allow_html=True)
    else:
        df_flitrado = df_ocupoacion.loc[(df_ocupoacion['state'] == option) & (df_ocupoacion['fecha'] >= start) & (df_ocupoacion['fecha'] <= end)].sort_values(by='fecha').melt(id_vars=['fecha'],value_vars=['Muertes','Pacientes (COVID-19) Hospitalizados'])
        titulo = f"""<p style="font-family:arial; color:black; text-align: center; font-size: 42px;">Pacientes {linea} (COVID-19) {df_flitrado.value.sum()}</p>"""""
        st.markdown(titulo, unsafe_allow_html=True)

########################### LINEA DE TIEMPO ###############################

    def get_chart(df):
            hover = alt.selection_single(
                fields=["fecha"],
                nearest=True,
                on="mouseover",
                empty="none",
            )
            lines = (
                alt.Chart(df)
                .mark_line()
                .encode(
                    x='fecha',
                    y='value',
                    color='variable'
                )
            )
            points = lines.transform_filter(hover).mark_circle(size=65)

            tooltips = (
                alt.Chart(df)
                .mark_rule()
                .encode(
                    x="yearmonthdate(fecha)",
                    y="value",
                    opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                    tooltip=[
                        alt.Tooltip("fecha", title="Fecha"),
                        alt.Tooltip("value", title="Camas"),
                    ],
                )
                .add_selection(hover)
            )
            return (lines + points + tooltips).interactive()


    chart = get_chart(df_flitrado)

    st.altair_chart(chart,use_container_width=True)
    titulo = '<p style="font-family:sans-serif; color:black; text-align: left; font-size: 20px;">Fechas Importantes en Hospitalizaciones y contagios por COVID 19</p>'
    st.markdown(titulo, unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    if option == 'Todos':
        df_flitrado = df_global.loc[(df_global['fecha'] >= start) & (df_global['fecha'] <= end)].sort_values(by='fecha')
    else:
        df_flitrado = df_ocupoacion.loc[(df_ocupoacion['state'] == option) & (df_ocupoacion['fecha'] >= start) & (df_ocupoacion['fecha'] <= end)].sort_values(by='fecha')

    df_flitrado['mes'] = df_flitrado.fecha.dt.month
    df_flitrado_max = df_flitrado.groupby([df_flitrado.fecha.dt.year,'mes']).sum('Pacientes (COVID-19) Hospitalizados').sort_values(by='Pacientes (COVID-19) Hospitalizados',ascending=False).head(5)
    df_flitrado_min = df_flitrado.groupby([df_flitrado.fecha.dt.year,'mes']).sum('Pacientes (COVID-19) Hospitalizados').sort_values(by='Pacientes (COVID-19) Hospitalizados',ascending=True).head(5)

    with col3:
        if eventos == 'Mayor':
            st.dataframe(df_flitrado_max)
        else:
            st.dataframe(df_flitrado_min)
    with col4:
        c4 = alt.Chart(df_etario).mark_bar().encode(
            alt.X('variable:N', axis=alt.Axis(title='Rango Etario'),sort=alt.EncodingSortField(field='value', op="sum", order="descending")),
            alt.Y('value:Q',axis=alt.Axis(title='Pacientes Hospitalizados')),
        )
        titulo = '<p style="font-family:sans-serif; color:black; text-align: center; font-size: 20px;">Cantidad de Hospitalizaciones por rango Etario</p>'
        st.markdown(titulo, unsafe_allow_html=True)
        st.altair_chart(c4, use_container_width=True)
        
########################### LINEA DE TIEMPO y BARRAS FALLECIDOS###############################
elif linea == 'Fallecidos':
    y = 'Muertes'
    if option == 'Todos':
        df_flitrado = df_global.loc[(df_global['fecha'] >= start) & (df_global['fecha'] <= end)].sort_values(by='fecha')
        titulo = f"""<p style="font-family:arial; color:black; text-align: center; font-size: 42px;">Pacientes {linea} (COVID-19) {df_flitrado.Muertes.sum()}</p>"""""
        st.markdown(titulo, unsafe_allow_html=True)
    else:
        df_flitrado = df_ocupoacion.loc[(df_ocupoacion['state'] == option) & (df_ocupoacion['fecha'] >= start) & (df_ocupoacion['fecha'] <= end)].sort_values(by='fecha')
        titulo = f"""<p style="font-family:arial; color:black; text-align: center; font-size: 42px;">Pacientes {linea} (COVID-19) {df_flitrado.Muertes.sum()}</p>"""""
        st.markdown(titulo, unsafe_allow_html=True)

    def get_chart(df):
            hover = alt.selection_single(
                fields=["fecha"],
                nearest=True,
                on="mouseover",
                empty="none",
            )
            lines = (
                alt.Chart(df)
                .mark_line()
                .encode(
                    x='fecha',
                    y=y
                )
            )
            points = lines.transform_filter(hover).mark_circle(size=65)

            tooltips = (
                alt.Chart(df)
                .mark_rule()
                .encode(
                    x="yearmonthdate(fecha)",
                    y=y,
                    opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                    tooltip=[
                        alt.Tooltip("fecha", title="Fecha"),
                        alt.Tooltip(y, title="Fallecidos"),
                    ],
                )
                .add_selection(hover)
            )
            return (lines + points + tooltips).interactive()
    
    df_muertos = df[["state", "date",'deaths_covid']]
    df_muertos = df_muertos.loc[(df_muertos['date'] >= start) & (df_muertos['date'] <= end)].sort_values(by='date')
    df_muertos = df_muertos.groupby(by=['state']).sum('deaths_covid').sort_values(by='deaths_covid',ascending=False).head(10)
    df_muertos['State'] = df_muertos.index

    cmuertos = alt.Chart(df_muertos,title='Ranking de Estados con mayor No de Fallecidos por COVID-19').mark_bar().encode(
            alt.X('State:N', axis=alt.Axis(title='Estado'),sort=alt.EncodingSortField(field='deaths_covid', op="sum", order="descending")),
            alt.Y('deaths_covid:Q',axis=alt.Axis(title='Fallecidos por COVID-19'))
        )

    textmuertos = cmuertos.mark_text(
            align='center',
            baseline='bottom'
        ).encode(
            text='deaths_covid:Q'
        )
    col10, col11 = st.columns(2)

    with col10:
        chart = get_chart(df_flitrado)
        st.altair_chart(chart,use_container_width=True)
    with col11:
        st.altair_chart(cmuertos + textmuertos, use_container_width=True)


    col3, col4 = st.columns(2)
    df_flitrado.drop(columns=['Pacientes (COVID-19) Hospitalizados'],inplace=True)
    df_flitrado['mes'] = df_flitrado.fecha.dt.month
    with col3:
         if eventos == 'Mayor':
             titulo = '<p style="font-family:sans-serif; color:black; text-align: center; font-size: 20px;">Fechas con Mayor numero de Fallecidos (COVID-19) (Por Mes)</p>'
             df_flitrado = df_flitrado.groupby([df_flitrado.fecha.dt.year,'mes']).sum('Muertes').sort_values(by='Muertes',ascending=False).head(5)

         else:
             titulo = '<p style="font-family:sans-serif; color:black; text-align: center; font-size: 20px;">Fechas con Menor numero de Fallecidos (COVID-19) (Por Mes)</p>'
             df_flitrado = df_flitrado.groupby([df_flitrado.fecha.dt.year,'mes']).sum('Muertes').sort_values(by='Muertes',ascending=True).head(5)

         st.markdown(titulo, unsafe_allow_html=True)
         st.dataframe(df_flitrado)
    with col4:
        c4 = alt.Chart(df_etario).mark_bar().encode(
            alt.X('variable:N', axis=alt.Axis(title='Rango Etario'),sort=alt.EncodingSortField(field='value', op="sum", order="descending")),
            alt.Y('value:Q',axis=alt.Axis(title='Pacientes Hospitalizados')),
        )
        titulo = '<p style="font-family:sans-serif; color:black; text-align: center; font-size: 20px;">Cantidad de Hospitalizaciones por rango Etario</p>'
        st.markdown(titulo, unsafe_allow_html=True)
        st.altair_chart(c4, use_container_width=True)
    
########################### LINEA DE TIEMPO HOSPITALIZADOS ############################### 
else:
    y = 'Pacientes (COVID-19) Hospitalizados'
    if option == 'Todos':
        df_flitrado = df_global.loc[(df_global['fecha'] >= start) & (df_global['fecha'] <= end)].sort_values(by='fecha')
        titulo = f"""<p style="font-family:arial; color:black; text-align: center; font-size: 42px;">Pacientes {linea} (COVID-19) {df_flitrado['Pacientes (COVID-19) Hospitalizados'].sum()}</p>"""""
        st.markdown(titulo, unsafe_allow_html=True)
    else:
        df_flitrado = df_ocupoacion.loc[(df_ocupoacion['state'] == option) & (df_ocupoacion['fecha'] >= start) & (df_ocupoacion['fecha'] <= end)].sort_values(by='fecha')
        titulo = f"""<p style="font-family:arial; color:black; text-align: center; font-size: 42px;">Pacientes {linea} (COVID-19) {df_flitrado['Pacientes (COVID-19) Hospitalizados'].sum()}</p>"""""
        st.markdown(titulo, unsafe_allow_html=True)

    def get_chart(df):
            hover = alt.selection_single(
                fields=["fecha"],
                nearest=True,
                on="mouseover",
                empty="none",
            )
            lines = (
                alt.Chart(df)
                .mark_line()
                .encode(
                    x='fecha',
                    y=y
                )
            )
            points = lines.transform_filter(hover).mark_circle(size=65)

            tooltips = (
                alt.Chart(df)
                .mark_rule()
                .encode(
                    x="yearmonthdate(fecha)",
                    y=y,
                    opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                    tooltip=[
                        alt.Tooltip("fecha", title="Fecha"),
                        alt.Tooltip(y, title="Hospitalizados"),
                    ],
                )
                .add_selection(hover)
            )
            return (lines + points + tooltips).interactive()


    chart = get_chart(df_flitrado)
    st.altair_chart(chart,use_container_width=True)
    col3, col4 = st.columns(2)
    df_flitrado.drop(columns=['Muertes'],inplace=True)
    df_flitrado['mes'] = df_flitrado.fecha.dt.month
    with col3:
         if eventos == 'Mayor':
             titulo = '<p style="font-family:sans-serif; color:black; text-align: center; font-size: 20px;">Fechas con Mayor numero de Hospitalizaciones (Por Mes)</p>'
             df_flitrado = df_flitrado.groupby([df_flitrado.fecha.dt.year,'mes']).sum('Pacientes (COVID-19) Hospitalizados').sort_values(by='Pacientes (COVID-19) Hospitalizados',ascending=False).head(5)

         else:
             titulo = '<p style="font-family:sans-serif; color:black; text-align: center; font-size: 20px;">Fechas con Menor numero de Hospitalizaciones (Por Mes)</p>'
             df_flitrado = df_flitrado.groupby([df_flitrado.fecha.dt.year,'mes']).sum('Pacientes (COVID-19) Hospitalizados').sort_values(by='Pacientes (COVID-19) Hospitalizados',ascending=True).head(5)

         st.markdown(titulo, unsafe_allow_html=True)
         st.dataframe(df_flitrado)
    with col4:
        c4 = alt.Chart(df_etario).mark_bar().encode(
            alt.X('variable:N', axis=alt.Axis(title='Rango Etario'),sort=alt.EncodingSortField(field='value', op="sum", order="descending")),
            alt.Y('value:Q',axis=alt.Axis(title='Pacientes Hospitalizados')),
        )
        titulo = '<p style="font-family:sans-serif; color:black; text-align: center; font-size: 20px;">Cantidad de Hospitalizaciones por rango Etario</p>'
        st.markdown(titulo, unsafe_allow_html=True)
        st.altair_chart(c4, use_container_width=True)
    
        

########### TOP ESTADOS OCUPACION HOSPITALARIA CAMAS COMUNES #######################

df_top = df[["state", "date",'inpatient_beds_used_covid']]
df_top = df_top.loc[(df_top['date'] >= start) & (df_top['date'] <= end)].sort_values(by='date')
df_top = df_top.groupby(by=['state']).sum('inpatient_beds_used_covid').sort_values(by='inpatient_beds_used_covid',ascending=False).head(10)
df_top['State'] = df_top.index

c1 = alt.Chart(df_top,title='Ranking de Estados con mayor ocupación hospitalaria por COVID').mark_bar().encode(
            alt.X('State:N', axis=alt.Axis(title='Estado'),sort=alt.EncodingSortField(field='inpatient_beds_used_covid', op="sum", order="descending")),
            alt.Y('inpatient_beds_used_covid:Q',axis=alt.Axis(title='Ocupacion Hospitalaria(Camas Ocupadas)'))
        )

text = c1.mark_text(
            align='center',
            baseline='bottom'
        ).encode(
            text='inpatient_beds_used_covid:Q'
        )

########### TOP ESTADOS OCUPACION HOSPITALARIA CAMAS CUIDADOS INTENSIVOS #######################

df_UCI = df[["state", "date",'staffed_adult_icu_bed_occupancy','staffed_pediatric_icu_bed_occupancy','total_staffed_adult_icu_beds','total_staffed_pediatric_icu_beds']]
df_UCI['Camas Ocupadas'] = df_UCI.staffed_adult_icu_bed_occupancy + df_UCI.staffed_pediatric_icu_bed_occupancy
df_UCI = df_UCI.loc[(df_UCI['date'] >= start) & (df_UCI['date'] <= end)].sort_values(by='date')
Total_camas = df_UCI = df_UCI.groupby(by=['state']).sum().sort_values(by='Camas Ocupadas',ascending=False)
df_UCI = df_UCI.groupby(by=['state']).sum().sort_values(by='Camas Ocupadas',ascending=False).head(5)
df_UCI['State'] = df_UCI.index

df_top_UCI = df[["state", "date",'staffed_adult_icu_bed_occupancy','staffed_pediatric_icu_bed_occupancy','staffed_icu_pediatric_patients_confirmed_covid','staffed_icu_adult_patients_confirmed_covid']]
df_top_UCI.fillna(0,inplace=True)
df_top_UCI['total_camas_UCI_COVID'] = df_top_UCI.staffed_icu_pediatric_patients_confirmed_covid + df_top_UCI.staffed_icu_adult_patients_confirmed_covid
df_top_UCI = df_top_UCI.loc[(df_top_UCI['date'] >= start) & (df_top_UCI['date'] <= end)].sort_values(by='date')
Total_camas_covid = df_top_UCI = df_top_UCI.groupby('state').sum('total_camas_UCI_COVID').sort_values(by='total_camas_UCI_COVID',ascending=False)
df_top_UCI = df_top_UCI.groupby('state').sum('total_camas_UCI_COVID').sort_values(by='total_camas_UCI_COVID',ascending=False).head(10)
df_top_UCI['State'] = df_top_UCI.index

if genre == 'Total':
    c2 = alt.Chart(df_UCI,title='Total de camas Unidad de Cuidados Intensivos Utilizadas').mark_bar().encode(
            alt.X('State:N', axis=alt.Axis(title='Estado'),sort=alt.EncodingSortField(field='inpatient_beds_used_covid', op="sum", order="descending")),
            alt.Y('Camas Ocupadas:Q',axis=alt.Axis(title='Ocupacion Hospitalaria(Camas UCI Ocupadas)'))
        )

    text2 = c2.mark_text(
            align='center',
            baseline='bottom'
        ).encode(
            text='Camas Ocupadas:Q'
        )
else:
    c2 = alt.Chart(df_top_UCI,title='Ranking de Estados con mayor ocupación hospitalaria por COVID').mark_bar().encode(
            alt.X('State:N', axis=alt.Axis(title='Estado'),sort=alt.EncodingSortField(field='inpatient_beds_used_covid', op="sum", order="descending")),
            alt.Y('total_camas_UCI_COVID:Q',axis=alt.Axis(title='Ocupacion Hospitalaria(Camas UCI Ocupadas)'))
        )

    text2 = c2.mark_text(
            align='center',
            baseline='bottom'
        ).encode(
            text='total_camas_UCI_COVID:Q'
        )

col3, col4 = st.columns(2)
with col3:
    titulo = '<p style="font-family:sans-serif; color:black; text-align: center; font-size: 20px;">Ranking de Estados con mayor ocupación hospitalaria (Camas Normales) por COVID</p>'
    st.markdown(titulo, unsafe_allow_html=True)
    st.altair_chart(c1 + text, use_container_width=True)

with col4:
    titulo = f"""<p style="font-family:sans-serif; color:black; text-align: center; font-size: 20px;">Ranking de Estados con mayor ocupación hospitalaria (Camas Cuidados Intensivos) {genre}</p>"""
    st.markdown(titulo, unsafe_allow_html=True)
    st.altair_chart(c2 + text2, use_container_width=True)

########### TOP ESTADOS OCUPACION CAMAS OCUPADAS NINOS ADULTOS #######################

df_p_covid = df[["state", "date",'total_pediatric_patients_hospitalized_confirmed_covid']]
df_p_covid = df_p_covid.loc[(df_p_covid['date'] >= start) & (df_p_covid['date'] <= end)].sort_values(by='date')
df_p_covid = df_p_covid.groupby(by=['state']).sum().sort_values(by='total_pediatric_patients_hospitalized_confirmed_covid',ascending=False).head(20)
df_p_covid['State'] = df_p_covid.index

df_a_covid = df[["state", "date",'total_adult_patients_hospitalized_confirmed_covid']]
df_a_covid = df_a_covid.loc[(df_a_covid['date'] >= start) & (df_a_covid['date'] <= end)].sort_values(by='date')
df_a_covid = df_a_covid.groupby(by=['state']).sum().sort_values(by='total_adult_patients_hospitalized_confirmed_covid',ascending=False).head(20)
df_a_covid['State'] = df_a_covid.index
if option == 'Todos':
    if paci == 'Pediatricos':
        c3 = alt.Chart(df_p_covid).mark_bar().encode(
                    alt.X('State:N', axis=alt.Axis(title='Estado'),sort=alt.EncodingSortField(field='inpatient_beds_used_covid', op="sum", order="descending")),
                    alt.Y('total_pediatric_patients_hospitalized_confirmed_covid:Q',axis=alt.Axis(title='Ocupacion Hospitalaria(Camas UCI Ocupadas)'))
                )

        text3 = c3.mark_text(
                    align='center',
                    baseline='bottom'
                ).encode(
                    text='total_pediatric_patients_hospitalized_confirmed_covid:Q'
                )
    else:
        c3 = alt.Chart(df_a_covid).mark_bar().encode(
                    alt.X('State:N', axis=alt.Axis(title='Estado'),sort=alt.EncodingSortField(field='inpatient_beds_used_covid', op="sum", order="descending")),
                    alt.Y('total_adult_patients_hospitalized_confirmed_covid:Q',axis=alt.Axis(title='Ocupacion Hospitalaria(Camas UCI Ocupadas)'))
                )
        text3 = c3.mark_text(
                    align='center',
                    baseline='bottom'
                ).encode(
                    text='total_adult_patients_hospitalized_confirmed_covid:Q'
                )
    titulo = f"""<p style="font-family:sans-serif; color:black; text-align: center; font-size: 25px;">Camas utilizadas por Pacientes {paci} Afirmativos COVID-19</p>"""
    st.markdown(titulo, unsafe_allow_html=True)
    st.altair_chart(c3 + text3, use_container_width=True)


########### LINEA DE TIEMPO ESTADO CAMAS OCUPADAS #######################

else:
    if paci == 'Pediatricos':
        y = 'total_pediatric_patients_hospitalized_confirmed_covid'
    else:
        y = 'total_adult_patients_hospitalized_confirmed_covid'

    df_p_covid = df[["state", "date", y]]
    df_flitrado = df_p_covid.loc[(df_p_covid['state'] == option) & (df_p_covid['date'] >= start) & (df_p_covid['date'] <= end)].sort_values(by='date')

    def get_chart(df):
            hover = alt.selection_single(
                fields=["date"],
                nearest=True,
                on="mouseover",
                empty="none",
            )
            lines = (
                alt.Chart(df)
                .mark_line()
                .encode(
                    x='date',
                    y=y,
                )
            )
            points = lines.transform_filter(hover).mark_circle(size=65)

            tooltips = (
                alt.Chart(df)
                .mark_rule()
                .encode(
                    x="yearmonthdate(date)",
                    y=y,
                    opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                    tooltip=[
                        alt.Tooltip("date", title="Fecha"),
                        alt.Tooltip(y, title="Camas"),
                    ],
                )
                .add_selection(hover)
            )
            return (lines + points + tooltips).interactive()


    chart = get_chart(df_flitrado)
    titulo = f"""<p style="font-family:sans-serif; color:black; text-align: center; font-size: 25px;">Camas Comun utilizadas por Pacientes {paci} Afirmativos COVID-19: {df_flitrado[y].sum()}</p>"""
    st.markdown(titulo, unsafe_allow_html=True)
    st.altair_chart(chart,use_container_width=True)

################################ PIE CHART PORCENTAJE CAMAS COVID #################################

Total_camas = Total_camas.sort_values(by='state')
Total_camas.drop(Total_camas.columns.difference(['Camas Ocupadas']), 1, inplace=True)
Total_camas['state'] = Total_camas.index
dfprueba = {'Camas Ocupadas':Total_camas['Camas Ocupadas'].sum(), 'state':'Todos'}
Total_camas = Total_camas.append(dfprueba, ignore_index = True)

Total_camas_covid = Total_camas_covid.sort_values(by='state')
Total_camas_covid.drop(Total_camas_covid.columns.difference(['total_camas_UCI_COVID']), 1, inplace=True)
Total_camas_covid['state'] = Total_camas_covid.index
dfprueba = {'total_camas_UCI_COVID':Total_camas_covid['total_camas_UCI_COVID'].sum(), 'state':'Todos'}
Total_camas_covid = Total_camas_covid.append(dfprueba, ignore_index = True)

Total_camas['Porcentaje'] = (Total_camas_covid.total_camas_UCI_COVID / Total_camas['Camas Ocupadas'])

def pie_chart(Estados):
    df = Total_camas.loc[Total_camas.state == Estados]
    labels = ['Pacientes Confirmados COVID-19','Otras Aflicciones/Enfermedades']
    data = [(df.Porcentaje.values[0] * 100), (100 - (df.Porcentaje.values[0] * 100))]
    explode = (0.1, 0.0)
    colors = ( "#EC6B56", "#9BBFE0")
    wp = { 'linewidth' : 2, 'edgecolor' : "black" }

    fig, ax = plt.subplots(figsize =(6, 3),facecolor='white')
    wedges, texts, autotexts = ax.pie(data,
                                  autopct ='%1.1f%%',
                                  explode=explode,
                                  labels = labels,
                                  shadow = True,
                                  colors = colors,
                                  startangle = 90,
                                  wedgeprops = wp,
                                  textprops = dict(color ="black"))
    ax.legend(wedges, labels,
          title ="Camas UCI",
          loc ="center left",
          bbox_to_anchor =(1, 0, 0.5, 1))
    plt.setp(autotexts, size = 12, weight ="bold")
    ax.set_title("% de Camas en Unidad de Cuidados Intensivos Utilizadas " + '(' + Estados + ')')
    return fig

################################ RELACION MUERTOS,PERSONAL #################################'

def get_chart(df):
            hover = alt.selection_single(
                fields=["fecha"],
                nearest=True,
                on="mouseover",
                empty="none",
            )
            lines = (
                alt.Chart(df)
                .mark_line()
                .encode(
                    x='fecha',
                    y='value',
                    color='variable'
                )
            )
            points = lines.transform_filter(hover).mark_circle(size=65)

            tooltips = (
                alt.Chart(df)
                .mark_rule()
                .encode(
                    x="yearmonthdate(fecha)",
                    y="value",
                    opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                    tooltip=[
                        alt.Tooltip("fecha", title="Fecha"),
                        alt.Tooltip("value", title="Paciente"),
                    ],
                )
                .add_selection(hover)
            )
            return (lines + points + tooltips).interactive()

col5, col6 = st.columns(2)
with col5:
    st.pyplot(pie_chart(option))

with col6:
    chart = get_chart(df_relacion)
    titulo = f"""<p style="font-family:arial; color:black; text-align: center; font-size: 20px;">Relacion Fallecidos / Falta de personal</p>"""""
    st.markdown(titulo, unsafe_allow_html=True)
    st.altair_chart(chart,use_container_width=True)
