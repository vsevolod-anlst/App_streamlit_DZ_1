import pandas as pd
import requests
from datetime import datetime
import streamlit as st
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


month_to_season = {12: "winter", 1: "winter", 2: "winter",
                   3: "spring", 4: "spring", 5: "spring",
                   6: "summer", 7: "summer", 8: "summer",
                   9: "autumn", 10: "autumn", 11: "autumn"}

# Функция для проверки введенного API-ключа
def check_api_key():
    if st.session_state.api_key == "":
        st.error("API-ключ не введен")
        return False

    default_city = "Москва"
    result = get_temp(default_city, st.session_state.api_key)
    if isinstance(result, str) and ("ошибка" in result.lower() or "invalid api key" in result.lower()):
        st.error(f"Ошибка: {result}")
        return False
    return True

def check_csv(file):
    required_columns = {'city', 'timestamp', 'temperature', 'season'}
    try:
        df = pd.read_csv(file)
        if not required_columns.issubset(df.columns):
            missing_columns = required_columns - set(df.columns)
            st.error(f"В CSV файле отсутствуют следующие столбцы: {', '.join(missing_columns)}")
            return False
        st.session_state.data = df
        return True
    except Exception as e:
        st.error(f"Ошибка чтения CSV файла: {e}")
        return False

def get_temp(city_name, API_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "main" in data and "temp" in data["main"]:
            temp = data['main']['temp']
            return temp
        else:
            return f"Ошибка: {data.get('message', 'Неизвестная ошибка')}"
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            return "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."
        return f"HTTP ошибка: {http_err}"
    except requests.exceptions.ConnectionError as conn_err:
        return f"Ошибка соединения: {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        return f"Ошибка таймаута: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Ошибка запроса: {req_err}"

def get_city_data(city,df):
    city_data = df[df['city'] == city].copy()
    return city_data

def detect_anomalies(df, city_name, threshold=2):
    # Фильтруем данные по городу
    city_data = df[df['city'] == city_name].copy()
    #city_data = df

    city_data['timestamp'] = pd.to_datetime(city_data['timestamp'])

    # Вычисляем скользящую среднюю с окном в 30 дней
    city_data['moving_avg'] = city_data['temperature'].rolling(window=30, min_periods=1).mean() # min_periods значит что для вычисления значения нужно хотя бы одно измерение
    # Вычисляем стандартное отклонение с окном в 30 дней
    city_data['moving_std'] = city_data['temperature'].rolling(window=30, min_periods=1).std()

    # Вычисляем сезонные средние значения и стандартное отклонение по реальной температуре
    season_means = city_data.groupby(['season'])['temperature'].mean().reset_index()
    season_means.rename(columns={'temperature': 'seasonal_mean'}, inplace=True)
    season_stds = city_data.groupby(['season'])['temperature'].std().reset_index()
    season_stds.rename(columns={'temperature': 'seasonal_std'}, inplace=True)


    # Объединяем данные по температуре с сезонными средними значениями и стандартными отклонениями
    city_data = city_data.merge(season_means, on='season')
    city_data = city_data.merge(season_stds, on='season')


    # Обнаружение аномалий на основе скользящей средней
    city_data['is_anomaly_moving_avg'] = city_data.apply(
        lambda row: abs(row['temperature'] - row['moving_avg']) > threshold * row['moving_std'],
        axis=1
    )

    # Обнаружение аномалий на основе сезонной средней и сезонного стандартного отклонения
    city_data['is_anomaly_season'] = city_data.apply(
        lambda row: abs(row['temperature'] - row['seasonal_mean']) > threshold * row['seasonal_std'],
        axis=1
    )

    # Средние значения и стандартное отклонение по каждому сезону
    seasonal_stats = city_data.groupby('season')['temperature'].agg(['mean', 'std']).reset_index()
    seasonal_stats.rename(columns={'mean': 'seasonal_mean', 'std': 'seasonal_std'}, inplace=True)

    # Минимальная, максимальная и средняя температура за все время наблюдений
    min_temp = city_data['temperature'].min()
    max_temp = city_data['temperature'].max()
    mean_temp = city_data['temperature'].mean()

    return seasonal_stats, min_temp, max_temp, mean_temp, city_data

def is_anomalous_temp(season, temp, seasonal_stats):
    row = seasonal_stats[seasonal_stats['season'] == season]
    if not row.empty:
        seasonal_mean = row['seasonal_mean'].values[0]
        seasonal_std = row['seasonal_std'].values[0]
        abs_raznica = abs(temp - seasonal_mean)
        return (abs_raznica > 2 * seasonal_std), (abs_raznica / (seasonal_std))
    else:
        print(f"Данные для сезона {season} не найдены")
        return


def get_season():
    current_datetime = datetime.now()
    current_month_number = current_datetime.month
    current_season = month_to_season.get(current_month_number)
    return current_season

def get_seasonal_stats_min_temp_max_temp_mean_temp(city, API_key,df):
    temp = get_temp(city, API_key)
    # отделим данные по городу
    city_data_new = get_city_data(city,df)
    # узнаем профиль ВСЕХ СЕЗОНОВ В ГОРОДЕ СРАЗУ, min, max, mean
    seasonal_stats, min_temp, max_temp, mean_temp, city_data = detect_anomalies(city_data_new, city)

    current_season = get_season() # узнаем сезон
    seasonal_stats_current_season = seasonal_stats[seasonal_stats['season'] == current_season]
    is_anomaly_for_season, cnt_sigm_temp = is_anomalous_temp(current_season, temp, seasonal_stats)
    return is_anomaly_for_season, cnt_sigm_temp, temp, seasonal_stats_current_season, min_temp, max_temp, mean_temp, city_data




def add_trend_line(city_data, city_name):
    # Подготовка данных для линейной регрессии
    city_data['timestamp_ordinal'] = pd.to_datetime(city_data['timestamp']).apply(lambda x: x.toordinal())
    X = city_data['timestamp_ordinal'].values.reshape(-1, 1)
    y = city_data['temperature'].values

    # Построение линейной регрессии
    model = LinearRegression()
    model.fit(X, y)
    trend = model.predict(X)

    # Получение коэффициента наклона
    slope = model.coef_[0]

    # Определение направления тренда
    if slope > 0:
        trend_direction = "Восходящий"
    else:
        trend_direction = "Нисходящий"

    # Построение графика
    plt.figure(figsize=(12, 6))
    plt.plot(city_data['timestamp'], city_data['temperature'], label='Temperature', color='green', alpha=1, linewidth=0.3)
    plt.plot(city_data['timestamp'], trend, label=f'Trend Line ({trend_direction})', color='red')
    plt.title(f'Real Temperature and Trend Line in {city_name}')
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature')
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)

    # Отображение дополнительной информации
    st.write(f"Коэффициент наклона трендовой линии: {slope:.8f}")
    st.write(f"Направление тренда: {trend_direction}")
