#streamlit run app.py - запуск в терминале


import streamlit as st
import pandas as pd
import tempfile

from functions import check_api_key, check_csv, get_seasonal_stats_min_temp_max_temp_mean_temp, add_trend_line
from print_grafics import plot_temp_and_moving_avg, plot_temp_and_seasonal_anomalies, plot_temp_and_all_anomalies

# Инициализация состояния сессии
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

if 'selected_cities' not in st.session_state:
    st.session_state.selected_cities = []

if 'api_key_entered' not in st.session_state:
    st.session_state.api_key_entered = False

if 'csv_uploaded' not in st.session_state:
    st.session_state.csv_uploaded = False


st.title("Анализ Аномальности текущей погоды")
st.header("Шаг 1: Ввод API-ключа для сайта OpenWeatherMap")
api_key_input = st.text_input("API-ключ", placeholder='Скопируйте сюда ваш ключ, мистер Поттер', value=st.session_state.api_key)

# проверим не нажал ли он кнопку просто так
if st.button("Готово"):
    st.session_state.api_key = api_key_input
    if check_api_key():
        st.session_state.api_key_entered = True
    else:
        st.session_state.api_key_entered = False

if st.session_state.api_key_entered:
    st.header("Шаг 2: Загрузка CSV файла с историческими данными")
    uploaded_file = st.file_uploader("Загрузите CSV файл", type="csv")

    if uploaded_file is not None:
        if check_csv(uploaded_file):
            st.session_state.csv_uploaded = True
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name

            # Прочитайте CSV файл в DataFrame
            df = pd.read_csv(temp_file_path, encoding='utf-8')
            st.session_state.data = df
            st.session_state.cities_list = df['city'].unique()
            st.write(df.head())
        else:
            st.session_state.csv_uploaded = False

if st.session_state.csv_uploaded:
    st.header("Шаг 3: Выбор города")
    multiselect_streamlit = st.multiselect("Выберите город", options=st.session_state.cities_list, max_selections=1, placeholder='Выберите город')

    if multiselect_streamlit:
        city = multiselect_streamlit[0]
        st.write(f"Вы выбрали: {city}")

        is_Anomal_temp, cnt_over_time, temp, seasonal_stats_current_season, min_temp, max_temp, mean_temp, city_data = get_seasonal_stats_min_temp_max_temp_mean_temp(city, st.session_state.api_key, df)
        st.write(city_data.head())
        # Посчитаем внутри 2 сигм оно или нет
        if is_Anomal_temp is not None and is_Anomal_temp:
            st.write(f"Температура составляет: {temp:.2f} °C")
            st.markdown(f"""Это <span style="color:red">аномалия</span> для города {city} для этого сезона""", unsafe_allow_html=True)
            st.write(f"Температура отличается от среднесезонной на {cnt_over_time} стандартных отклонения")
        elif is_Anomal_temp is not None:
            st.write(f"Температура составляет: {temp:.2f} °C")
            st.markdown(f"""Это <span style="color:green">нормально</span> для города {city} для этого сезона""", unsafe_allow_html=True)
            st.write(f"Температура отличается от среднесезонной на {cnt_over_time} стандартных отклонения")
        if 'season' in seasonal_stats_current_season.columns and 'seasonal_mean' in seasonal_stats_current_season.columns and 'seasonal_std' in seasonal_stats_current_season.columns:
            season = seasonal_stats_current_season.loc[3, 'season']
            seasonal_mean = seasonal_stats_current_season.loc[3, 'seasonal_mean']
            seasonal_std = seasonal_stats_current_season.loc[3, 'seasonal_std']
            st.write(
                f'Для сезона {season} среднесезонная температура: {seasonal_mean:.2f} °C, а стандартное отклонение: {seasonal_std:.2f} °C')
        else:
            print("Проблема с именами столбцов")

        st.header("Шаг 4: Выбор графиков для построения")
        selected_plots = st.multiselect(
        "Выберите графики для построения",
        options=["Температура и Скользящее Среднее", "Температура и Сезонные Аномалии", "Температура и Все Аномалии", "Температура и Линия Тренда"],
        default=["Температура и Скользящее Среднее"]
        )

        if "Температура и Скользящее Среднее" in selected_plots:
            plot_temp_and_moving_avg(city_data, city)

        if "Температура и Сезонные Аномалии" in selected_plots:
            plot_temp_and_seasonal_anomalies(city_data, city)

        if "Температура и Все Аномалии" in selected_plots:
            plot_temp_and_all_anomalies(city_data, city)

        if "Температура и Линия Тренда" in selected_plots:
            add_trend_line(city_data,city)