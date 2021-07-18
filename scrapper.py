#!/usr/bin/env python
# coding: utf-8

import urllib.request
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np

# Парсим metacritic.com, топ игр по Metascore

GOOD_RESPONSE_STATUS = 200

titles = []
user_scores = []
critic_scores = []
dates = []
platforms = []
game_urls = []

# Metacritic отклоняет все запросы без строки User-agent, поставим дефолтный хромовский User-Agent
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36"}
# Если поставить больше страниц на обработку, то есть шанс напороться на 'too many requests'
for page_num in range(140): # max = 180
    url = f'https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?page={page_num}'
    response = requests.get(url, headers=header)
    while response.status_code != GOOD_RESPONSE_STATUS:
        time.sleep(20)
        print(response.status_code, 'waiting')
        response = requests.get(url, headers=header)
    time.sleep(1)
    if response.status_code == GOOD_RESPONSE_STATUS:
        soup = BeautifulSoup(response.content, 'html.parser')
        title_soup = soup.find_all('a', 'title')
        critic_score_soup = soup.find_all('div', 'clamp-metascore')
        user_score_soup = soup.find_all('div', 'clamp-userscore')
        platform_date_soup = soup.find_all('div', 'clamp-details')
        for elem in title_soup:
            titles.append(elem('h3')[0].text)
            game_urls.append('http://metacritic.com' + elem.get('href'))
        for elem in critic_score_soup:
            critic_scores.append(elem('div')[0].text)
        for elem in user_score_soup:
            user_scores.append(elem('div')[0].text)
        for elem in platform_date_soup:
            platforms.append(elem('span')[1].text.strip(' \n'))
            dates.append(elem('span')[2].text)
    time.sleep(1)

# ставим играм без пользовательской оценки nan, приводим пользовательскую оценку к виду, который можно засунуть в corr()
def to_float(string):
    if (string == 'tbd'):
        return float('nan')
    else:
        return float(string)
user_scores = [to_float(elem) for elem in user_scores]


df = pd.DataFrame(
    {
        'titles': titles,
        'dates': dates,
        'platforms': platforms,
        'critic_scores': critic_scores,
        'user_scores': user_scores,
        'game_urls': game_urls 
    }
)

df.to_csv('out.csv', encoding='utf-8')
