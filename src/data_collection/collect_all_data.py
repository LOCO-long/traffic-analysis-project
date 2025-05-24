# src/data_collection/collect_all_data.py
import os
import sys
import time
from datetime import datetime, timedelta
import pandas as pd

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collection.baidu_map_api import BaiduMapAPI
from data_collection.gaode_map_api import GaodeMapAPI
from data_collection.weather_api import WeatherAPI


def collect_route_data():
    """收集路线数据"""
    # 初始化API客户端
    baidu_api = BaiduMapAPI()
    gaode_api = GaodeMapAPI()

    # 定义要分析的路线
    routes = [
        {"origin": "北京市海淀区中关村", "destination": "北京市朝阳区国贸"},
        {"origin": "北京市西城区天安门", "destination": "北京市海淀区颐和园"},
        {"origin": "北京市朝阳区三里屯", "destination": "北京市东城区王府井"},
        {"origin": "北京市丰台区北京南站", "destination": "北京市朝阳区北京首都国际机场"}
    ]

    # 收集不同时间段的数据
    time_intervals = [7, 10, 13, 16, 19, 22]  # 一天中的不同时间段

    for route in routes:
        for hour in time_intervals:
            # 构建时间戳（今天的特定小时）
            timestamp = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)

            # 转换为Unix时间戳
            unix_timestamp = int(timestamp.timestamp())

            print(f"收集 {route['origin']} 到 {route['destination']} 在 {timestamp.strftime('%Y-%m-%d %H:%M')} 的数据")

            # 收集百度地图数据
            baidu_api.get_driving_route(route["origin"], route["destination"], unix_timestamp)

            # 收集高德地图数据
            gaode_api.get_driving_route(route["origin"], route["destination"], unix_timestamp)

            # 避免API请求过于频繁
            time.sleep(2)


def collect_weather_data():
    """收集天气数据"""
    weather_api = WeatherAPI()

    # 定义要收集天气数据的城市
    cities = ["北京市", "上海市", "广州市", "深圳市", "杭州市"]

    for city in cities:
        print(f"收集 {city} 的当前天气数据")
        weather_api.get_current_weather(city)

        # 收集未来天气预报
        print(f"收集 {city} 的天气预报数据")
        weather_api.get_forecast(city)

        # 避免API请求过于频繁
        time.sleep(2)


if __name__ == "__main__":
    print("开始数据收集...")

    # 收集路线数据
    collect_route_data()

    # 收集天气数据
    collect_weather_data()

    print("数据收集完成!")