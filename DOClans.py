import requests
from lxml import html
import pandas as pd
import json, codecs
import time

print('Starting script...')

clans = list()

session_requests = requests.session()

login_url = 'https://www.darkorbit.pl/?lang=pl&ref_sid=b9d0df61f0c484f8c0c2b74fc19f9107&ref_pid=22&__utma=-&__utmb=-&__utmc=-&__utmx=-&__utmz=-&__utmv=-&__utmk=38294271'
result = session_requests.get(login_url)

print('Getting login info and tokens...')

tree = html.fromstring(result.text)
auth_token = list(set(tree.xpath("//input[@name='reloadToken']/@value")))[0]
login_destination = list(set(tree.xpath("//form[@name='bgcdw_login_form']/@action")))[0]

payload = {
    'username': '',
    'password': '',
    'reloadToken': auth_token
}
print('logging in...')

result = session_requests.post(
    login_destination,
    payload,
    headers = dict(referer=login_url)
)
print('Logging in DONE\n')

for i in range(1,10):
    time.sleep(1)
    print('checking id: ' + str(i))
    url = 'https://pl2.darkorbit.com/indexInternal.es?action=internalNewClanDetails&clanId=' + str(i)
    result = session_requests.get(
        url,
        headers = dict(referer=login_url)
    )

    tree = html.fromstring(result.text)
    
    clanName = list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Nazwa klanu']/following-sibling::span/text()")))
    if (len(clanName) > 0):
        clanTag = list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Tag klanu']/following-sibling::span/text()")))
        clanDate = list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Data założenia']/following-sibling::span/text()")))
        clanOwner = list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Zarządca']/following-sibling::span/text()")))
        clanMembers = list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Liczba członków']/following-sibling::span/text()")))
        clanRank = list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Ranga klanu']/following-sibling::span/text()")))
        clanCompany = list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Firma']/following-sibling::span/text()")))
        clanStatus = list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Status']/following-sibling::span/text()")))
        
        clan = {
            'id': i,
            'clanName': clanName[0],
            'clanTag': clanTag[0],
            'clanDate': clanDate[0],
            'clanOwner': clanOwner[0],
            'clanCompany': clanCompany[0],
            'clanRank': clanRank[0],
            'clanMembers': clanMembers[0],
            'clanStatus': clanStatus[0]
        }
        clans.append(clan)
        print(clan)

with open('clans.json', 'wb') as f:
    json.dump(clans, codecs.getwriter('utf-8')(f), ensure_ascii=False)

df =  pd.DataFrame.from_dict(clans)
df.to_csv('clans.csv')
print(clans)