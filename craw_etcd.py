import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin
from tqdm import tqdm  # 进度条

# 配置参数
BASE_URL = "https://learn.lianglianglee.com/专栏/etcd实战课"
CATALOG_URL = "https://learn.lianglianglee.com/%e4%b8%93%e6%a0%8f/etcd%e5%ae%9e%e6%88%98%e8%af%be"  # 目录页
OUTPUT_DIR = "etcd_tutorial"  # 保存目录
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

def extract_links_from_catalog():
    """从目录页提取所有文章链接"""
    try:
        print("🔍 正在获取目录页内容...")
        response = requests.get(CATALOG_URL, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含所有文章的容器 - 根据实际结构调整
        catalog_section = soup.find('div', class_='catalog') or soup.find('ul', class_='posts-list')
        
        if not catalog_section:
            # 如果找不到特定容器，尝试通用方法
            all_links = soup.find_all('a', href=True)
            article_links = []
            for link in all_links:
                href = link['href']
                if "/etcd%e5%ae%9e%e6%88%98%e8%af%be/" in href and href.endswith('.md'):
                    article_links.append(href)
        else:
            # 从目录容器提取精确链接
            article_links = [
                a['href'] for a in catalog_section.find_all('a', href=True) 
                if a['href'].endswith('.md')
            ]
        
        # 去重并生成完整URL
        article_links = list(set(article_links))
        full_urls = [urljoin(BASE_URL, link) for link in article_links]
        
        print(f"✅ 找到 {len(full_urls)} 篇文章")
        return full_urls
        
    except Exception as e:
        print(f"❌ 获取目录失败: {str(e)}")
        return []

def download_article(url):
    """下载单篇文章并保存为Markdown"""
    try:
        # 获取文件名
        filename = unquote(url.split('/')[-1]).replace('.md', '')
        safe_filename = re.sub(r'[\\/*?:"<>|]', "", filename) + ".md"
        
        # 下载内容
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        # 直接保存原始Markdown内容
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, safe_filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ 已保存: {safe_filename}")
        return True
        
    except Exception as e:
        print(f"❌ 下载失败 [{url}]: {str(e)}")
        return False

def main():
    # 获取所有文章链接
    article_urls = extract_links_from_catalog()
    
    if not article_urls:
        print("⚠️ 未找到文章链接，请检查目录页结构")
        return
    
    # 批量下载
    print("⏬ 开始下载文章...")
    success_count = 0
    
    for url in tqdm(article_urls, desc="下载进度"):
        if download_article(url):
            success_count += 1
        time.sleep(3)  # 请求间隔
    
    print(f"\n🎉 下载完成! 成功: {success_count}/{len(article_urls)}")

if __name__ == "__main__":
    main()