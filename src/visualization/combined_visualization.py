# src/visualization/combined_visualization.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap, MarkerCluster
import os
import configparser

# 加载配置
config = configparser.ConfigParser()
config.read('../config/config.ini')


class Visualizer:
    def __init__(self):
        self.processed_data_dir = config['settings']['processed_data_dir']
        self.results_dir = config['settings']['results_dir']
        os.makedirs(self.results_dir, exist_ok=True)

    def visualize_route_comparison(self):
        """可视化不同地图服务的路线比较"""
        data_path = os.path.join(self.processed_data_dir, 'merged_routes.csv')

        if not os.path.exists(data_path):
            print("路线比较数据不存在")
            return

        df = pd.read_csv(data_path)

        # 创建图表
        plt.figure(figsize=(14, 12))

        # 1. 不同时间段的平均耗时对比
        plt.subplot(2, 2, 1)
        hour_grouped = df.groupby('hour').agg({
            'duration_baidu': 'mean',
            'duration_gaode': 'mean'
        })
        hour_grouped.plot(kind='bar', ax=plt.gca())
        plt.title('不同时间段的平均耗时对比')
        plt.xlabel('小时')
        plt.ylabel('平均耗时 (秒)')
        plt.legend(['百度地图', '高德地图'])

        # 2. 不同路线的平均耗时对比
        plt.subplot(2, 2, 2)
        route_grouped = df.groupby(['origin', 'destination']).agg({
            'duration_baidu': 'mean',
            'duration_gaode': 'mean'
        }).reset_index()

        # 创建路线名称
        route_grouped['route'] = route_grouped['origin'] + ' -> ' + route_grouped['destination']
        route_grouped.set_index('route', inplace=True)
        route_grouped.plot(kind='barh', ax=plt.gca())
        plt.title('不同路线的平均耗时对比')
        plt.xlabel('平均耗时 (秒)')
        plt.ylabel('路线')

        # 3. 耗时差异百分比分布
        plt.subplot(2, 2, 3)
        sns.histplot(df['duration_diff_percent'], kde=True, bins=20)
        plt.title('路线耗时差异百分比分布')
        plt.xlabel('耗时差异百分比 (%)')
        plt.ylabel('频次')

        # 4. 箱线图展示耗时差异
        plt.subplot(2, 2, 4)
        sns.boxplot(data=df[['duration_baidu', 'duration_gaode']])
        plt.title('路线耗时分布对比')
        plt.ylabel('耗时 (秒)')

        plt.tight_layout()
        fig_path = os.path.join(self.results_dir, 'route_comparison_charts.png')
        plt.savefig(fig_path)
        plt.close()

        print(f"路线比较图表已保存到 {fig_path}")

    def visualize_weather_impact(self):
        """可视化天气对交通的影响"""
        data_path = os.path.join(self.processed_data_dir, 'routes_with_weather.csv')

        if not os.path.exists(data_path):
            print("天气与路线合并数据不存在")
            return

        df = pd.read_csv(data_path)

        # 创建图表
        plt.figure(figsize=(14, 12))

        # 1. 天气类型与平均耗时
        plt.subplot(2, 2, 1)
        weather_grouped = df.groupby('weather_main')['duration_baidu'].mean().sort_values(ascending=False)
        weather_grouped.plot(kind='bar', ax=plt.gca())
        plt.title('不同天气条件下的平均耗时')
        plt.xlabel('天气类型')
        plt.ylabel('平均耗时 (秒)')

        # 2. 温度与耗时关系
        plt.subplot(2, 2, 2)
        sns.scatterplot(x='temperature', y='duration_baidu', data=df)
        plt.title('温度与路线耗时关系')
        plt.xlabel('温度 (°C)')
        plt.ylabel('耗时 (秒)')

        # 3. 湿度与耗时关系
        plt.subplot(2, 2, 3)
        sns.scatterplot(x='humidity', y='duration_baidu', data=df)
        plt.title('湿度与路线耗时关系')
        plt.xlabel('湿度 (%)')
        plt.ylabel('耗时 (秒)')

        # 4. 风速与耗时关系
        plt.subplot(2, 2, 4)
        sns.scatterplot(x='wind_speed', y='duration_baidu', data=df)
        plt.title('风速与路线耗时关系')
        plt.xlabel('风速 (m/s)')
        plt.ylabel('耗时 (秒)')

        plt.tight_layout()
        fig_path = os.path.join(self.results_dir, 'weather_impact_charts.png')
        plt.savefig(fig_path)
        plt.close()

        print(f"天气影响图表已保存到 {fig_path}")

    def create_route_map(self, origin, destination):
        """创建指定路线的地图可视化"""
        data_path = os.path.join(self.processed_data_dir, 'routes_with_weather.csv')

        if not os.path.exists(data_path):
            print("路线数据不存在")
            return

        df = pd.read_csv(data_path)

        # 筛选特定路线的数据
        route_data = df[(df['origin'] == origin) & (df['destination'] == destination)]

        if route_data.empty:
            print(f"未找到从 {origin} 到 {destination} 的路线数据")
            return

        # 为简化示例，我们假设已经有路线的经纬度点
        # 实际应用中需要从API返回的数据中提取路线点

        # 创建地图
        # 假设起点的经纬度 (实际应用中需要从数据中提取)
        start_lat, start_lon = 39.9896, 116.3075  # 示例坐标
        m = folium.Map(location=[start_lat, start_lon], zoom_start=12)

        # 添加起点和终点标记
        folium.Marker(
            location=[start_lat, start_lon],
            popup=origin,
            icon=folium.Icon(color='green')
        ).add_to(m)

        # 终点坐标
        end_lat, end_lon = 39.9087, 116.4343  # 示例坐标
        folium.Marker(
            location=[end_lat, end_lon],
            popup=destination,
            icon=folium.Icon(color='red')
        ).add_to(m)

        # 为示例创建模拟路线
        # 实际应用中应该使用API返回的真实路线点
        route_points = [
            [start_lat, start_lon],
            [39.9650, 116.3520],  # 中间点1
            [39.9450, 116.3920],  # 中间点2
            [end_lat, end_lon]
        ]

        # 添加百度地图推荐路线
        folium.PolyLine(
            locations=route_points,
            color='blue',
            weight=5,
            opacity=0.7,
            popup='百度地图推荐路线'
        ).add_to(m)

        # 添加高德地图推荐路线 (稍有不同)
        alt_route_points = [
            [start_lat, start_lon],
            [39.9750, 116.3620],  # 替代路线中间点1
            [39.9550, 116.4020],  # 替代路线中间点2
            [end_lat, end_lon]
        ]

        folium.PolyLine(
            locations=alt_route_points,
            color='purple',
            weight=5,
            opacity=0.7,
            popup='高德地图推荐路线'
        ).add_to(m)

        # 添加地图标题
        title_html = f'''
                     <h3 align="center" style="font-size:20px"><b>{origin} 到 {destination} 的路线比较</b></h3>
                     '''
        m.get_root().html.add_child(folium.Element(title_html))

        # 保存地图
        output_path = os.path.join(self.results_dir, f'route_map_{origin}_{destination}.html')
        m.save(output_path)

        print(f"路线地图已保存到 {output_path}")

        return m