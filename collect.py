#coding:utf8
import HTMLParser
from util import *
from settings import *
import os
import base64
import time
def feed_from_collect(what, who):
    collect_url = 'https://%s.douban.com/people/%s/collect?mode=list' % (what, who)
    class Parser(HTMLParser.HTMLParser):
        def __init__(self):
            HTMLParser.HTMLParser.__init__(self)
            self.subject = {}
            self.should_fetch_name = False
            self.subjects = []
            self.next_url = None
            self.what = ''
        def match(self, string):
            keyword = ['http://%s.douban.com/subject/' % self.what,
                    'https://%s.douban.com/subject/' % self.what,
                    ]
            for kw in keyword:
                if string.find(kw) != -1:
                    return True
            return False

        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                for key, value in attrs:
                    if key == 'href' and self.match(value):
                        self.subject['url'] = value
                        break
            if tag == 'div':
                for key, value in attrs:
                    if key == 'class' and value == 'date':
                        if not self.subject.has_key('date'):
                            self.subject['date'] = None
            if tag == 'link':
                for key, value in attrs:
                    if key == 'rel' and value == 'next':
                        for k, v in attrs:
                            if k == 'href':
                                self.next_url = v
                                print v
                                break
        def handle_endtag(self, tag):
            pass
        def handle_data(self, data):
            if self.subject.has_key('url'):
                try:
                    data = data.decode('gbk')
                except:
                    data = data.decode('utf8')
                if not self.subject.has_key('title'):
                    self.subject['title'] = data
            if self.subject.has_key('date') and self.subject['date'] == None:
                data = data.replace('\n', '').replace(' ', '')
                if not data == '':
                    self.subject['date'] = data
                    self.subjects.append(self.subject)
                    self.subject = {}
    subjects = []
    p = Parser()
    p.what = what
    url = collect_url
    while True:
        tmp = base64.b64encode(url)
        tmp = tmp + '.html'
        tmp = os.path.join(tmp_folder, tmp)
        if os.path.exists(tmp):
            with open(tmp, 'rb') as tmp:
                r = tmp.read()#.replace('&amp;', '-')
        else:
            sleep(interval)
            if what == 'book':
                r = open_url_and_keep_alive(url, proxy)#.replace('&amp;', '-')
            else:
                r = open_url(url, proxy)#.replace('&amp;', '-')

            if r == None:
                text = '''{
"title":"",
"year":"",
"images":{
"small":"",
"large":"",
"medium":""
},
"id":"%s"
}''' % (id)
                print '%s is empty.Fuck the damn censorship!' % (id)
            print '[%s] -> [%s]' % (url, tmp)
            with open(tmp, 'wb') as tmp:
                tmp.write(r)
        p.feed(r)
        subjects += p.subjects
        p.subjects = []
        if p.next_url != None:
            url = p.next_url
            p.next_url = None
        else:
            return subjects


if '__main__' == __name__:
    tmp = 'tmp'
    if not os.path.isdir(tmp):
        os.mkdir(tmp)
    print feed_from_collect('movie', 'zhuhuotui') 
    __import__('shutil').rmtree(tmp)


