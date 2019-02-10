# encoding: utf-8
import urllib2
import datetime
import time
import urlparse
from bs4 import BeautifulSoup
import re
import csv


# seed_url = "https://coinmarketcap.com/assets/views/all/"
seed_url = 'https://coinmarketcap.com/all/views/all/'
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/525.13 '
market_cap_pat = '\\n\D+(.*?)\\n'
market_cap_pat = re.compile(market_cap_pat)

circulating_supply_pat = '\\n+(.*?)$'
circulating_supply_pat = re.compile(circulating_supply_pat)

full_list = []
# top_30 = []


class Throttle:
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)
        if last_accessed is not None and self.delay > 0:
            sleep_time = self.delay - (datetime.datetime.now() - last_accessed).seconds
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.domains[domain] = datetime.datetime.now()


def download(url, user_agent=None, proxy=None, num_retry=2):
    print("Downloading.....:", url)
    '''        
    # header 的另一种写法
    postdata = {"Accept": "*/*",       
                "User-Agent": user_agent,
                "Referer": "http://seputu.com/",
                "Host": "nsclick.baidu.com",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                "X-Requested-With": "XMLHttpRequest",
                "origin": "http://seputu.com"}
    for key, value in postdata.items():
        item = (key, value)
        headall.append(item)
    opener.addhandler = headall
    '''
    headers = {"User-Agent": user_agent}
    if user_agent is None:
        request = urllib2.Request(url)
    else:
        request = urllib2.Request(url, headers=headers)
    opener = urllib2.build_opener()
    # opener.addheaders = headall
    if proxy is not None:
        proxy_para = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_para))
    try:
        throttle = Throttle(delay=10)
        throttle.wait(url=url)
        html = opener.open(request).read()
    except urllib2.URLError as e:
        print("Download error: ", e.reason)
        html = None
        if num_retry > 0:
            if hasattr(e, "code") and 500 <= e.code <= 600:
                html = download(url, user_agent, proxy, num_retry-1)
    opener.close()
    return html

with open('data//top30.csv', 'wb') as fp:
    csv_writer = csv.writer(fp)
    csv_writer.writerow(('Name', 'Platform', 'Market Cap', 'Price', 'Circulating Supply', 'Volume', '1h', '24h', '7d'))

with open('data//full_list.csv', 'wb') as fp:
    csv_writer = csv.writer(fp)
    csv_writer.writerow(('Name', 'Platform', 'Market Cap', 'Price', 'Circulating Supply', 'Volume', '1h', '24h', '7d'))

while True:
    html = download(url=seed_url, user_agent=user_agent)
    if html is None:
        print('page_source download error')
        continue
    else:
        print('successfully download page_source')
        soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
        # print(soup)
        table = soup.find_all('table', attrs={'id': 'currencies-all'})[0]
        original_data = table.find('tbody')
        data_set = original_data.find_all('tr')
        for data in data_set:
            name = data.find('td', attrs={'class': 'no-wrap currency-name'}).find('a').text.encode('utf-8')
            platform = data.find('td', attrs={'class': 'text-left'}).text.encode('utf-8')
            # platform = data.find('td', attrs={'class': 'no-wrap platform-name'}).find('a').text.encode('utf-8')
            market_cap = data.find('td', attrs={'class': 'no-wrap market-cap text-right'}).text.encode('utf-8')        
            market_cap = re.findall(market_cap_pat, market_cap)[0]
            price = data.find('a', attrs={'class': 'price'}).text.encode('utf-8')
            circulating_supply = data.find_all('td', attrs={'class': 'no-wrap text-right circulating-supply'})[0].find('a')
            if circulating_supply is None:
                circulating_supply = data.find_all('td', attrs={'class': 'no-wrap text-right circulating-supply'})[0].find('span')
            circulating_supply = circulating_supply.text.encode('utf-8')
            # circulating_supply = re.findall(circulating_supply_pat, circulating_supply)[0]
            if circulating_supply.startswith('\n'):
                circulating_supply = re.findall(circulating_supply_pat, circulating_supply)[0]
            volume_24h = data.find('a', attrs={'class': 'volume'}).text.encode('utf-8')

            V_1h = data.find('td', attrs={'class': 'no-wrap percent-change negative_change text-right'})
            if V_1h is None:
                V_1h = data.find('td', attrs={'class': 'no-wrap percent-change positive_change text-right'})
                if V_1h is None:
                    V_1h = '?'
                else:
                    V_1h = V_1h.text.encode('utf-8')
            else:
                V_1h = V_1h.text.encode('utf-8')

            V_24h = data.find('td', attrs={'class': 'no-wrap percent-change positive_change text-right'})
            if V_24h is None:
                V_24h = data.find('td', attrs={'class': 'no-wrap percent-change negative_change text-right'})
                if V_24h is None:
                    V_24h = '?'
                else:
                    V_24h = V_24h.text.encode('utf-8')
            else:
                V_24h = V_24h.text.encode('utf-8')

            V_7d = data.find('td', attrs={'class': 'no-wrap percent-change positive_change text-right'})
            if V_7d is None:
                V_7d = data.find('td', attrs={'class': 'no-wrap percent-change negative_change text-right'})
                if V_7d is None:
                    V_7d = '?'
                else:
                    V_7d = V_7d.text.encode('utf-8')
            else:
                V_7d = V_7d.text.encode('utf-8')
            # V_7d = V_7d.text.encode('utf-8')
            # print(tr)
            data_collect = (name, platform, market_cap, price, circulating_supply, volume_24h, V_1h, V_24h, V_7d)
            print(data_collect)
            full_list.append(data_collect)

            '''
            if len(top_30) == 30:
                with open('top30.csv', 'ab') as fp:
                    # excel
                    csv_writer = csv.writer(fp)
                    csv_writer.writerows(top_30)
                del top_30[0:len(top_30)]
                        # print(circulating_supply)
            '''

        with open('data//full_list.csv', 'ab') as fp:
            csv_writer = csv.writer(fp)
            csv_writer.writerows(full_list)

        time.sleep(20)
        
        #查询的币种数量
        top_30 = full_list[0:30]
        with open('data//top30.csv', 'ab') as fp:
            csv_writer = csv.writer(fp)
            csv_writer.writerows(top_30)

        del full_list[0:len(full_list)]

    break

