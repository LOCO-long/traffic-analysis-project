# src/data_preprocessing/combined_data_processing.py
import pandas as pd
import os
import json
from datetime import datetime
import configparser
import numpy as np

# 加载配置
config = configparser.ConfigParser()
config.read('../config/config.ini')


class CombinedDataProcessor:
    def __init__(self):
        self.processed_data_dir = config['settings']['processed_data_dir']
        self.results_dir = config['settings']['results_dir']
        os.makedirs(self.processed_data_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)

    def merge_route_data(self):
        """合并百度和高德地图的路线数据"""
        baidu_data_path = os.path.join(self.processed_data_dir, 'baidu_routes.csv')
        gaode_data_path = os.path.join(self.processed_data_dir, 'gaode_routes.csv')

        if not os.path.exists(baidu_data_path) or not os.path.exists(gaode_data_path):
            print("百度或高德地图数据不存在，无法合并")
            return None

        # 读取数据
        baidu_df = pd.read_csv(baidu_data_path)
        gaode_df = pd.read_csv(gaode_data_path)

        # 确保数据包含必要的列
        required_columns = ['origin', 'destination', 'timestamp', 'distance', 'duration']
        for col in required_columns:
            if col not in baidu_df.columns or col not in gaode_df.columns:
                print(f"数据缺少必要的列: {col}")
                return None

        # 转换时间戳为datetime类型
        baidu_df['timestamp'] = pd.to_datetime(baidu_df['timestamp'])
        gaode_df['timestamp'] = pd.to_datetime(gaode_df['timestamp'])

        # 提取小时和星期几作为特征
        baidu_df['hour'] = baidu_df['timestamp'].dt.hour
        baidu_df['day_of_week'] = baidu_df['timestamp'].dt.dayofweek  # 0=周一，6=周日
        gaode_df['hour'] = gaode_df['timestamp'].dt.hour
        gaode_df['day_of_week'] = gaode_df['timestamp'].dt.dayofweek

        # 重命名列以便区分
        baidu_df = baidu_df.rename(columns={
            'distance': 'distance_baidu',
            'duration': 'duration_baidu'
        })

        gaode_df = gaode_df.rename(columns={
            'distance': 'distance_gaode',
            'duration': 'duration_gaode'
        })

        # 合并数据
        merged_df = pd.merge(
            baidu_df[['origin', 'destination', 'timestamp', 'hour', 'day_of_week', 'distance_baidu', 'duration_baidu']],
            gaode_df[['origin', 'destination', 'timestamp', 'distance_gaode', 'duration_gaode']],
            on=['origin', 'destination', 'timestamp']
        )

        # 计算差异
        merged_df['distance_diff'] = merged_df['distance_baidu'] - merged_df['distance_gaode']
        merged_df['duration_diff'] = merged_df['duration_baidu'] - merged_df['duration_gaode']
        merged_df['duration_diff_percent'] = (merged_df['duration_diff'] / merged_df['duration_gaode']) * 100

        # 保存合并后的数据
        output_path = os.path.join(self.processed_data_dir, 'merged_routes.csv')
        merged_df.to_csv(output_path, index=False)
        print(f"已合并路线数据并保存到 {output_path}")

        return merged_df

    def merge_with_weather_data(self):
        """将路线数据与天气数据合并"""
        routes_data_path = os.path.join(self.processed_data_dir, 'merged_routes.csv')
        weather_data_path = os.path.join(self.processed_data_dir, 'weather_data.csv')

        if not os.path.exists(routes_data_path) or not os.path.exists(weather_data_path):
            print("路线或天气数据不存在，无法合并")
            return None

        # 读取数据
        routes_df = pd.read_csv(routes_data_path)
        weather_df = pd.read_csv(weather_data_path)

        # 转换时间戳为datetime类型
        routes_df['timestamp'] = pd.to_datetime(routes_df['timestamp'])
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])

        # 为简化起见，我们按日期和小时进行匹配
        routes_df['date_hour'] = routes_df['timestamp'].dt.strftime('%Y-%m-%d %H')
        weather_df['date_hour'] = weather_df['timestamp'].dt.strftime('%Y-%m-%d %H')

        # 合并数据
        merged_df = pd.merge(
            routes_df,
            weather_df[['date_hour', 'temperature', 'humidity', 'wind_speed', 'weather_main', 'clouds']],
            on='date_hour',
            how='left'
        )

        # 保存合并后的数据
        output_path = os.path.join(self.processed_data_dir, 'routes_with_weather.csv')
        merged_df.to_csv(output_path, index=False)
        print(f"已合并路线和天气数据并保存到 {output_path}")

        return merged_df