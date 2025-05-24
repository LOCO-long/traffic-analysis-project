# src/data_collection/weather_api.py
import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import configparser

# 加载配置
config = configparser.ConfigParser()
config.read('../config/config.ini')


class WeatherAPI:
    def __init__(self):
        self.api_key = config['weather_api']['api_key']
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.output_dir = os.path.join(config['settings']['raw_data_dir'], 'weather')
        os.makedirs(self.output_dir, exist_ok=True)
        self.units = "metric"  # 公制单位

    def get_current_weather(self, location, timestamp=None):
        """获取指定位置的当前天气数据"""
        # 将中文地址转换为经纬度
        lat, lon = self._geocode(location)

        if not lat or not lon:
            print(f"无法获取 {location} 的经纬度")
            return None

        endpoint = "/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": self.units
        }

        try:
            response = requests.get(self.base_url + endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # 保存数据
            timestamp_str = timestamp or datetime.now().strftime("%Y%m%d%H%M")
            filename = f"weather_{location}_{timestamp_str}.json"
            with open(os.path.join(self.output_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 控制API请求频率
            time.sleep(1)

            return data
        except requests.exceptions.RequestException as e:
            print(f"天气API请求错误: {e}")
            return None

    def get_forecast(self, location, days=5):
        """获取指定位置的天气预报数据"""
        # 将中文地址转换为经纬度
        lat, lon = self._geocode(location)

        if not lat or not lon:
            print(f"无法获取 {location} 的经纬度")
            return None

        endpoint = "/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": self.units
        }

        try:
            response = requests.get(self.base_url + endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # 保存数据
            filename = f"forecast_{location}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(os.path.join(self.output_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return data
        except requests.exceptions.RequestException as e:
            print(f"天气预报API请求错误: {e}")
            return None

    def _geocode(self, address):
        """将地址转换为经纬度"""
        # 这里简化处理，实际应用中可以使用地图API进行地址解析
        # 或者使用专门的地理编码API
        if "北京" in address:
            return 39.9042, 116.4074
        elif "上海" in address:
            return 31.2304, 121.4737
        elif "广州" in address:
            return 23.1291, 113.2644
        else:
            # 默认返回北京坐标
            return 39.9042, 116.4074


# 示例使用
if __name__ == "__main__":
    api = WeatherAPI()
    location = "北京市"
    weather_data = api.get_current_weather(location)

    if weather_data:
        print(f"成功获取 {location} 的天气数据")
        print(f"当前温度: {weather_data['main']['temp']}°C")
        print(f"天气状况: {weather_data['weather'][0]['description']}")