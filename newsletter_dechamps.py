from discord_webhook import DiscordWebhook, DiscordEmbed
from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
import time
import os
import sys
from lxml import html

baseURL = 'https://getnada.com/api/v1'

class NewsLetterMessage:

    def __init__(self, title, message, color):
        self.title = title
        self.message = message
        self.color = color
        self.url = os.environ.get('DISCORD_WEBHOOK')
        if ',' in self.url:
            self.url = self.url.split(',')

    def send(self):
        if self.url is list:
            for link in self.url:
                webhook = DiscordWebhook(url=link, username="Filipe Deschamps Newsletter")
                embed = DiscordEmbed(
                    title=self.title,
                    description=f'{self.message[0:1].upper()}{self.message[1:len(self.message)]}',
                    color=self.color
                )
                webhook.add_embed(embed)
                webhook.execute()
        else:
            webhook = DiscordWebhook(url=self.url, username="Filipe Deschamps Newsletter")
            embed = DiscordEmbed(
                title=self.title,
                description=f'{self.message[0:1].upper()}{self.message[1:len(self.message)]}',
                color=self.color
            )
            webhook.add_embed(embed)
            webhook.execute()

def getlastMessage():
    msg = None
    mail = os.environ.get('MAIL_ADDRESS')
    response = requests.get(f'{baseURL}/inboxes/{mail}')
    data = json.loads(response.text)
    for d in data['msgs']:
        if d['fe'] == 'newsletter@filipedeschamps.com.br':
            if 'Today' in d['rf']:
                if "ru" not in d:
                    msg = d
    return msg

def getMessages(id):
    response = requests.get(f'{baseURL}/messages/html/{id}')
    soup = BeautifulSoup(response.text, features="html.parser")
    tree = html.fromstring(soup.__str__())
    result = tree.xpath('//p[text()]')
    titles = []
    notices = []

    for r in result:
        titles.append(r[0].text)
    
    message = {}
    for t in titles:
        result = tree.xpath(f'//strong[text()="{t}"]/../text()')
        message['title'] = str(t)
        message['content'] = str(result[0])
        notices.append(message)
        message = {}

    result = tree.xpath(f'//strong/../a/..')
    for r in result:
        notices.remove(next(item for item in notices if item["title"] == r[0].text))

    print(len(notices))

    if len(notices) > 0:
        dias = ['segunda', 'terça', 'quarta', 'quinta', 'sexta']
        for d in dias:
            if d in notices[0]['title'].lower():
                notices = notices[1::]

    print(notices)

    return notices

n = len(sys.argv)
if n == 0:
    print('Informe o email e Discord WebHook Link')
else:
    os.environ['MAIL_ADDRESS'] = sys.argv[1]
    os.environ['DISCORD_WEBHOOK'] = sys.argv[2]
    lastMessage = getlastMessage()
    if lastMessage is not None:
        for m in getMessages(lastMessage['uid']):
            NewsLetterMessage(m['title'].replace(':', ''), m['content'].replace(': ', ''), '242424').send()
            time.sleep(1)
    else:
        print('Nenhuma noticia encontrada')
