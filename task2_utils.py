from currency_symbols import _constants
import string 
import re
import datefinder

from task1_utils import unique
import spacy  

# currency symbols to filter by
cur_symbs = list(_constants.CURRENCY_SYMBOLS_MAP.values())
cur_keys = list(_constants.CURRENCY_SYMBOLS_MAP.keys())
#load core english library
nlp = spacy.load("en_core_web_sm")

cur_symbs = ''.join(unique([x for x in ''.join(cur_symbs) if (not x.isalpha()) and all([x!=p for p in string.punctuation])]))+'$'

# to check for a certain symbol
def isthere_cur_symb(sent):
    return any([symb in sent for symb in cur_symbs])
def isthere_cur_keys(sent):
    return any([symb in sent for symb in cur_keys])
def isthere_dig(sent):
    return any([dig in sent for dig in '0123456789'])

# to check for a company name
def isthere_name(lst,name):
    ret = [x for x in lst if name.lower() in x.lower()]
    if len(ret)<0 and (len(name.split())>1):
        for nm in name.split():
            filter_by_name(lst,nm)
    return ret     

# regexp to fround amount
def extract_fround_amount(text):
    return [x.strip().lower() for x in re.findall(r"[\$€£]?\s?\d+\s?[\d|\.|,|\s]+[\w\.,]+", text)]
   
# take all text from page
def all_strings(soup):
    ret=[]
    if soup:
        if soup.head:
            ret = ret+list(soup.head.strings)
        if soup.body:
            ret = ret+list(soup.body.strings)
    return ret

# turn text to set of sentences
def list_to_sents(lst):
    try:
        text = ' '.join([x.strip() for x in lst])
        sents = [sent.text.strip() for sent in nlp(text).sents]
        return sents
    except:
        return []    
    
# take all 'time' tags from page
def times(soup):
    ret = []
    for x in soup.find_all('time'):
        try:
            ret.extend([x.text.strip(),x['datetime']])
        except:
            pass
    return ret

def find_dates_from_list(lst):
    ret = []
    for txt in lst:
        try:
            ret = ret +list(datefinder.find_dates(txt))
        except:
            pass
    return ret
    
def first_element(lst):
    try:
        return lst[0]
    except:
        return lst
