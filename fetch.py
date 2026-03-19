import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re

def fetch_78500_data():
    """
    从 kaijiang.78500.cn 获取双色球历史数据
    修复版本：直接定位号码所在的表格单元格
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
        # 添加延时
        time.sleep(3)
        
        response = requests.get(url, headers=headers, timeout=20)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"请求失败: {response.status_code}")
            return None
            
        response.encoding = 'utf-8'
        html = response.text
        
        # 使用BeautifulSoup解析
        soup = BeautifulSoup(html, 'html.parser')
        
        history = []
        
        # 方法1: 直接查找所有包含期号链接的行
        # 在78500.cn上，期号通常在 <a> 标签内
        rows = soup.find_all('tr')
        print(f"找到 {len(rows)} 行数据，开始解析...")
        
        for row in rows:
            try:
                # 获取行中所有单元格
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue
                
                # 提取期号 - 可能在第一个td中的a标签里
                issue_cell = cells[0]
                issue_link = issue_cell.find('a')
                if issue_link:
                    issue_text = issue_link.text.strip()
                else:
                    issue_text = issue_cell.text.strip()
                
                # 期号格式应为6位数字（如202629）或更多
                issue_match = re.search(r'(\d{6,7})', issue_text)
                if not issue_match:
                    continue
                issue = issue_match.group(1)
                
                # 提取日期 - 第二个td
                date_text = cells[1].text.strip()
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                date = date_match.group(1) if date_match else ""
                
                # 提取开奖号码 - 关键修复点
                # 号码在第三个td中，格式为 "06 19 22 23 28 31 05"
                number_cell = cells[2]
                
                # 方法A: 查找所有球号元素（如果有span.ball之类的）
                ball_spans = number_cell.find_all('span', class_=re.compile('ball'))
                if ball_spans and len(ball_spans) >= 7:
                    # 从span中提取数字
                    numbers = []
                    for span in ball_spans[:7]:  # 取前7个
                        num_text = span.text.strip()
                        if num_text.isdigit():
                            numbers.append(int(num_text))
                    
                    if len(numbers) == 7:
                        red_balls = numbers[:6]
                        blue_ball = numbers[6]
                        
                        # 验证范围
                        if all(1 <= r <= 33 for r in red_balls) and 1 <= blue_ball <= 16:
                            history.append({
                                "issue": issue,
                                "date": date,
                                "red": sorted(red_balls),
                                "blue": blue_ball
                            })
                            print(f"解析成功 (方法A): {issue} -> {red_balls} + {blue_ball}")
                            continue
                
                # 方法B: 直接提取整个单元格文本中的数字
                cell_text = number_cell.get_text(strip=True)
                # 查找所有两位数以内的数字
                all_numbers = re.findall(r'(\d{1,2})', cell_text)
                
                if len(all_numbers) >= 7:
                    # 取前7个数字
                    numbers = [int(x) for x in all_numbers[:7]]
                    red_balls = numbers[:6]
                    blue_ball = numbers[6]
                    
                    # 验证范围
                    if all(1 <= r <= 33 for r in red_balls) and 1 <= blue_ball <= 16:
                        history.append({
                            "issue": issue,
                            "date": date,
                            "red": sorted(red_balls),
                            "blue": blue_ball
                        })
                        print(f"解析成功 (方法B): {issue} -> {red_balls} + {blue_ball}")
                
            except Exception as e:
                # 跳过解析失败的行
                continue
        
        # 按期号倒序排序
        history.sort(key=lambda x: int(x["issue"]), reverse=True)
        
        # 只保留最近100期
        history = history[:100]
        
        print(f"\n✅ 成功解析 {len(history)} 期真实数据")
        
        # 如果解析成功，显示前几期验证
        if history:
            print("\n📊 解析到的数据预览:")
            for i, item in enumerate(history[:3]):
                print(f"  {item['issue']} {item['date']}: {item['red']} + {item['blue']}")
        
        return history
        
    except Exception as e:
        print(f"抓取过程出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 60)
    print("双色球阳光开奖数据自动抓取工具 v2.0")
    print("数据源: kaijiang.78500.cn")
    print("与官网完全同步 - 修复解析问题")
    print("=" * 60)
    
    # 抓取数据
    history = fetch_78500_data()
    
    if history and len(history) > 0:
        # 准备输出数据
        output = {
            "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": history,
            "source": "78500.cn"
        }
        
        # 保存到文件
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据文件更新成功！共 {len(history)} 期")
        print(f"📅 更新时间: {output['lastUpdated']}")
        
    else:
        print("\n❌ 数据抓取失败，没有解析到任何期号")
        exit(1)

if __name__ == "__main__":
    main()
