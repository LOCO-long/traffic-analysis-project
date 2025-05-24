# src/data_collection/gaode_map_api.py
import requests
import json
import os
import time
from dotenv import load_dotenv
import configparser

# 加载配置
config = configparser.ConfigParser()
config.read('../config/config.ini')


class GaodeMapAPI:
    def __init__(self):
        self.api_key = config['gaode_map']['api_key']
        self.base_url = "https://restapi.amap.com/v3"
        self.output_dir = os.path.join(config['settings']['raw_data_dir'], 'gaode')
        os.makedirs(self.output_dir, exist_ok=True)

    def get_driving_route(self, origin, destination, timestamp=None):
        """获取驾车路线数据"""
        endpoint = "/direction/driving"

        # 将中文地址转换为经纬度
        origin_location = self._geocode(origin)
        destination_location = self._geocode(destination)

        if not origin_location or not destination_location:
            print(f"无法获取 {origin} 或 {destination} 的经纬度")
            return None

        params = {
            "origin": origin_location,
            "destination": destination_location,
            "key": self.api_key,
            "output": "json",
            "strategy": 0  # 0表示速度优先
        }

        if timestamp:
            # 高德地图API没有直接的时间参数，这里仅作为文件名标记
            pass

        try:
            response = requests.get(self.base_url + endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # 检查API返回状态
            if data.get('status') != '1':
                print(f"高德地图API请求失败: {data.get('info', '未知错误')}")
                return None

            # 保存数据
            filename = f"driving_route_{origin}_{destination}_{timestamp or 'now'}.json"
            with open(os.path.join(self.output_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 控制API请求频率，避免超限
            time.sleep(1)

            return data
        except requests.exceptions.RequestException as e:
            print(f"高德地图API请求错误: {e}")
            return None

    def _geocode(self, address):
        """将地址转换为经纬度"""
        endpoint = "/geocode/geo"
        params = {
            "address": address,
            "key": self.api_key
        }

        try:
            response = requests.get(self.base_url + endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == '1' and data.get('count', '0') > '0':
                location = data['geocodes'][0]['location']
                return location

            return None
        except requests.exceptions.RequestException:
            return None


# 示例使用
if __name__ == "__main__":
    api = GaodeMapAPI()
    origin = "北京市海淀区中关村"
    destination = "北京市朝阳区国贸"
    route_data = api.get_driving_route(origin, destination)
    if route_data:
        print(f"成功获取高德地图路线数据，距离: {route_data['route']['paths'][0]['distance']}米")