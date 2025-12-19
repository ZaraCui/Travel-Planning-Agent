#!/usr/bin/env python3
"""
拆分中国城市景点JSON文件
将spots_china_cities.json拆分成每个城市一个单独的JSON文件
"""
import json
import os
from collections import defaultdict

def split_china_spots():
    # 读取合并的JSON文件
    input_file = 'data/spots_china_cities.json'
    
    print(f"正在读取 {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        all_spots = json.load(f)
    
    print(f"总共读取了 {len(all_spots)} 个景点")
    
    # 按城市分组
    spots_by_city = defaultdict(list)
    for spot in all_spots:
        city = spot.get('city', 'Unknown')
        spots_by_city[city].append(spot)
    
    print(f"\n发现 {len(spots_by_city)} 个城市:")
    for city, spots in sorted(spots_by_city.items()):
        print(f"  - {city}: {len(spots)} 个景点")
    
    # 为每个城市创建单独的JSON文件
    print("\n开始创建单独的JSON文件...")
    for city, spots in spots_by_city.items():
        # 将城市名转换为文件名（小写，处理特殊字符）
        city_filename_map = {
            'Beijing': 'beijing',
            'Shanghai': 'shanghai',
            'Guangzhou': 'guangzhou',
            'Shenzhen': 'shenzhen',
            'Hangzhou': 'hangzhou',
            'Chengdu': 'chengdu',
            'Chongqing': 'chongqing',
            'Wuhan': 'wuhan',
            'Xi\'an': 'xian',
            'Suzhou': 'suzhou',
            'Tianjin': 'tianjin',
            'Nanjing': 'nanjing',
            'Qingdao': 'qingdao',
            'Dalian': 'dalian',
            'Xiamen': 'xiamen',
            'Shantou': 'shantou',
            'Ningbo': 'ningbo',
            'Kunming': 'kunming',
            'Harbin': 'harbin',
            'Changsha': 'changsha',
            'Hong Kong': 'hongkong',
            'Macau': 'macau',
        }
        
        filename = city_filename_map.get(city, city.lower().replace(' ', '').replace('\'', ''))
        output_file = f'data/spots_{filename}.json'
        
        # 写入JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(spots, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ 已创建 {output_file} ({len(spots)} 个景点)")
    
    print(f"\n完成！共创建了 {len(spots_by_city)} 个城市的JSON文件")

if __name__ == '__main__':
    split_china_spots()
