import urllib
import time
import sys
import requests
import datetime

conn = None
def open_url_and_keep_alive(url, proxies=None):
    global conn
    if conn == None:
        conn = requests.session()
    rep = conn.get(url, proxies=proxies)
    if 200 != rep.status_code:
        print rep
        return None
    return rep.content

def open_url(url, proxies=None):
    response  = requests.get(url, proxies=proxies)
    if 200 != response.status_code:
        print response.status_code
        return None
    return response.content

def sleep(interval):
    i = 0
    while i < interval:
        time.sleep(1)
        sys.stdout.write('\b' * len(str(i)))
        sys.stdout.write('%d' % i)
        sys.stdout.flush()
        i += 1
    sys.stdout.write('\b' * len(str(i)))

def s_to_date(s):
    t = s.split('-')
    for i in range(len(t)):
        t[i] = int(t[i])
    return datetime.datetime(*t)
