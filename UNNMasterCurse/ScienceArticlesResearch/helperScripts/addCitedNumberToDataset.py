import sys
import os
import json
from tqdm import tqdm
import mmap 
import requests
from bs4 import BeautifulSoup
import time
from random import random
assert len(sys.argv) > 1, "dont have path variable to patht to dataset"


cookie = sys.argv[3]
s = requests.Session()
headers = {'upgrade-insecure-requests': '1','accept-encoding': 'gzip, deflate, br','authority': 'scholar.google.com','accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' ,'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36', 'cookie': cookie}
s.headers.update(headers)



def get_num_lines(dataset_path):
    fp = open(dataset_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines

def get_cites_count_by_doi(doi):
    url = f'https://scholar.google.com/scholar?hl=ru&as_sdt=0%2C5&q={doi}'
    respond = s.get(url)
    soup = BeautifulSoup (respond.text, 'html.parser') 
    f = open('last-shapshot.html','w')
    f.write(soup.prettify())
    f.close()
    res = 0
    flag = True
    if len(soup.select('.g-recaptcha')) > 0 or len(soup.select('#gs_captcha_f')) > 0:
        flag = False
    try:
        res = int(soup.select('.gs_fl a')[3].text[12:])
    except Exception as e:
        pass
    # print(f"Цитируется {doi} - {res}")
    return res, flag

dataset_path = sys.argv[1]
dump_file = open('datasets/arxiv-metadata-oai-snapshot-with-cited-count-6.json','w')
data = []
count = 0
with open(dataset_path) as file:
    for line in tqdm(file, total=get_num_lines(dataset_path)):
        elem = json.loads(line.rstrip())
        if (elem['doi'] and elem['id'] > sys.argv[2]):
            cited_number, flag = get_cites_count_by_doi(elem['doi'])
            if flag == False:
                print(f'\nTotal cites count {count}')
                print('Oops, recaptcha\n8 minutes sleep ...')
                time.sleep(8*60)
                while get_cites_count_by_doi(elem['doi'])[1] == False:
                    print('An enother 1 minute sleep ...')
                    time.sleep(1*60)
                cited_number, _ = get_cites_count_by_doi(elem['doi'])
            elem['cited_number'] = cited_number
            dump_file.write(json.dumps(elem, separators=(',', ':')))
            dump_file.write('\n')
            # break
            count += 1
