#!/bin/bash
# 重新获取问题较多的中国城市数据

echo "🌍 开始重新获取中国城市景点数据..."
echo ""

# 问题较多的中国城市列表
cities=(
    "Changchun"
    "Chengdu"
    "Dongguang"
    "Foshan"
    "Fuzhou"
    "Guangzhou"
    "Guiyang"
    "Hangzhou"
    "Harbin"
    "Hefei"
    "Hongkong"
    "Kunming"
    "Lanzhou"
    "Nanjing"
    "Ningbo"
    "Qingdao"
    "Shenyang"
    "Shenzhen"
    "Shijiazhuang"
    "Suzhou"
    "Taiyuan"
    "Urumqi"
    "Xiamen"
)

total=${#cities[@]}
count=0

for city in "${cities[@]}"; do
    count=$((count + 1))
    echo "[$count/$total] 正在获取 $city 的景点数据..."
    python scripts/fetch_osm_spots_clean.py "$city" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ $city 完成"
    else
        echo "⚠️ $city 获取失败"
    fi
    # 为了避免 API 限流，每个请求间隔 2 秒
    sleep 2
done

echo ""
echo "✨ 所有城市数据获取完成！"
