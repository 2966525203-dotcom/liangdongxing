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
尝试:
    print("正在连接中彩网...")
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    print(f"HTTP状态码: {resp.status_code}")
    
    如果响应状态码 != 200
        打印(f"请求失败:{响应状态码}")
        exit(1)
        
    data = resp.json()
    print(f"获取到数据: {len(data.get('result', []))} 条")
    
    result = data["result"]
    # 转换为统一格式
历史 =[]
    对于项在结果：
红色 =(映射(整数，项["红色"].拆分(",")))
蓝色 =整数(项["蓝色"])
历史.追加({
            “问题”: 项目[“代码”,
            “日期”: 项“日期”
            "红色": 红色,
            : 蓝色
        })
    # 按期号倒序（最新在前）
历史。排序键=lambdax: x[“问题”
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
