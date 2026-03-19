import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone, timedelta
import time
import re

# 定义北京时间时区（UTC+8）
BJ_TIMEZONE = timezone(timedelta(hours=8))

def get_beijing_time():
    """获取当前北京时间"""
    utc_now = datetime.now(timezone.utc)
    return utc_now.astimezone(BJ_TIMEZONE)

def fetch_78500_data():
    """
    从 kaijiang.78500.cn 获取双色球历史数据
    """
    print("正在连接开奖网站 78500.cn...")
    
    url = "https://kaijiang.78500.cn/ssq/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://kaijiang.78500.cn/'
    }
    
    try:
        time.sleep(3)
        response = requests.get(url, headers=headers, timeout=20)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"请求失败: {response.status_code}")
            return None
            
        response.encoding = 'utf-8'
        html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        
        history = []
        # 找到所有表格行
        rows = soup.find_all('tr')
        print(f"找到 {len(rows)} 行数据，开始解析...")
        
        for row in rows:
            try:
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue
                
                # 提取期号
                issue_cell = cells[0]
                issue_link = issue_cell.find('a')
                if issue_link:
                    issue_text = issue_link.text.strip()
                else:
                    issue_text = issue_cell.text.strip()
                
                issue_match = re.search(r'(\d{6,7})', issue_text)
                if not issue_match:
                    continue
                issue = issue_match.group(1)
                
                # 提取日期
                date_text = cells[1].text.strip()
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                date = date_match.group(1) if date_match else ""
                
                # 提取开奖号码
                number_cell = cells[2]
                
                # 方法1: 查找球号元素
                ball_spans = number_cell.find_all('span', class_=re.compile('ball'))
                
                if ball_spans and len(ball_spans) >= 7:
                    numbers = []
                    for span in ball_spans[:7]:
                        num_text = span.text.strip()
                        if num_text.isdigit():
                            numbers.append(int(num_text))
                    
                    if len(numbers) == 7:
                        red_balls = numbers[:6]
                        blue_ball = numbers[6]
                        
                        if all(1 <= r <= 33 for r in red_balls) and 1 <= blue_ball <= 16:
                            history.append({
                                "issue": issue,
                                "date": date,
                                "red": sorted(red_balls),
                                "blue": blue_ball
                            })
                            print(f"解析成功: {issue} -> {red_balls} + {blue_ball}")
                            continue
                
                # 方法2: 直接提取文本中的数字
                cell_text = number_cell.get_text(strip=True)
                all_numbers = re.findall(r'(\d{1,2})', cell_text)
                
                if len(all_numbers) >= 7:
                    numbers = [int(x) for x in all_numbers[:7]]
                    red_balls = numbers[:6]
                    blue_ball = numbers[6]
                    
                    if all(1 <= r <= 33 for r in red_balls) and 1 <= blue_ball <= 16:
                        history.append({
                            "issue": issue,
                            "date": date,
                            "red": sorted(red_balls),
                            "blue": blue_ball
                        })
                        print(f"解析成功: {issue} -> {red_balls} + {blue_ball}")
                
            except Exception as e:
                continue
        
        # 按期号倒序排序
        history.sort(key=lambda x: int(x["issue"]), reverse=True)
        history = history[:100]
        
        print(f"\n✅ 成功解析 {len(history)} 期真实数据")
        return history
        
    except Exception as e:
        print(f"抓取过程出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 60)
    print("双色球阳光开奖数据自动抓取工具")
    print("数据源: kaijiang.78500.cn")
    print("=" * 60)
    
    history = fetch_78500_data()
    
    if history and len(history) > 0:
        # 使用北京时间作为更新时间
        beijing_now = get_beijing_time()
        
        output = {
            "lastUpdated": beijing_now.strftime("%Y-%m-%d %H:%M:%S"),
            "history": history,
            "source": "78500.cn"
        }
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据文件更新成功！共 {len(history)} 期")
        print(f"📅 更新时间 (北京时间): {output['lastUpdated']}")
        
        print("\n📊 最近3期数据验证:")
        for i, item in enumerate(history[:3]):
            print(f"  第{item['issue']}期 ({item['date']}): 红球{item['red']} + 蓝球{item['blue']}")
            
    else:
        print("\n❌ 数据抓取失败")
        exit(1)

if __name__ == "__main__":
    main()
