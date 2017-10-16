from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import re
from pyquery import PyQuery as pq
import pymongo

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


def search():
    try:
        browser.get('https://www.taobao.com/')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input.send_keys('美食')
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        get_products()
        return total.text
    except TimeoutException:
        print('请求超时')
        return search()


def get_page(page):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        submit = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page)
        submit.click()
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active'), str(page)))
        get_products()
    except TimeoutException:
        print('输入超时')
        get_page(page)


def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()  # 调用items方法得到内部所有内容
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            "price": item.find('.price').text(),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        save_to_mongo(product)


def save_to_mongo(result):
    ip = '127.0.0.1'
    port = '27017'
    client = pymongo.MongoClient()
    db = client['taobao']  # 要用[]
    try:
        if db['taobao'].insert_one(result):  # 此处要用insert_one
            print('存储到mongo', result)
    except Exception:
        print('保存失败')


def main():
    total = search()
    pattern = int(re.compile('(\d+)').search(total).group(1))
    for i in range(2, pattern + 1):
        get_page(i)


if __name__ == '__main__':
    main()

