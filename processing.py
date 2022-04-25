from bs4 import Tag
from urllib.parse import urlparse

from task1_utils import *

# some marks to filtering out contact pages, legal pages and about us pages
legals_marks = ['privacy', 'cookie', 'policies','policy','terms','terminos','disclaimer','conditions','legal','datenschutz','politica','of-service','of-use']
contacts_marks = ['contact','kontakt','impressum','contatt','imprint']
about_us_marks = ['about','mission','we are','we-are','we-do','team','company','werte']

# regexs for phone numbers
# if we are looking for in plain text
phone_regexp1 = r'\+\s?[0-9\s\-\(\)]{6,}'
phone_regexp2 = r'[\d]\s?\(\d{,3}\)[0-9\s\-]{6,}'
obvious_phone_regexps = [phone_regexp1,phone_regexp2]
# if we are looking for in hrefs
just_more_that_6_digits = [r'[\s|:|\+]+[0-9\s\-\(\)]{6,}']

class Company():
    def __init__(self,url,name,client_id):
        self.name = name
        self.main_url = url
        self.client_id = client_id
        self.soups = []
        self.urls = {url:url}
        self.phones = []
        self.emails = []
        self.desc = ''
        self.legals = []
        self.contacts =[]
        self.about_us = []
        self.all_text = ''
        self.all_urls_text = ''

# checking if url belongs to company's host
# filter from linkedin and instagram pages
    def url_belongs_to_host(self,url):
        netloc = urlparse(url).netloc
        if self.main_url:
            if netloc=='':
                return False
            else:
                if netloc in self.main_url:
                    return True
        return False
        
# download all pages from list of urls
    def update_soups(self):        
        for k,url in self.urls.items():
            sp,resp_url = soup_by_url(url)
            if (resp_url!=url) and (url==self.main_url):
                self.main_url = resp_url
            if sp:
                self.soups.append(sp)

# looking for url in all downloaded pages
    def update_urls(self):
        for soup in self.soups:
            dou = dict_of_urls(soup,'a')
            self.urls.update(dou)
            if soup.body:                
                dou = dict_of_urls(soup.body,'a')
                self.urls.update(dou)
        self.all_urls_text = ' '.join([k+' '+v for k,v in self.urls.items()])

# filter from linkedin and instagram urls, completing url with main page host
    def validate_urls(self):
        for k,v in self.urls.copy().items():
            if v.startswith('/'):
                self.urls[k] = self.main_url+v
            else:
                if not self.url_belongs_to_host(v):
                    del self.urls[k]                    
                    
# extract all texts from all downloaded pages
    def update_texts(self):
        chs = []
        for sp in self.soups:
            if sp and sp.body:
                for ch in sp.body.children:
                    if isinstance(ch, Tag):
                        chs.append(ch.text) 
        lst_all_texts = unique(chs)
        self.all_texts = ' '.join(lst_all_texts)
        
# apply emails regexp
    def update_emails(self):
        self.emails = extract_emails(self.all_texts)
        self.emails.extend(extract_emails(self.all_urls_text))
        
# apply phones regexp, separately to plain text and text from links
    def update_phones(self):
        self.phones = extract_phone(self.all_texts,obvious_phone_regexps)
        self.phones.extend(extract_phone(self.all_urls_text,just_more_that_6_digits))  
        
# cleaning from main page url
    def no_main_url(self,txt):        
        return txt.replace(self.main_url,'').lower()
    
# appy filter by marks to urls, all link's text and describing text
    def find_legals(self):
        for k,v in self.urls.items():
            if any([mrk in self.no_main_url(k) for mrk in legals_marks]) | any([mrk in self.no_main_url(v) for mrk in legals_marks]):
                self.legals.append(v)    

    def find_contacts(self):
        for k,v in self.urls.items():
            if any([mrk in self.no_main_url(k) for mrk in contacts_marks]) | any([mrk in self.no_main_url(v) for mrk in contacts_marks]):
                self.contacts.append(v)                

    def find_about(self):
        for k,v in self.urls.items():
            if any([mrk in self.no_main_url(k) for mrk in about_us_marks]) | any([mrk in self.no_main_url(v) for mrk in about_us_marks]):
                self.about_us.append(v)                

# looking for description on main page and all about us pages
    def find_desc(self):
        self.desc= self.desc+ self.big_chunk_of_text(self.main_url)
        if len(self.about_us)>0:            
            for url in self.about_us:
                self.desc=self.desc+ self.big_chunk_of_text(url)

# take first big chunks of text including company name or some marks like 'mission' or  'vision'
    def big_chunk_of_text(self,url):
        sp,_ = soup_by_url(url)
        props = []
        if sp:
            props = unique([div.text.strip() for div in sp.find_all('span') if len(div.text.split(' '))>7])        
            props = unique(props + [div.text.strip() for div in sp.find_all('p') if len(div.text.split(' '))>7])
            if len(props)>2:
                props = [x for x in props if 
                         any([nm in x.lower() for nm in self.name.lower().split(' ' )]) or 
                         any([mrk in x.lower() for mrk in ['mission','vision']])]
            props = props[:2]
        return ' '.join(props)
                
                
                
    def pipeline(self):
# take first 3 levels of site's pages
        for i in range(3):
            self.update_soups()
            self.update_urls()
            self.validate_urls()        
# take all text
        self.update_texts()
# extact contact imfo
        self.update_emails()
        self.update_phones()    
# filter some pages from list of all urls
        self.find_legals()
        self.find_contacts()
        self.find_about()
# filter desc from all text
        self.find_desc()
