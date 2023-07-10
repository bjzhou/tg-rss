import urllib.parse
from xml.etree import ElementTree

import requests as requests
from bs4 import BeautifulSoup

tg_url = "https://api.telegram.org/bot5810042168:AAEEE1kbTHXFNOR9m-pDguToWQJk5vMi_L0/sendMessage?chat_id=105181972&parse_mode=MarkdownV2&text="
news_36kr = "https://36kr.com/feed-newsflash"
thepaper = "https://rsshub.app/thepaper/featured"
cls = "https://rsshub.app/cls/telegraph"
ithome = "https://www.ithome.com/rss/"
v2ex = "https://rsshub.app/v2ex/topics/hot"
mafengwo = "https://rsshub.app/mafengwo/note/latest"
damai = "https://rsshub.app/damai/activity/%E5%85%A8%E9%83%A8/%E5%85%A8%E9%83%A8/%E5%85%A8%E9%83%A8/"


def tg_safe_text(text: str):
    chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars:
        text = text.replace(char, "\\%s" % char)
    return text


def parse_rss(history_file, url):
    history_file.seek(0)
    send_list = list(history_file.read().splitlines())
    try:
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        })
    except:
        return
    if response.status_code != 200:
        return
    text = response.text
    rss = ElementTree.fromstring(text)
    channel = rss[0]
    news = []
    for item in channel:
        title = ""
        link = ""
        description = ""
        pub_date = ""
        if item.tag == "item":
            for item_child in item:
                if item_child.tag == "title":
                    title = tg_safe_text(item_child.text)
                if item_child.tag == "link":
                    link = item_child.text
                if item_child.tag == "description":
                    description = item_child.text
                    soup = BeautifulSoup(description, features="lxml")
                    description = soup.text.strip()
                    if len(description) > 512:
                        description = description[0:512] + "..."
                    description = tg_safe_text(description)
                if item_child.tag == "pubDate":
                    pub_date = item_child.text
            news.insert(0, {
                "title": title,
                "link": link,
                "description": description,
                "pub_date": pub_date,
            })
    for news_item in news:
        if news_item['link'] in send_list:
            continue
        message = """
[%s](%s)

```
%s
```
        """ % (news_item['title'], news_item['link'], news_item['description'])
        try:
            response = requests.get(tg_url + urllib.parse.quote_plus(message.strip()))
            if response.status_code != 200:
                print(response.json())
            else:
                send_list.append(news_item['link'])
                history_file.write(news_item['link'] + "\n")
        except:
            continue


if __name__ == '__main__':
    with open("history.txt", "a+") as file:
        file.seek(0)
        lines = file.readlines()
        if len(lines) > 5000:
            file.truncate(0)
            file.seek(0)
            file.writelines(lines[4000:])
        parse_rss(file, news_36kr)
        parse_rss(file, ithome)
        parse_rss(file, thepaper)
        parse_rss(file, cls)
        parse_rss(file, v2ex)
        parse_rss(file, mafengwo)
        parse_rss(file, damai)
