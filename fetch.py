import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re

def fetch_78500_data():
    """
    从 kaijiang.78500.cn 获取双色球历史数据
    该网站数据与福彩中心官网同步更新
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
        # 添加延时，模拟人类访问
        time.sleep(3)
        
        response = requests.get(url, headers=headers, timeout=20)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"请求失败: {response.status_code}")
            return None
            
        response.encoding = 'utf-8'
        html = response.text
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 找到数据表格 - 根据您提供的截图，数据在一个表格中
        # 方法1: 找到包含期号的表格行
        history = []
        
        # 查找所有表格行，通常数据在 <tr> 标签中
        rows = soup.find_all('tr')
        print(f"找到 {len(rows)} 行数据，开始解析...")
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 5:  # 至少需要期号、日期、号码等几列
                continue
                
            try:
                # 提取期号（第一个td）
                issue_text = cells[0].text.strip()
                # 期号格式如 "2026029"
                issue_match = re.search(r'(\d{6,7})', issue_text)
                if not issue_match:
                    continue
                issue = issue_match.group(1)
                
                # 提取开奖时间（第二个td）
                date_text = cells[1].text.strip()
                # 日期格式如 "2026-03-17"
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                date = date_match.group(1) if date_match else ""
                
                # 提取开奖号码（第三个td）- 这是关键
                # 号码格式在一个独立的td中，例如 "06 19 22 23 28 31 05"
                number_cell = cells[2]
                # 获取所有数字
                numbers_text = number_cell.get_text(strip=True)
                # 使用正则找到所有两位数以内的数字
                all_numbers = re.findall(r'\b(\d{1,2})\b', numbers_text)
                
                if len(all_numbers) >= 7:
                    # 前6个是红球，最后1个是蓝球
                    red_balls = [int(x) for x in all_numbers[:6] if 1 <= int(x) <= 33]
                    blue_ball = int(all_numbers[6]) if len(all_numbers) > 6 and 1 <= int(all_numbers[6]) <= 16 else 0
                    
                    if len(red_balls) == 6 and 1 <= blue_ball <= 16:
                        history.append({
                            "issue": issue,
                            "date": date,
                            "red": sorted(red_balls),
                            "blue": blue_ball
                        })
                        print(f"解析成功: {issue} -> {red_balls} + {blue_ball}")
                        
            except Exception as e:
                # 静默跳过解析失败的行
                continue
        
        # 按期号倒序排序（最新在前）
        history.sort(key=lambda x: int(x["issue"]), reverse=True)
        
        # 只保留最近100期
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
    print("与官网完全同步 - 基于您提供的网站")
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
        
        # 显示最近3期验证
        print("\n📊 最近3期数据验证:")
        for i, item in enumerate(history[:3]):
            print(f"  第{item['issue']}期 ({item['date']}): 红球{item['red']} + 蓝球{item['blue']}")
            
    else:
        print("\n❌ 数据抓取失败")
        exit(1)

if __name__ == "__main__":
    main()
