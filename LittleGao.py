#!/usr/bin/env python
# coding: utf-8


from bs4 import BeautifulSoup;
import time
from selenium import webdriver
import tushare as ts
import datetime

# 1、设置TUSHARE接口TOKEN
ts.set_token('cecf5814ed5b3708c7ba44fa1419fa250c5167bb2b37044cddb02292')  # 设置token，只需设置一次
pro = ts.pro_api()

# 2、自动获取上一交易日期
today = datetime.date.today()
today_str = datetime.datetime.strptime(str(today), '%Y-%m-%d')
today_str = today_str.strftime('%Y-%m-%d')
print(type(today_str))
my_date2 = today - datetime.timedelta(days=1)
while ts.get_tick_data('000001', date=str(my_date2), src='tt') is None:  # get_tick_data为空
    my_date2 = my_date2 - datetime.timedelta(days=1)
my_date2 = str(my_date2)
print(type(my_date2))
# my_date2 = '2020-08-07' #str(my_date2) #上一交易日日期2020-08-07
my_date = my_date2[0:4] + my_date2[5:7] + my_date2[8:10]  # 变换格式后的上一交易日日期
print(my_date)

# 3、条件一：筛选昨日涨停且开板次数大于1或昨日最终封板时间在14.30之后
to_rise_stock = pro.limit_list(trade_date=my_date, limit_type='U',
                               fields='ts_code,name,close,first_time,last_time,open_times,pct_chg')  # 获取昨日涨停的股票
print(to_rise_stock)
time_stamp_1430 = time.mktime(time.strptime(my_date + ' 14:30:00', '%Y%m%d %H:%M:%S'))  # 14.30对应的时间戳，用于比较最终封板时间
# to_rise_stock.to_csv('C:/1.txt')
for i in range(len(to_rise_stock)):
    # if len(to_rise_stock.loc[i,'last_time'].encode('unicode-escape').decode('string_escape')) == 0:  #舍弃无
    # to_rise_stock = to_rise_stock.drop(i)
    # continue
    if to_rise_stock.loc[i, 'pct_chg'] < 6 or to_rise_stock.loc[i, 'pct_chg'] > 11:  # 对涨跌幅进行限制，用以去掉ST股票（异常股票）和新股
        to_rise_stock = to_rise_stock.drop(i)
        continue
    if to_rise_stock.loc[i, 'open_times'] < 1:  # and \
        # time.mktime(time.strptime(my_date+to_rise_stock.loc[i,'last_time'],'%Y%m%d%H:%M:%S')) < time_stamp_1430:  #去掉下午2：30条件
        to_rise_stock = to_rise_stock.drop(i)
print('(1/3) Filtering price limit stock completed.' + '\n'       'Now filtering 0.85-condition-satisfied stock.')
print(to_rise_stock)

print(type(to_rise_stock['ts_code'].iloc[2]))

for num in range(len(to_rise_stock['ts_code'])):
    stock_code = to_rise_stock['ts_code'].iloc[num]
    stock_str = stock_code.split('.')[1] + stock_code.split('.')[0]
    stock_str = stock_str.lower()
    print(stock_str)
    stock_url = 'https://finance.sina.com.cn/realstock/company/' + stock_str + '/nc.shtml'
    driver = webdriver.Chrome()

    driver.get(stock_url)
    page = BeautifulSoup(driver.page_source, 'html5lib')
    more_link = driver.find_elements_by_xpath(
        "//div[@class='block_comment block_comment_gs']/div[@class='title_brown']/a")
    print(more_link[0].get_attribute('href'))
    more_link_text = more_link[0].get_attribute('href')

    driver.get(more_link_text)
    page = BeautifulSoup(driver.page_source, 'html5lib')
    essay_link_pool = driver.find_elements_by_xpath("//div[@class='main']/table/tbody/tr/td[@class = 'tal f14']/a")
    if len(essay_link_pool):
        essay_link_text = essay_link_pool[0].get_attribute('href')
        essay_title = essay_link_pool[0].text
        print(essay_title)

        driver.get(essay_link_text)
        page = BeautifulSoup(driver.page_source, 'html5lib')
        word_pool = driver.find_elements_by_xpath("//div[@class='blk_container']/p")
        essay_text = word_pool[0].text
        essay_date = driver.find_elements_by_xpath("//div[@class='creab']/span")
        essay_date_text = essay_date[3].text
        print(essay_date_text)

        print(int(essay_date_text[3:7]))
        print(int(essay_date_text[8:10]))
        print((int(essay_date_text[3:7]) >= 2020) & (int(essay_date_text[8:10]) >= 7))
        print(essay_text)
        essay_title = essay_date_text + to_rise_stock['name'].iloc[num] + '.txt'
        if (int(essay_date_text[3:7]) >= 2020) & (int(essay_date_text[8:10]) >= 7):
            with open(essay_title, 'w') as f:
                print(int(essay_date_text[3:7]))
                print(int(essay_date_text[8:10]))
                f.write(essay_date_text)
                f.write(essay_text)
print('Success!')


