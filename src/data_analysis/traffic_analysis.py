# src/data_analysis/traffic_analysis.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os
import configparser
from statsmodels.formula.api import ols
import folium
from folium.plugins import HeatMap

# 加载配置
config = configparser.ConfigParser()
config.read('../config/config.ini')


class TrafficAnalyzer:
    def __init__(self):
        self.processed_data_dir = config['settings']['processed_data_dir']
        self.results_dir = config['settings']['results_dir']
        os.makedirs(self.results_dir, exist_ok=True)

    def load_analysis_data(self):
        """加载用于分析的数据"""
        data_path = os.path.join(self.processed_data_dir, 'routes_with_weather.csv')

        if not os.path.exists(data_path):
            print("分析数据不存在，请先处理数据")
            return None

        # 读取数据
        df = pd.read_csv(data_path)

        # 转换时间戳为datetime类型
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        return df

    def analyze_route_differences(self):
        """分析不同地图服务的路线推荐差异"""
        df = self.load_analysis_data()
        if df is None:
            return

        # 基本统计
        print("\n路线距离差异统计:")
        print(df['distance_diff'].describe())

        print("\n路线耗时差异统计:")
        print(df['duration_diff'].describe())

        # 可视化差异分布
        plt.figure(figsize=(12, 10))

        # 距离差异分布
        plt.subplot(2, 2, 1)
        sns.histplot(df['distance_diff'], kde=True)
        plt.title('路线距离差异分布')
        plt.xlabel('距离差异 (米)')
        plt.ylabel('频次')

        # 耗时差异分布
        plt.subplot(2, 2, 2)
        sns.histplot(df['duration_diff'], kde=True)
        plt.title('路线耗时差异分布')
        plt.xlabel('耗时差异 (秒)')
        plt.ylabel('频次')

        # 距离与耗时散点图
        plt.subplot(2, 2, 3)
        sns.scatterplot(x='distance_baidu', y='duration_baidu', label='百度地图', data=df)
        sns.scatterplot(x='distance_gaode', y='duration_gaode', label='高德地图', data=df)
        plt.title('路线距离与耗时关系')
        plt.xlabel('距离 (米)')
        plt.ylabel('耗时 (秒)')
        plt.legend()

        # 不同时间段的耗时差异
        plt.subplot(2, 2, 4)
        sns.boxplot(x='hour', y='duration_diff', data=df)
        plt.title('不同时间段的耗时差异')
        plt.xlabel('小时')
        plt.ylabel('耗时差异 (秒)')

        # 保存图表
        fig_path = os.path.join(self.results_dir, 'route_differences.png')
        plt.tight_layout()
        plt.savefig(fig_path)
        plt.close()

        # 按时间段分析差异
        hour_grouped = df.groupby('hour')['duration_diff'].mean()
        print("\n不同时间段的平均耗时差异:")
        print(hour_grouped)

        # 保存分析结果
        results_path = os.path.join(self.results_dir, 'route_differences_analysis.csv')
        hour_grouped.to_csv(results_path)

        return df

    def analyze_traffic_factors(self):
        """分析交通拥堵影响因素"""
        df = self.load_analysis_data()
        if df is None:
            return

        # 相关性分析
        numeric_columns = ['duration_baidu', 'duration_gaode', 'temperature', 'humidity', 'wind_speed', 'clouds']
        correlation = df[numeric_columns].corr()

        # 可视化相关性
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation, annot=True, cmap='coolwarm')
        plt.title('交通拥堵影响因素相关性分析')
        plt.tight_layout()

        corr_path = os.path.join(self.results_dir, 'traffic_correlation.png')
        plt.savefig(corr_path)
        plt.close()

        # 线性回归分析
        # 假设duration_baidu为因变量，分析各种因素的影响
        model = ols('duration_baidu ~ hour + day_of_week + temperature + humidity + C(weather_main)', data=df).fit()

        # 保存回归结果
        summary_path = os.path.join(self.results_dir, 'regression_summary.txt')
        with open(summary_path, 'w') as f:
            f.write(model.summary().as_text())

        print("\n线性回归分析结果已保存到", summary_path)

        # 分析不同天气条件下的平均耗时
        weather_effect = df.groupby('weather_main')['duration_baidu'].mean().sort_values(ascending=False)
        print("\n不同天气条件下的平均耗时:")
        print(weather_effect)

        return model

    def create_traffic_heatmap(self):
        """创建交通拥堵热力图"""
        df = self.load_analysis_data()
        if df is None:
            return

        # 为简化示例，假设我们有经纬度信息
        # 实际应用中需要从路线数据中提取或计算拥堵热点

        # 创建地图
        center_location = [39.9042, 116.4074]  # 北京中心点
        m = folium.Map(location=center_location, zoom_start=10)

        # 准备热力图数据 (纬度, 经度, 拥堵程度)
        # 这里使用duration_baidu作为拥堵程度的指标
        heat_data = []

        # 为示例创建模拟热点数据
        for _, row in df.iterrows():
            # 提取或计算经纬度 (这里使用简化示例)
            lat, lon = 39.9042, 116.4074  # 北京中心点

            # 添加一些随机偏移来创建热点
            lat += np.random.normal(0, 0.1)
            lon += np.random.normal(0, 0.1)

            # 使用耗时作为拥堵程度
            congestion_level = row['duration_baidu'] / 100

            heat_data.append([lat, lon, congestion_level])

        # 添加热力图
        HeatMap(heat_data, radius=15, blur=10).add_to(m)

        # 添加地图标题
        title_html = '''
                     <h3 align="center" style="font-size:20px"><b>交通拥堵热力图</b></h3>
                     '''
        m.get_root().html.add_child(folium.Element(title_html))

        # 保存地图
        output_path = os.path.join(self.results_dir, 'traffic_heatmap.html')
        m.save(output_path)

        print(f"交通拥堵热力图已保存到 {output_path}")

        return m