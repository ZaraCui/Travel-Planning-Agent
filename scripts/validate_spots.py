#!/usr/bin/env python3
"""
验证景点数据质量的脚本
检查常见问题：缺少字段、无效坐标、可疑名称、重复位置、空描述等
"""
import json
from pathlib import Path
from collections import defaultdict

def validate_spots():
    data_dir = Path('data')
    
    issues = {
        'missing_fields': [],
        'invalid_coords': [],
        'suspicious_names': [],
        'duplicate_locations': [],
        'generic_descriptions': [],
        'invalid_ratings': [],
        'invalid_duration': []
    }
    
    city_stats = {}
    
    for json_file in sorted(data_dir.glob('spots_*.json')):
        city = json_file.stem.replace('spots_', '')
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                spots = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ {city}: JSON 解析错误 - {e}")
            continue
        
        city_stats[city] = {
            'total': len(spots),
            'valid': 0,
            'issues': 0
        }
        
        coords_seen = defaultdict(list)
        
        for i, spot in enumerate(spots):
            has_issue = False
            
            # 检查必填字段
            required = ['name', 'lat', 'lon', 'category', 'rating']
            for field in required:
                if field not in spot:
                    issues['missing_fields'].append(
                        f"{city}: 景点 #{i} ({spot.get('name', 'Unknown')}) 缺少 '{field}' 字段"
                    )
                    has_issue = True
            
            # 检查坐标有效性
            lat = spot.get('lat')
            lon = spot.get('lon')
            if lat is not None and lon is not None:
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    issues['invalid_coords'].append(
                        f"{city}: {spot.get('name')} 坐标无效 ({lat}, {lon})"
                    )
                    has_issue = True
                else:
                    # 检查重复的坐标
                    coord_key = (round(lat, 4), round(lon, 4))
                    if coord_key in coords_seen:
                        # 只在首次发现时报告
                        if len(coords_seen[coord_key]) == 1:
                            issues['duplicate_locations'].append(
                                f"{city}: 坐标 ({lat}, {lon}) 被多个景点使用："
                                f" {coords_seen[coord_key][0]} 和 {spot.get('name')}"
                            )
                            has_issue = True
                    coords_seen[coord_key].append(spot.get('name', 'Unknown'))
            
            # 检查可疑的名称（包含引号或转义字符）
            name = spot.get('name', '')
            if '\"' in name or '\\' in name or name.startswith('"'):
                issues['suspicious_names'].append(
                    f"{city}: {name}"
                )
                has_issue = True
            
            # 检查评分有效性 (1-5)
            rating = spot.get('rating')
            if rating is not None and not (1 <= rating <= 5):
                issues['invalid_ratings'].append(
                    f"{city}: {spot.get('name')} 评分无效 ({rating})"
                )
                has_issue = True
            
            # 检查持续时间有效性
            duration = spot.get('duration_minutes')
            if duration is not None and duration <= 0:
                issues['invalid_duration'].append(
                    f"{city}: {spot.get('name')} 持续时间无效 ({duration} 分钟)"
                )
                has_issue = True
            
            # 检查通用/空描述
            desc = spot.get('description', '')
            if not desc or 'A popular' in desc or '是一个' in desc and len(desc) < 20:
                issues['generic_descriptions'].append(
                    f"{city}: {spot.get('name')}"
                )
                has_issue = True
            
            if not has_issue:
                city_stats[city]['valid'] += 1
            else:
                city_stats[city]['issues'] += 1
    
    # 输出报告
    print("=" * 70)
    print("📊 景点数据质量检查报告")
    print("=" * 70)
    
    # 城市统计
    print("\n🏙️ 各城市统计:")
    print("-" * 70)
    total_spots = 0
    total_issues = 0
    for city in sorted(city_stats.keys()):
        stat = city_stats[city]
        total = stat['total']
        valid = stat['valid']
        issues_count = stat['issues']
        total_spots += total
        total_issues += issues_count
        
        valid_pct = (valid / total * 100) if total > 0 else 0
        status = "✅" if issues_count == 0 else "⚠️"
        print(f"{status} {city:15} {valid:4}/{total:4} 有效 ({valid_pct:5.1f}%)")
    
    print("-" * 70)
    print(f"📈 总计: {total_spots} 个景点, {total_issues} 个存在问题")
    
    # 问题详情
    print("\n" + "=" * 70)
    print("🔍 问题详情")
    print("=" * 70)
    
    for issue_type, items in issues.items():
        if items:
            print(f"\n❌ {issue_type.upper()}: {len(items)} 个问题")
            print("-" * 70)
            # 显示前 5 个，避免输出过多
            for item in items[:5]:
                print(f"  • {item}")
            if len(items) > 5:
                print(f"  ... 还有 {len(items) - 5} 个问题")
    
    print("\n" + "=" * 70)
    
    # 建议
    print("\n💡 改进建议:")
    print("-" * 70)
    if issues['suspicious_names']:
        print("  1. 修复包含转义字符的景点名称")
    if issues['generic_descriptions']:
        print("  2. 使用更详细的景点描述")
    if issues['duplicate_locations']:
        print("  3. 合并或删除重复位置的景点")
    if issues['invalid_coords'] or issues['invalid_ratings'] or issues['invalid_duration']:
        print("  4. 修复无效的数据字段")
    if total_issues == 0:
        print("  ✅ 数据质量很好！")
    
    return issues, city_stats

if __name__ == '__main__':
    validate_spots()
