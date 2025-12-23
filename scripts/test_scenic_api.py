#!/usr/bin/env python3
"""
旅游景区大全 API 集成脚本
使用 AppKey 获取国内景点数据
"""

import requests
import json
from pathlib import Path

# 请替换为你的实际 AppKey
APP_KEY = "a28000267bc0de25bb76f84a619adcb6"  # 替换为你的完整 key

def get_spots_from_api(city_name):
    """
    从旅游景区大全 API 获取景点数据
    
    Args:
        city_name: 城市名称 (如: 北京, 上海, 深圳)
    
    Returns:
        list: 景点列表
    """
    print(f"\n正在从 API 获取 {city_name} 的景点数据...")
    
    # 尝试多个可能的 API 端点
    api_endpoints = [
        "https://apistore.amap.com/v1/scenic",  # 原始端点
        "https://api.amap.com/v1/scenic",       # 备选端点
        "https://restapi.amap.com/v3/place/text", # 高德 POI 搜索
    ]
    
    for url in api_endpoints:
        print(f"\n尝试端点: {url}")
        
        # 根据 URL 使用不同的参数
        if "scenic" in url:
            params = {
                'city': city_name,
                'key': APP_KEY,
                'page': 1,
                'pagesize': 50
            }
        else:
            # 高德 POI 搜索
            params = {
                'keywords': city_name + '旅游景点',
                'key': APP_KEY,
                'region': city_name,
                'output': 'json',
                'pagesize': 50
            }
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容长度: {len(response.text)}")
            
            if response.text:
                print(f"响应的前 300 字符: {response.text[:300]}")
                
                # 尝试解析 JSON
                try:
                    data = response.json()
                    print(f"✅ JSON 解析成功，这个端点可用！")
                    print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                    return data
                except json.JSONDecodeError as je:
                    print(f"JSON 解析失败: {je}")
                    continue
            else:
                print(f"返回空响应")
                continue
        except Exception as e:
            print(f"请求失败: {e}")
            continue
    
    print(f"\n❌ 所有端点都失败了")
    return None

if __name__ == '__main__':
    # 先测试一个城市
    result = get_spots_from_api("北京")
    
    # 检查返回的数据格式，帮助我们后续映射
    if result:
        print("\n✅ 数据获取成功")
        print(f"数据类型: {type(result)}")
        if isinstance(result, dict):
            print(f"键: {result.keys()}")
