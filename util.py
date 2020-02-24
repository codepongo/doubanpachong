import urllib
import time
import sys
import requests
import datetime
import base64
import os
import settings

import requests.packages.urllib3 as urllib3
urllib3.disable_warnings()


from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

headers={
"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"
}


# Never check any hostnames
class HostNameIgnoringAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       assert_hostname=False)


# Check a custom hostname
class CustomHostNameCheckingAdapter(HTTPAdapter):
    def cert_verify(self, conn, url, verify, cert):
        #      implement me
        host = custom_function_mapping_url_to_hostname(url)
        conn.assert_hostname = host
        return super(CustomHostNameCheckingAdapter,
                     self).cert_verify(conn, url, verify, cert)

conn = None
def open_url_and_keep_alive(url, proxies=None):
    global conn
    if conn == None:
        conn = requests.session()
        conn.mount('https://', HostNameIgnoringAdapter())
    rep = conn.get(url, proxies=proxies, verify=False, headers=headers)
    if 200 != rep.status_code:
        print rep
        return None
    return rep.content

def open_url(url, proxies=None):
    conn = requests.session()
    conn.mount('https://', HostNameIgnoringAdapter())
    response  = conn.get(url, proxies=proxies, verify=False, headers=headers)
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

def cache_url(url, directory, force=False):
    name = base64.b64encode(url) + '.html'
    path = os.path.join(directory, name)
    if not force and os.path.isfile(path):
        print url, '=', path
    else:
        print url, '->', path
        html = open_url(url, settings.proxy)
        if html == None:
            html = ''
        with open(path, 'wb') as f:
            f.write(html)
    return path
