import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def fetch_500_com_data():
    """
    从500彩票网获取双色球历史数据
    数据来源：https://datachart.500.com/ssq/
    与官网数据完全同步
    """
    print("正在连接500彩票网...")
    
    url = "https://datachart.500.com/ssq/history/newinc/history.php"
    params = {
        'start': '23001',
        'end': '26001'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://datachart.500.com/ssq/'
    }
    
    try:
        time.sleep(2)
        response = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"请求失败: {response.status_code}")
            return None
            
        response.encoding = 'utf-8'
        html = response.text
        
        # 解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 找到数据表格
        tbody = soup.find('tbody', id='tdata')
        
        if not tbody:
            print("未找到数据表格，尝试备用选择器...")
            tbody = soup.find('table', class_='chart-table').find('tbody')
        
        if not tbody:
            print("未找到数据表格")
            return None
        
        rows = tbody.find_all('tr')
        print(f"找到 {len(rows)} 行数据")
        
        history = []
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 7:
                continue
                
            try:
                # 期号
                issue = cells[0].text.strip()
                
                # 红球（第2-7列）
                red_balls = []
                for i in range(1, 7):
                    ball_text = cells[i].text.strip()
                    if ball_text and ball_text.isdigit():
                        red_balls.append(int(ball_text))
                
                # 蓝球（第8列）
                blue_text = cells[7].text.strip() if len(cells) > 7 else "0"
                blue_ball = int(blue_text) if blue_text.isdigit() else 0
                
                # 日期（倒数第2列或第3列）
                date_str = ""
                if len(cells) >= 3:
                    # 尝试获取日期
                    date_cell = cells[-2].text.strip() if len(cells) > 2 else ""
                    if date_cell and not date_cell.isdigit():
                        date_str = date_cell
                    else:
                        date_str = datetime.now().strftime("%Y-%m-%d")
                
                # 验证数据
                if len(red_balls) == 6 and 1 <= blue_ball <= 16:
                    history.append({
                        "issue": issue,
                        "date": date_str,
                        "red": sorted(red_balls),
                        "blue": blue_ball
                    })
                    
            except (ValueError, IndexError) as e:
                print(f"解析行数据时出错: {e}")
                continue
        
        # 按期号倒序排序
        history.sort(key=lambda x: x["issue"], reverse=True)
        history = history[:100]
        
        print(f"成功解析 {len(history)} 期数据")
        return history
        
    except Exception as e:
        print(f"抓取过程出错: {e}")
        return None

def main():
    print("=" * 50)
    print("双色球数据抓取工具 (500彩票网)")
    print("=" * 50)
    
    history = fetch_500_com_data()
    
    if history and len(history) > 0:
        output = {
            "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": history,
            "source": "500.com"
        }
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据更新成功！共 {len(history)} 期")
        print(f"📅 更新时间: {output['lastUpdated']}")
        
        print("\n📊 最近3期预览:")
        for i, item in enumerate(history[:3]):
            print(f"  {item['issue']}: 红球{item['red']} + 蓝球{item['blue']}")
            
    else:
        print("\n❌ 数据抓取失败")
        exit(1)

if __name__ == "__main__":
    main()
