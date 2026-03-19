import requests
import json
from datetime import datetime

url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
params = {
    "name": "ssq",
    "issueCount": "100",
    "pageNo": "1",
    "pageSize": "100",
    "systemType": "PC"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "http://www.cwl.gov.cn/ygkj/wqkjgg/ssq/"
}
try:
    print("正在连接中彩网...")
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    print(f"HTTP状态码: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"请求失败: {resp.status_code}")
        exit(1)
        
    data = resp.json()
    print(f"获取到数据: {len(data.get('result', []))} 条")
    
    result = data["result"]
    # 转换为统一格式
    history = []
    for item in result:
        red = list(map(int, item["red"].split(",")))
        blue = int(item["blue"])
        history.append({
            "issue": item["code"],
            "date": item["date"],
            "red": red,
            "blue": blue
        })
    # 按期号倒序（最新在前）
    history.sort(key=lambda x: x["issue"], reverse=True)
    output = {
        "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "history": history
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("✅ 数据更新成功！")
    print(f"共获取 {len(history)} 期数据")
    
except Exception as e:
    print(f"❌ 抓取失败: {e}")
    exit(1)
