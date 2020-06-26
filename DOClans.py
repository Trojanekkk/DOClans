import requests
from lxml import html
import pandas as pd
import json, codecs
import time

clans = list()

session_requests = requests.session()

login_url = 'https://www.darkorbit.pl/?lang=pl&ref_sid=b9d0df61f0c484f8c0c2b74fc19f9107&ref_pid=22&__utma=-&__utmb=-&__utmc=-&__utmx=-&__utmz=-&__utmv=-&__utmk=38294271'
result = session_requests.get(login_url)

tree = html.fromstring(result.text)
auth_token = list(set(tree.xpath("//input[@name='reloadToken']/@value")))[0]
login_destination = list(set(tree.xpath("//form[@name='bgcdw_login_form']/@action")))[0]

payload = {
    'username': '',
    'password': '',
    'reloadToken': auth_token
}

result = session_requests.post(
    login_destination,
    payload,
    headers = dict(referer=login_url)
)

for i in range(1,10):
    time.sleep(1)
    print('checking id: ' + str(i))
    url = 'https://pl2.darkorbit.com/indexInternal.es?action=internalNewClanDetails&clanId=' + str(i)
    result = session_requests.get(
        url,
        headers = dict(referer=login_url)
    )

    tree = html.fromstring(result.text)
    infoList = list(set(tree.xpath("//li[@class='clan_item']/span[@class='info']/text()")))

    if (len(infoList) == 8):
        clan = {
            'id': i,
            'clanName': infoList[0],
            'clanTag': infoList[1],
            'clanDate': infoList[2],
            'clanOwner': infoList[3],
            'clanCompany': infoList[4],
            'clanRank': infoList[5],
            'clanMembers': infoList[6],
            'clanStatus': infoList[7]
        }
        clans.append(clan)
        print(clan)

with open('data.json', 'wb') as f:
    json.dump(clans, codecs.getwriter('utf-8')(f), ensure_ascii=False)

df =  pd.DataFrame.from_dict(clans)
df.to_csv('clans.csv')
print(clans)