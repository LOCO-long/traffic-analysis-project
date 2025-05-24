# src/visualization/map_visualization.py
import folium
from folium.plugins import HeatMap
import pandas as pd
import os
import json
import configparser

# 加载配置
config = configparser.ConfigParser()
config.read('../config/config.ini')


class MapVisualizer:
    def __init__(self):
        self.processed_data_dir = config['settings']['processed_data_dir']
        self.results_dir = config['settings']['results_dir']
        os.makedirs(self.results_dir, exist_ok=True)

    def visualize_route_on_map(self, route_data, map_title="路线可视化", output_file="route_map.html"):
        """在地图上可视化路线"""
        # 创建地图，中心点设为路线起点
        start_location = route_data['steps'][0]['start_location']  # 假设格式为 [纬度, 经度]
        m = folium.Map(location=start_location, zoom_start=12)

        # 添加路线
        route_points = []
        for step in route_data['steps']:
            points = step.get('path', [])  # 假设每个步骤包含路径点
            route_points.extend(points)

        # 绘制路线
        folium.PolyLine(
            locations=route_points,
            color='blue',
            weight=5,
            opacity=0.7,
            popup='推荐路线'
        ).add_to(m)

        # 添加起点和终点标记
        folium.Marker(
            location=start_location,
            popup='起点',
            icon=folium.Icon(color='green')
        ).add_to(m)

        end_location = route_data['steps'][-1]['end_location']
        folium.Marker(
            location=end_location,
            popup='终点',
            icon=folium.Icon(color='red')
        ).add_to(m)

        # 添加地图标题
        title_html = f'''
                     <h3 align="center" style="font-size:20px"><b>{map_title}</b></h3>
                     '''
        m.get_root().html.add_child(folium.Element(title_html))

        # 保存地图
        output_path = os.path.join(self.results_dir, output_file)
        m.save(output_path)

        return m

    def create_traffic_heatmap(self, traffic_data, map_title="交通拥堵热力图", output_file="traffic_heatmap.html"):
        """创建交通拥堵热力图"""
        # 创建地图
        center_location = [39.9042, 116.4074]  # 北京中心点，实际应用中应根据数据调整
        m = folium.Map(location=center_location, zoom_start=10)

        # 准备热力图数据
        heat_data = []
        for _, row in traffic_data.iterrows():
            # 假设数据包含经纬度和拥堵程度
            heat_data.append([row['latitude'], row['longitude'], row['congestion_level']])

        # 添加热力图
        HeatMap(heat_data, radius=15, blur=10).add_to(m)

        # 添加地图标题
        title_html = f'''
                     <h3 align="center" style="font-size:20px"><b>{map_title}</b></h3>
                     '''
        m.get_root().html.add_child(folium.Element(title_html))

        # 保存地图
        output_path = os.path.join(self.results_dir, output_file)
        m.save(output_path)

        return m