# src/data_analysis/route_comparison.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os
import configparser

# 加载配置
config = configparser.ConfigParser()
config.read('../config/config.ini')


class RouteAnalyzer:
    def __init__(self):
        self.processed_data_dir = config['settings']['processed_data_dir']
        self.results_dir = config['settings']['results_dir']
        os.makedirs(self.results_dir, exist_ok=True)

    def load_route_data(self):
        """加载处理后的路线数据"""
        baidu_data_path = os.path.join(self.processed_data_dir, 'baidu_routes.csv')
        gaode_data_path = os.path.join(self.processed_data_dir, 'gaode_routes.csv')

        baidu_df = pd.read_csv(baidu_data_path) if os.path.exists(baidu_data_path) else None
        gaode_df = pd.read_csv(gaode_data_path) if os.path.exists(gaode_data_path) else None

        return baidu_df, gaode_df

    def compare_route_services(self):
        """比较不同地图服务的路线推荐差异"""
        baidu_df, gaode_df = self.load_route_data()

        if baidu_df is None or gaode_df is None:
            print("数据不足，无法进行比较分析")
            return

        # 假设两个数据集都有相同的路线和时间戳，可以进行合并
        # 实际应用中，可能需要根据路线起点、终点和时间戳进行匹配
        merged_df = pd.merge(baidu_df, gaode_df,
                             on=['origin', 'destination', 'timestamp'],
                             suffixes=('_baidu', '_gaode'))

        # 计算差异
        merged_df['distance_diff'] = merged_df['distance_baidu'] - merged_df['distance_gaode']
        merged_df['duration_diff'] = merged_df['duration_baidu'] - merged_df['duration_gaode']

        # 保存比较结果
        comparison_path = os.path.join(self.results_dir, 'route_comparison.csv')
        merged_df.to_csv(comparison_path, index=False)

        # 可视化差异
        self._visualize_route_differences(merged_df)

        # 相关性分析
        self._analyze_traffic_factors(merged_df)

        return merged_df

    def _visualize_route_differences(self, df):
        """可视化路线推荐差异"""
        plt.figure(figsize=(12, 10))

        # 距离差异分布
        plt.subplot(2, 2, 1)
        sns.histplot(df['distance_diff'], kde=True)
        plt.title('路线距离差异分布')
        plt.xlabel('距离差异 (米)')
        plt.ylabel('频次')

        # 时间差异分布
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

        # 保存图表
        fig_path = os.path.join(self.results_dir, 'route_comparison_charts.png')
        plt.tight_layout()
        plt.savefig(fig_path)
        plt.close()

    def _analyze_traffic_factors(self, df):
        """分析交通拥堵影响因素"""
        # 假设我们有天气数据和POI数据
        weather_data_path = os.path.join(self.processed_data_dir, 'weather_data.csv')
        poi_data_path = os.path.join(self.processed_data_dir, 'poi_data.csv')

        if os.path.exists(weather_data_path) and os.path.exists(poi_data_path):
            weather_df = pd.read_csv(weather_data_path)
            poi_df = pd.read_csv(poi_data_path)

            # 合并数据
            analysis_df = pd.merge(df, weather_df, on='timestamp')
            # 可能需要更复杂的合并逻辑，基于位置和时间

            # 相关性分析
            correlation = analysis_df.corr()

            # 可视化相关性
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation, annot=True, cmap='coolwarm')
            plt.title('交通拥堵影响因素相关性分析')
            plt.tight_layout()

            corr_path = os.path.join(self.results_dir, 'traffic_correlation.png')
            plt.savefig(corr_path)
            plt.close()