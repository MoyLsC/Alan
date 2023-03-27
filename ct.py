from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re
import urllib.request
from urllib.parse import urlparse
import ssl

# 禁用SSL证书验证
context = ssl._create_unverified_context()

# 创建Chrome浏览器实例
driver = webdriver.Chrome()

# 打开网页
driver.get("https://www.goyard.com/eu_fr/sacs/sacs-mini.html")

# 等待元素加载完成，点击同意隐私协议
wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
element.click()
driver.implicitly_wait(10)

# 获取所有包含class="product photo product-item-photo"的节点
nodes = driver.find_elements_by_xpath('//a[@class="product photo product-item-photo"]')

# 遍历所有节点，获取a标签下的href链接,并存储到列表中
links = []
for node in nodes:
    link = node.get_attribute("href")
    links.append(link)

# 展开所有颜色，并保存图片
for link in links:
    driver.get(link)
    driver.implicitly_wait(10)
    # 获取商品名称并作为文件夹名称
    title = driver.find_element_by_xpath('//h1[@class="page-title"]/span').text
    # 去掉商品名称中的非法字符
    title = "".join(c for c in title if c.isalnum() or c.isspace())
    if not os.path.exists(title):
        os.makedirs(title)
    # 提取尺寸信息
    height = driver.find_element_by_xpath('//ul[@class="product-info-feature"]/li//span[@itemprop="height"]')
    width = driver.find_element_by_xpath('//ul[@class="product-info-feature"]/li//span[@itemprop="width"]')
    length = driver.find_element_by_xpath('//ul[@class="product-info-feature"]/li//span[@itemprop="length"]')
    size_info = "尺寸：" + height.text + " x " + width.text + " x " + length.text

    # 提取重量信息
    weight = driver.find_element_by_xpath('//ul[@class="product-info-feature"]/li//span[@itemprop="weight"]')
    weight_info = "重量：" + weight.text

    # 提取材质信息
    primary_texture = driver.find_element_by_xpath('//ul[@class="product-info-feature"]/li//span[@itemprop="primary-texture"]')
    secondary_texture = driver.find_element_by_xpath('//ul[@class="product-info-feature"]/li//span[@itemprop="secondary-texture"]')
    texture_info = "材质：" + primary_texture.text + " & " + secondary_texture.text

    with open(f'{title}/product_info.txt', 'w') as f:
        f.write(size_info + '\n')
        f.write(weight_info + '\n')
        f.write(texture_info + '\n')
    
    node = driver.find_element_by_xpath('//div[@class="swatch-attribute couleur"]/div')
    children = node.find_elements_by_xpath('./*')
    for child in children:
        child.click()
        # 使用显式等待等待图片加载完成
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//img[@class="fotorama__img--full"]')))
        # 获取颜色名称
        color = child.get_attribute('aria-label')
        # 去掉颜色名称中的非法字符
        color = "".join(c for c in color if c.isalnum() or c.isspace())
        if not os.path.exists(f'{title}/{color}'):
            os.makedirs(f'{title}/{color}')  
        # 获取所有图片，并保存
        imgs = driver.find_elements_by_xpath('//img[@class="fotorama__img--full"]')
        for img in imgs:
            url = img.get_attribute('src')
            response = urllib.request.urlopen(url, context=context)
            # 检查请求响应状态码
            if response.status == 200:
                # 获取图片文件名
                filename = os.path.basename(urlparse(url).path)
                # 保存到以颜色名称命名的子文件夹中
                with open(f'{title}/{color}/{filename}', 'wb') as f:
                    f.write(response.read())
                    print(f'Saved image {filename} in {color} folder of {title} folder.')
            else:
                print(f'Request failed with status code {response.status}.')
        time.sleep(1)

# 关闭浏览器
driver.quit()


