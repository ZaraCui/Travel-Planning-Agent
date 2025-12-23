#!/usr/bin/env python3
"""
高德地图 Web 服务 API - 景点数据采集脚本
使用高德地图的 POI 搜索服务获取景点信息
"""

import requests
import json
import time
import os
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取 API Key
GAODE_API_KEY = os.getenv('GAODE_API_KEY')
if not GAODE_API_KEY:
    print("❌ 错误: GAODE_API_KEY 环境变量未设置")
    print("请在 .env 文件中设置 GAODE_API_KEY，或运行:")
    print("export GAODE_API_KEY='your_actual_key'")
    exit(1)

API_URL = "https://restapi.amap.com/v3/place/text"

# 城市列表（中英文对应）
CITIES = {
    "beijing": "北京",
    "shanghai": "上海",
    "guangzhou": "广州",
    "shenzhen": "深圳",
    "chengdu": "成都",
    "hangzhou": "杭州",
    "suzhou": "苏州",
    "nanjing": "南京",
    "qingdao": "青岛",
    "xiamen": "厦门",
    "wuhan": "武汉",
    "xian": "西安",
    "changchun": "长春",
    "harbin": "哈尔滨",
    "shenyang": "沈阳",
    "taiyuan": "太原",
    "lanzhou": "兰州",
    "xining": "西宁",
    "urumqi": "乌鲁木齐",
    "kunming": "昆明",
    "guiyang": "贵阳",
    "nanning": "南宁",
    "fuzhou": "福州",
    "hefei": "合肥",
    "zhengzhou": "郑州",
    "jinan": "济南",
}

def fetch_scenic_data(city_name: str, page: int = 1) -> Optional[Dict]:
    """
    从高德地图 API 获取景点数据
    
    Args:
        city_name: 城市名称（中文）
        page: 页码（起始 1）
    
    Returns:
        API 返回的结果或 None
    """
    params = {
        'key': GAODE_API_KEY,
        'keywords': '景点',  # 搜索关键词
        'region': city_name,  # 指定城市
        'output': 'json',
        'pagesize': 50,  # 每页最多 50 条
        'page': page,
        'citylimit': True  # 限制在指定城市内
    }
    
    try:
        response = requests.get(API_URL, params=params, timeout=15)
        response.encoding = 'utf-8'
        data = response.json()
        
        if data.get('status') == '1':
            return data
        else:
            reason = data.get('info', 'Unknown error')
            print(f"    ❌ 高德 API 错误: {reason}")
            return None
    except requests.exceptions.Timeout:
        print(f"    ❌ 请求超时")
        return None
    except Exception as e:
        print(f"    ❌ 请求失败: {e}")
        return None

def convert_to_spot_format(poi_item: Dict, city_name: str) -> Dict:
    """
    将高德地图 POI 格式转换为标准 Spot 格式
    
    Args:
        poi_item: 高德 POI 项
        city_name: 城市名称
    
    Returns:
        转换后的景点数据
    """
    name = poi_item.get('name', '').strip()
    
    # 获取坐标（格式：经度,纬度）
    location = poi_item.get('location', '')
    lat, lon = 0.0, 0.0
    if location and ',' in location:
        try:
            lon_str, lat_str = location.split(',')
            lat = float(lat_str)
            lon = float(lon_str)
        except:
            pass
    
    # 获取地址和电话作为描述
    address = poi_item.get('address', '')
    tel = poi_item.get('tel', '')
    type_info = poi_item.get('type', '')
    
    # 构建描述
    description_parts = []
    if tel:
        description_parts.append(f"电话: {tel}")
    if address:
        description_parts.append(f"地址: {address}")
    if type_info:
        description_parts.append(f"类别: {type_info}")
    
    description = " | ".join(description_parts) if description_parts else f"位于{city_name}的知名景点"
    
    # 根据类型或名称推断分类
    category = "sightseeing"
    type_lower = type_info.lower() if type_info else ""
    name_lower = name.lower()
    
    if any(word in type_lower for word in ['博物馆', 'museum']):
        category = "museum"
    elif any(word in type_lower for word in ['公园', 'park', '森林', 'forest', '山', 'mountain']):
        category = "outdoor"
    elif any(word in type_lower for word in ['古城', 'ancient', '遗址', 'ruins', '古迹', 'historic', '纪念', '宫', '庙', '塔']):
        category = "history"
    elif any(word in name_lower for word in ['博物馆', '美术馆', '纪念馆']):
        category = "museum"
    elif any(word in name_lower for word in ['公园', '山', '湖', '江', '海', '森林']):
        category = "outdoor"
    elif any(word in name_lower for word in ['古城', '古迹', '遗址', '宫', '庙', '塔', '桥']):
        category = "history"
    
    # 默认评分 4.0
    rating = 4.0
    
    # 默认访问时间 2 小时
    duration_minutes = 120
    
    return {
        'name': name,
        'category': category,
        'duration_minutes': duration_minutes,
        'rating': rating,
        'lat': lat,
        'lon': lon,
        'description': description,
        'city': city_name,
    }

