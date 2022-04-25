import pandas as pd
import numpy as np

import requests
from bs4 import BeautifulSoup
import re

import json

# to manage lists
def unique(lst):
    return list(set(lst))
def sum_list(lst):
    return sum(lst,[])

#  to save jsons
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)  

# to save info in process of extraction
def append_to_list_of_jsons(_dict, path):
    with open(path, 'ab+') as f:
        f.seek(0, 2)
        f.write('\n'.encode())  # Write the separator
        f.write(json.dumps(_dict,cls=NpEncoder).encode())  # Dump the dictionary

# to open saved info
def open_json_pd(path):
    list_of_row = []
    with open(path) as f:
        for line in f:
            try:
                row = json.loads(line)
                list_of_row.append(row)
                del line, row
            except:
                pass
    df = pd.DataFrame.from_dict(list_of_row)
    return df

# regexps
def extract_emails(text):
    return [x.strip().lower() for x in re.findall(r':?[^@\s]+@[^@\s]+\.[\w]{,6}', text)]

def extract_phone(text,phone_regexps):
    ret = []
    for phe in phone_regexps:
        ret = ret + [x.strip() for x in re.findall (phe, text)]
    ret = unique(ret)
    return ret

# to download a page
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def soup_by_url(url):
    try:
        if not url.startswith('http'):
            try:
                soup_by_url('http://'+url)
            except:
                soup_by_url('https://'+url)
        response = requests.get(url,headers = headers, verify=False)
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        return (soup, response.url)
    except:
        return (None,None)
    
# to decode protected email
def decodeEmail(e):
    de = ""
    k = int(e[:2], 16)
    for i in range(2, len(e)-1, 2):
        de += chr(int(e[i:i+2], 16)^k)

    return de

# to save all links from page
def dict_of_urls(soup,tag):
    ret = {}
    for x in soup.find_all(tag):
        try:
            href = x['href']
            if 'email-protection' in href:
                href = decodeEmail(href.split('#')[-1])
            ret.update({x.text.strip():href})
        except:
            pass
    return ret