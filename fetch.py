import requests
import json
from datetime import datetime
import time

def fetch_kaicai_data():
    """
    从开彩API获取双色球历史数据
    接口来源：http://www.opencai.net/apifree/
    """
    print("正在连接开彩API...")
    
    # 开彩API双色球接口
    url = "http://www.opencai.net/apifree/"
    
    params = {
        'caipiaoid': 'ssq',  # 双色球ID
        'format': 'json',
        'num': '100'  # 获取最近100期
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    try:
        # 添加延时，避免请求过快
        time.sleep(2)
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"请求失败: {response.status_code}")
            return None
            
        data = response.json()
        
        # 开彩API返回格式示例
        # {
        #   "data": [
        #     {
        #       "date": "2017-09-21",
        #       "haoma": "02,08,11,15,19,28|09",
        #       "qi": "2017111"
        #     }
        #   ]
        # }
        
        items = data.get('data', [])
        print(f"获取到 {len(items)} 条数据")
        
        history = []
        for item in items:
            try:
                issue = item.get('qi', '')
                date = item.get('date', '')
                haoma = item.get('haoma', '')
                
                # 解析开奖号码
                if '|' in haoma:
                    red_part, blue_part = haoma.split('|')
                    reds = [int(x) for x in red_part.split(',') if x.strip().isdigit()]
                    blue = int(blue_part) if blue_part.strip().isdigit() else 0
                    
                    if len(reds) == 6 and 1 <= blue <= 16:
                        history.append({
                            "issue": issue,
                            "date": date,
                            "red": sorted(reds),
                            "blue": blue
                        })
                        print(f"解析成功: {issue} -> {reds} + {blue}")
                        
            except Exception as e:
                print(f"解析出错: {e}")
                continue
        
        # 按期号倒序排序
        history.sort(key=lambda x: x["issue"], reverse=True)
        
        print(f"\n✅ 成功解析 {len(history)} 期真实数据")
        return history
        
    except Exception as e:
        print(f"抓取过程出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_fallback_data():
    """生成备用数据（当API完全不可用时）"""
    print("使用备用数据生成模式...")
    from datetime import timedelta
    import random
    
    history = []
    base_issue = 26030
    base_date = datetime.now()
    
    for i in range(100):
        issue = str(base_issue - i)
        date = (base_date - timedelta(days=i*3)).strftime("%Y-%m-%d")
        reds = sorted(random.sample(range(1, 34), 6))
        blue = random.randint(1, 16)
        history.append({
            "issue": issue,
            "date": date,
            "red": reds,
            "blue": blue
        })
    
    return history

def main():
    print("=" * 50)
    print("双色球阳光开奖数据抓取工具 (开彩API)")
    print("=" * 50)
    
    # 尝试抓取真实数据
    history = fetch_kaicai_data()
    
    # 如果抓取失败，使用备用数据
    if not history or len(history) == 0:
        print("⚠️ API抓取失败，使用备用数据...")
        history = generate_fallback_data()
        source = "fallback"
    else:
        source = "opencai.net"
    
    # 保存数据
    output = {
        "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "history": history,
        "source": source
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据文件生成成功！共 {len(history)} 期")
    print(f"📅 更新时间: {output['lastUpdated']}")
    print(f"📊 数据来源: {source}")
    if len(history) > 0:
        print(f"📊 最新期号: {history[0]['issue']}")
        print(f"  红球: {history[0]['red']} + 蓝球: {history[0]['blue']}")

if __name__ == "__main__":
    main()