def fetch_city_spots(city_en: str, city_cn: str) -> List[Dict]:
    """
    获取城市的所有景点
    
    Args:
        city_en: 城市英文名
        city_cn: 城市中文名
    
    Returns:
        景点列表
    """
    print(f"\n正在获取 {city_cn} 的景点数据...")
    
    all_spots = []
    page = 1
    max_pages = 50  # 最多获取 50 页（2500 条景点）
    
    while page <= max_pages:
        print(f"  [第 {page} 页...]", end=' ', flush=True)
        
        result = fetch_scenic_data(city_cn, page=page)
        
        if not result:
            print("失败，停止")
            break
        
        pois = result.get('pois', [])
        if not pois:
            print("完成（无更多数据）")
            break
        
        print(f"{len(pois)} 个景点", end='')
        
        # 转换格式
        for poi in pois:
            spot = convert_to_spot_format(poi, city_cn)
            all_spots.append(spot)
        
        # 检查是否有下一页
        count = result.get('count', '0')
        try:
            total = int(count)
            if len(all_spots) >= total:
                print(" ✓ 全部获取")
                break
            else:
                print()
        except:
            print()
        
        page += 1
        # 避免 API 限流
        time.sleep(0.5)
    
    print(f"  ✅ 共获得 {len(all_spots)} 个景点")
    return all_spots

def save_spots_to_file(city_en: str, spots: List[Dict]) -> bool:
    """
    将景点数据保存到 JSON 文件
    
    Args:
        city_en: 城市英文名
        spots: 景点列表
    
    Returns:
        是否成功保存
    """
    output_path = Path(f'data/spots_{city_en}.json')
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(spots, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"    ❌ 保存文件失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("🌍 高德地图 Web 服务 API - 景点数据采集")
    print("=" * 70)
    
    total_cities = len(CITIES)
    completed = 0
    successful = 0
    
    for city_en, city_cn in CITIES.items():
        completed += 1
        print(f"\n[{completed}/{total_cities}] 处理 {city_cn}")
        
        # 获取景点数据
        spots = fetch_city_spots(city_en, city_cn)
        
        if spots:
            # 保存到文件
            if save_spots_to_file(city_en, spots):
                print(f"  💾 数据已保存到 data/spots_{city_en}.json")
                successful += 1
            else:
                print(f"  ⚠️ {city_cn} 数据获取成功，但保存失败")
        else:
            print(f"  ⚠️ {city_cn} 未获取到景点数据")
        
        # 避免过于频繁的请求
        if completed < total_cities:
            time.sleep(1)
    
    print("\n" + "=" * 70)
    print(f"✨ 数据采集完成！成功更新 {successful}/{total_cities} 个城市")
    print("=" * 70)

if __name__ == '__main__':
    main()
