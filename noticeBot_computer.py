import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands, tasks


last_major_title = ""
last_normal_title = ""

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

TOKEN = "" # bot token
CHANNEL_ID = "" # channel id
GUILD_ID = "" # server id
url = 'https://computer.cnu.ac.kr/computer/notice/bachelor.do'


@tasks.loop(minutes=0.1)
async def news_sender(channel):
    global last_major_title, last_normal_title
    new_scraped_news = scrape_news()

    new_major_title = new_scraped_news["major_notice_title"][0].find('a')['title']
    new_normal_title = new_scraped_news["normal_notice_title"][0].find('a')['title']
    if new_major_title != last_major_title:
        last_major_title = new_major_title
        new_major_title = new_major_title[:len(new_major_title)-7]
        print(new_major_title)
        await send_news_major(channel, new_scraped_news, new_major_title)
    else:
        print("Keep waiting for another news ...")

    if new_normal_title != last_normal_title:
        last_normal_title = new_normal_title
        new_normal_title = new_normal_title[:len(new_normal_title)-7]
        await send_news_normal(channel, new_scraped_news, new_normal_title)
    else:
        print("Keep waiting for another news ...")

def scrape_news():
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    tbody_list = soup.findChildren("tbody")
    tbody = tbody_list[0]

    find_major_notice = tbody.find_all('tr', class_='b-top-box')
    major_notice_count = len(find_major_notice)
    major_notice = find_major_notice[0] 
    major_notice_title = major_notice.findAll("div", class_="b-title-box")
    
    first_children = tbody.findChildren()[0]
    for _ in range(major_notice_count): 
        first_children = first_children.find_next_sibling()

    normal_notice = first_children
    normal_notice_title = first_children.findAll("div", class_="b-title-box")
    return {"major_notice": major_notice, "major_notice_title": major_notice_title,"normal_notice": normal_notice,"normal_notice_title": normal_notice_title}

async def send_news_major(channel, news, title):
    link = news["major_notice_title"][0].find('a')['href']
    news_info =f'{"🔔 중요 공지를 알립니다 🔔 "+title}\n\n- [링크] : {url+link} \n\n'
    await channel.send(news_info)

async def send_news_normal(channel, news, title):
    link = news["normal_notice_title"][0].find('a')['href']
    news_info =f'{"🔔 일반 공지를 알립니다 🔔 "+title}\n\n- [링크] : {url+link} \n\n'
    await channel.send(news_info)


class MyClient(discord.Client):
    async def on_ready(self):
        channel = self.get_channel(int(CHANNEL_ID))
        news_sender.start(channel)

client = MyClient(intents=intents)
client.run(TOKEN)



