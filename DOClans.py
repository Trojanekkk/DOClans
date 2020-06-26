import grequests
from lxml import html
import pandas as pd
import json, codecs
import time
from random import randrange
import getpass

def isEmpty (clanAttrArr):
    if (len(clanAttrArr) > 0):
        return clanAttrArr[0]
    return False

clans = list()

print('Starting script...')

session_requests = grequests.Session()

login_url = 'https://www.darkorbit.pl/?lang=pl&ref_sid=b9d0df61f0c484f8c0c2b74fc19f9107&ref_pid=22&__utma=-&__utmb=-&__utmc=-&__utmx=-&__utmz=-&__utmv=-&__utmk=38294271'
result = session_requests.get(login_url)

print('Getting login info and tokens...')

print("Your credentials won't be saved anywhere, it's only required to grab clans info")
username = input("Username: ")
password = getpass.getpass(prompt="Password (password won't display): ")
server = ''
while server != "pl2":
    server = input("Server (default: pl2): ") or "pl2"
concurrent = input("Concurent scrapping (default: 1; experimental): ") or 1
startRange = input("Start checking at: ")
stopRange = input("Stop checking at: ")

tic = time.perf_counter()

tree = html.fromstring(result.text)
auth_token = list(set(tree.xpath("//input[@name='reloadToken']/@value")))[0]
login_destination = list(set(tree.xpath("//form[@name='bgcdw_login_form']/@action")))[0]

payload = {
    'username': username,
    'password': password,
    'reloadToken': auth_token
}
print('logging in...')

result = session_requests.post(
    login_destination,
    payload,
    headers = dict(referer=login_url)
)
print('Logging in DONE\n')


for i in range(int(startRange),int(stopRange) + 1, int(concurrent)):
    toc = time.perf_counter()
    print('at ' + str("{:10.2f}".format(toc - tic)) + 's checking ' + str(concurrent) + ' id(s) starting from: ' + str(i))
    urls = []
    id_list = []
    for j in range(0,int(concurrent)):
        id = i + j
        id_list.append(i + j)
        if id <= int(stopRange):
            urls.append('https://' + str(server) + '.darkorbit.com/indexInternal.es?action=internalNewClanDetails&clanId=' + str(id))

    result = (grequests.get(
        url,
        headers = dict(referer=login_url),
        session=session_requests
    ) for url in urls)
    res = grequests.map(result)
    
    for response in res:
        id = id_list.pop(0)
        tree = html.fromstring(response.text)
            
        clanName = isEmpty(list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Nazwa klanu']/following-sibling::span/text()"))))
        if (clanName):     
            clanTag = isEmpty(list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Tag klanu']/following-sibling::span/text()"))))
            clanDate = isEmpty(list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Data założenia']/following-sibling::span/text()"))))
            clanOwner = isEmpty(list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Zarządca']/following-sibling::span/text()"))))
            clanMembers = isEmpty(list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Liczba członków']/following-sibling::span/text()"))))
            clanRank = isEmpty(list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Ranga klanu']/following-sibling::span/text()"))))
            clanCompany = isEmpty(list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Firma']/following-sibling::span/text()"))))
            clanStatus = isEmpty(list(set(tree.xpath("//li[@class='clan_item']/span[text() = 'Status']/following-sibling::span/text()"))))
                    
            clan = {
                'id': id,
                'clanName': clanName,
                'clanTag': clanTag,
                'clanDate': clanDate,
                'clanOwner': clanOwner,
                'clanCompany': clanCompany,
                'clanRank': clanRank,
                'clanMembers': clanMembers,
                'clanStatus': clanStatus
            }
            clans.append(clan)

            print('found for ' + str(id))

        if (i % 25 == 0):
            with open('clans.json', 'wb') as f:
                json.dump(clans, codecs.getwriter('utf-8')(f), ensure_ascii=False)

            df =  pd.DataFrame.from_dict(clans)
            df.to_csv('clans.csv')

with open('clans.json', 'wb') as f:
    json.dump(clans, codecs.getwriter('utf-8')(f), ensure_ascii=False)

df =  pd.DataFrame.from_dict(clans)
df.to_csv('clans.csv')

toc = time.perf_counter()
print('Script DONE in ' + str("{:7.2f}".format(toc - tic)))
input("Press Enter to continue...")

# print(clans)