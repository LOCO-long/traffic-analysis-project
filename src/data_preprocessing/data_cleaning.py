# src/data_preprocessing/data_cleaning.py
import pandas as pd
import os
import json
from datetime import datetime
import configparser

# 加载配置
config = configparser.ConfigParser()
config.read('../config/config.ini')


class DataCleaner:
    def __init__(self):
        self.raw_data_dir = config['settings']['raw_data_dir']
        self.processed_data_dir = config['settings']['processed_data_dir']
        os.makedirs(self.processed_data_dir, exist_ok=True)

    # 百度地图数据处理方法保持不变...

    def clean_gaode_route_data(self, file_path):
        """清洗高德地图路线数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'route' not in data or 'paths' not in data['route']:
            return None

        path = data['route']['paths'][0]  # 取第一条推荐路线
        cleaned_data = {
            'distance': int(path['distance']),  # 距离(米)
            'duration': int(path['duration']),  # 耗时(秒)
            'traffic_lights': int(path.get('traffic_lights', 0)),  # 红绿灯数量
            'steps': [
                {
                    'instruction': step.get('instruction', ''),
                    'distance': int(step.get('distance', 0)),
                    'duration': int(step.get('duration', 0)),
                    'road': step.get('road', ''),
                    'orientation': step.get('orientation', '')
                }
                for step in path['steps']
            ]
        }

        # 从文件名提取时间戳
        filename = os.path.basename(file_path)
        try:
            timestamp_str = filename.split('_')[-1].replace('.json', '')
            if timestamp_str != 'now':
                cleaned_data['timestamp'] = datetime.strptime(timestamp_str, "%Y%m%d%H%M")
            else:
                cleaned_data['timestamp'] = datetime.now()
        except:
            cleaned_data['timestamp'] = datetime.now()

        # 提取起点和终点
        origin = data['route']['origin'].split(',')
        destination = data['route']['destination'].split(',')
        cleaned_data['origin'] = f"{float(origin[1]):.6f},{float(origin[0]):.6f}"  # 转换为百度地图格式
        cleaned_data['destination'] = f"{float(destination[1]):.6f},{float(destination[0]):.6f}"

        return cleaned_data

    def process_all_gaode_route_data(self):
        """处理所有高德地图路线数据"""
        gaode_data_dir = os.path.join(self.raw_data_dir, 'gaode')
        processed_routes = []

        for filename in os.listdir(gaode_data_dir):
            if filename.startswith('driving_route') and filename.endswith('.json'):
                file_path = os.path.join(gaode_data_dir, filename)
                cleaned_data = self.clean_gaode_route_data(file_path)
                if cleaned_data:
                    processed_routes.append(cleaned_data)

        # 转换为DataFrame并保存
        if processed_routes:
            df = pd.DataFrame(processed_routes)
            output_path = os.path.join(self.processed_data_dir, 'gaode_routes.csv')
            df.to_csv(output_path, index=False)
            print(f"已处理 {len(processed_routes)} 条高德地图路线数据并保存到 {output_path}")
            return df

        return None

    def clean_weather_data(self, file_path):
        """清洗天气数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'main' not in data or 'weather' not in data:
            return None

        cleaned_data = {
            'timestamp': datetime.fromtimestamp(data['dt']),
            'location': data.get('name', '未知位置'),
            'temperature': data['main']['temp'],  # 温度(°C)
            'feels_like': data['main']['feels_like'],  # 体感温度(°C)
            'pressure': data['main']['pressure'],  # 气压(hPa)
            'humidity': data['main']['humidity'],  # 湿度(%)
            'wind_speed': data['wind']['speed'],  # 风速(m/s)
            'weather_main': data['weather'][0]['main'],  # 天气主类
            'weather_description': data['weather'][0]['description'],  # 天气描述
            'clouds': data['clouds']['all']  # 云量(%)
        }

        # 提取地理位置
        if 'coord' in data:
            cleaned_data['latitude'] = data['coord']['lat']
            cleaned_data['longitude'] = data['coord']['lon']

        return cleaned_data

    def process_all_weather_data(self):
        """处理所有天气数据"""
        weather_data_dir = os.path.join(self.raw_data_dir, 'weather')
        processed_weather = []

        for filename in os.listdir(weather_data_dir):
            if filename.startswith('weather') and filename.endswith('.json'):
                file_path = os.path.join(weather_data_dir, filename)
                cleaned_data = self.clean_weather_data(file_path)
                if cleaned_data:
                    processed_weather.append(cleaned_data)

        # 转换为DataFrame并保存
        if processed_weather:
            df = pd.DataFrame(processed_weather)
            output_path = os.path.join(self.processed_data_dir, 'weather_data.csv')
            df.to_csv(output_path, index=False)
            print(f"已处理 {len(processed_weather)} 条天气数据并保存到 {output_path}")
            return df

        return None