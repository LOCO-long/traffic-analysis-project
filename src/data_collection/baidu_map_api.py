# src/data_collection/baidu_map_api.py
import requests
import json
import os
from dotenv import load_dotenv
import configparser

# 加载配置
config = configparser.ConfigParser()
config.read('../config/config.ini')
try:
    api_key = config['baidu_map']['api_key']
except KeyError:
    print("配置中缺少baidu_map相关配置")

class BaiduMapAPI:
    def __init__(self):
        self.api_key = config['baidu_map']['api_key']
        self.base_url = "https://api.map.baidu.com"
        self.output_dir = os.path.join(config['settings']['raw_data_dir'], 'baidu')
        os.makedirs(self.output_dir, exist_ok=True)

    def get_driving_route(self, origin, destination, timestamp=None):
        """获取驾车路线数据"""
        endpoint = "/direction/v2/driving"
        params = {
            "origin": origin,
            "destination": destination,
            "ak": self.api_key,
            "output": "json"
        }

        if timestamp:
            params["timestamp"] = timestamp

        try:
            response = requests.get(self.base_url + endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # 保存数据
            filename = f"driving_route_{origin}_{destination}_{timestamp or 'now'}.json"
            with open(os.path.join(self.output_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return data
        except requests.exceptions.RequestException as e:
            print(f"百度地图API请求错误: {e}")
            return None


# 示例使用
if __name__ == "__main__":
    api = BaiduMapAPI()
    origin = "北京市海淀区中关村"
    destination = "北京市朝阳区国贸"
    route_data = api.get_driving_route(origin, destination)
    if route_data:
        print(f"成功获取百度地图路线数据，距离: {route_data['result']['routes'][0]['distance']}米")