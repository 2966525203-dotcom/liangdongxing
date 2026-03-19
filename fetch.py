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
    
    # 500彩票网的历史数据接口（一次性获取所有历史数据）
    url = "https://datachart.500.com/ssq/history/newinc/history.php"
    
    # 设置一个足够大的范围，获取最近100期
    # 网站会自动返回有效范围内的所有数据
    params = {
        'start': '23001',  # 2023年第一期
        'end': '26001'     # 直到未来
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://datachart.500.com/ssq/'
    }
    
    try:
        # 添加延时，避免请求过快
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
        # 500彩票网的数据在 id="tdata" 的 tbody 中
        tbody = soup.find('tbody', id='tdata')
        
        if not tbody:
            print("未找到数据表格，页面结构可能已变化")
            return None
        
        # 获取所有数据行
        rows = tbody.find_all('tr')
        print(f"找到 {len(rows)} 行数据")
        
        history = []
        for row in rows:
            # 跳过表头行
            if 't_tr1' not in row.get('class', []):
                continue
                
            cells = row.find_all('td')
            if len(cells) < 16:  # 确保有足够的数据列
                continue
                
            try:
                # 提取数据
                issue = cells[0].text.strip()  # 期号
                
                # 红球（第2-7列，索引1-6）
                red_balls = []
                for i in range(1, 7):
                    ball = cells[i].text.strip()
                    if ball and ball.isdigit():
                        red_balls.append(int(ball))
                
                # 蓝球（第8列，索引7）
                blue_ball = int(cells[7].text.strip()) if cells[7].text.strip().isdigit() else 0
                
                # 开奖日期（通常是倒数第2列）
                date_str = cells[-2].text.strip() if len(cells) > 2 else ""
                
                # 验证数据有效性
                if len(red_balls) == 6 and 1 <= blue_ball <= 16:
                    history.append({
                        "issue": issue,
                        "date": date_str,
                        "red": sorted(red_balls),  # 排序红球
                        "blue": blue_ball
                    })
                    
            except (ValueError, IndexError) as e:
                print(f"解析行数据时出错: {e}")
                continue
        
        # 按期号倒序排序（最新在前）
        history.sort(key=lambda x: x["issue"], reverse=True)
        
        # 只保留最近100期
        history = history[:100]
        
        print(f"成功解析 {len(history)} 期数据")
        return history
        
    except Exception as e:
        print(f"抓取过程出错: {e}")
        return None

def main():
    """主函数"""
    print("=" * 50)
    print("双色球数据抓取工具 (500彩票网)")
    print("=" * 50)
    
    # 抓取数据
    history = fetch_500_com_data()
    
    if history and len(history) > 0:
        # 准备输出数据
        output = {
            "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": history,
            "source": "500.com"
        }
        
        # 保存到文件
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据更新成功！共 {len(history)} 期")
        print(f"📅 更新时间: {output['lastUpdated']}")
        
        # 显示最近3期预览
        print("\n📊 最近3期预览:")
        for i, item in enumerate(history[:3]):
            print(f"  {item['issue']}: 红球{item['red']} + 蓝球{item['blue']}")
            
    else:
        print("\n❌ 数据抓取失败")
        exit(1)

if __name__ == "__main__":
    main()
