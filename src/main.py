# src/main.py
import os
import sys
from data_collection.collect_all_data import collect_route_data, collect_weather_data
from data_preprocessing.combined_data_processing import CombinedDataProcessor
from data_analysis.traffic_analysis import TrafficAnalyzer
from visualization.combined_visualization import Visualizer


def main():
    """运行完整的数据分析流程"""
    print("开始多源数据融合下的路径推荐差异分析与交通拥堵影响因素研究...")

    # 1. 数据收集
    print("\n=== 步骤1: 数据收集 ===")
    collect_route_data()
    collect_weather_data()

    # 2. 数据处理
    print("\n=== 步骤2: 数据处理 ===")
    processor = CombinedDataProcessor()
    processor.merge_route_data()
    processor.merge_with_weather_data()

    # 3. 数据分析
    print("\n=== 步骤3: 数据分析 ===")
    analyzer = TrafficAnalyzer()
    analyzer.analyze_route_differences()
    analyzer.analyze_traffic_factors()
    analyzer.create_traffic_heatmap()

    # 4. 数据可视化
    print("\n=== 步骤4: 数据可视化 ===")
    visualizer = Visualizer()
    visualizer.visualize_route_comparison()
    visualizer.visualize_weather_impact()

    # 创建示例路线地图
    visualizer.create_route_map(
        "北京市海淀区中关村",
        "北京市朝阳区国贸"
    )

    print("\n分析完成! 结果已保存到 results 目录。")


if __name__ == "__main__":
    main()