import matplotlib.pyplot as plt
import streamlit as st

def plot_temp_and_moving_avg(city_data, city_name):
    if 'moving_avg' in city_data.columns and 'moving_std' in city_data.columns:
        plt.figure(figsize=(12, 6))
        plt.plot(city_data['timestamp'], city_data['temperature'], label='Temperature', color='green', alpha=1, linewidth=0.3)
        plt.plot(city_data['timestamp'], city_data['moving_avg'], label='Moving Average', color='red', alpha=1, linewidth=0.5)
        plt.fill_between(city_data['timestamp'],
                         city_data['moving_avg'] - 2 * city_data['moving_std'],
                         city_data['moving_avg'] + 2 * city_data['moving_std'],
                         color='gray', alpha=0.5, label='2 Moving Std Dev')
        anomalies_moving_avg = city_data[city_data['is_anomaly_moving_avg']]
        plt.scatter(anomalies_moving_avg['timestamp'], anomalies_moving_avg['temperature'],
                    color='black', label='Anomalies (Moving Avg)', marker='o')
        plt.title(f'Temperature and Moving Average Anomalies in {city_name}')
        plt.xlabel('Timestamp')
        plt.ylabel('Temperature')
        plt.legend()
        plt.tight_layout()
        st.pyplot(plt)
    else:
        st.write("Необходимые столбцы ('moving_avg', 'moving_std') отсутствуют в данных.")

def plot_temp_and_seasonal_anomalies(city_data, city_name):
    if 'seasonal_mean' in city_data.columns and 'seasonal_std' in city_data.columns:
        plt.figure(figsize=(12, 6))
        plt.plot(city_data['timestamp'], city_data['temperature'], label='Temperature', color='green', alpha=1, linewidth=0.3)
        plt.plot(city_data['timestamp'], city_data['seasonal_mean'], label='Seasonal Mean', color='blue', alpha=1, linewidth=0.5)
        plt.fill_between(city_data['timestamp'],
                         city_data['seasonal_mean'] - 2 * city_data['seasonal_std'],
                         city_data['seasonal_mean'] + 2 * city_data['seasonal_std'],
                         color='gray', alpha=0.5, label='2 Seasonal Std Dev')
        anomalies_season = city_data[city_data['is_anomaly_season']]
        plt.scatter(anomalies_season['timestamp'], anomalies_season['temperature'],
                    color='orange', label='Anomalies (Season)', marker='x')
        plt.title(f'Temperature and Seasonal Anomalies in {city_name}')
        plt.xlabel('Timestamp')
        plt.ylabel('Temperature')
        plt.legend()
        plt.tight_layout()
        st.pyplot(plt)
    else:
        st.write("Необходимые столбцы ('seasonal_mean', 'seasonal_std') отсутствуют в данных.")

def plot_temp_and_all_anomalies(city_data, city_name):
    if 'is_anomaly_moving_avg' in city_data.columns and 'is_anomaly_season' in city_data.columns:
        plt.figure(figsize=(12, 6))
        plt.plot(city_data['timestamp'], city_data['temperature'], label='Temperature', color='green', alpha=1, linewidth=0.3)
        anomalies_moving_avg = city_data[city_data['is_anomaly_moving_avg']]
        anomalies_season = city_data[city_data['is_anomaly_season']]
        plt.scatter(anomalies_moving_avg['timestamp'], anomalies_moving_avg['temperature'],
                    color='black', label='Anomalies (Moving Avg)', marker='o')
        plt.scatter(anomalies_season['timestamp'], anomalies_season['temperature'],
                    color='orange', label='Anomalies (Season)', marker='x')
        plt.title(f'Temperature Anomalies in {city_name}')
        plt.xlabel('Timestamp')
        plt.ylabel('Temperature')
        plt.legend()
        plt.tight_layout()
        st.pyplot(plt)
    else:
        st.write("Необходимые столбцы ('is_anomaly_moving_avg', 'is_anomaly_season') отсутствуют в данных.")


