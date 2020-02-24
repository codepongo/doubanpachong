#coding:utf8
import os
import time
import json
from settings import *
from util import *
import HTMLParser

def save_image(path, r):
    if r.has_key('image'):
        img_src = r['image']
        suffix = img_src[:-img_src.rfind('.')]
        poster = os.path.join(path, 'cover' + suffix)
        with open(poster, 'wb') as f:
            f.write(open_url(r['image']))
    elif r.has_key('images'):
        for i in r['images'].keys():
            img_src = r['images'][i]
            suffix = img_src[img_src.rfind('.'):]
            poster = os.path.join(path, i + suffix)
            if os.path.isfile(poster) or img_src == "":
                continue
            with open(poster, 'wb') as f:
                f.write(open_url(img_src.replace('https', 'http')))
    else:
        return

def parse_object_html(html):
    class Parser(HTMLParser.HTMLParser):
        def __init__(self):
            HTMLParser.HTMLParser.__init__(self)
            self.subject = None
            self.should_fetch_name = False
            self.next_url = None

        def handle_starttag(self, tag, attrs):
            if tag == 'script':
                for key, value in attrs:
                    if key == 'type' and value == 'application/ld+json':
                        self.subject = {}
                        break
            if tag == 'span':
                for key, value in attrs:
                    if key == 'property' and value == 'v:summary':
                        self.subject['description'] = None
                        break
        def handle_endtag(self, tag):
            pass
        def handle_data(self, data):
            if self.subject == None:
                return
            if not self.subject.has_key('description'):
                data = data.replace('\n', '')
                self.subject = json.loads(data)
                return
            if self.subject['description'] == None:
                #self.subject['description'] = data.replace('<br />', '\n').encode('utf8')
                return
    p = Parser()
    p.feed(html.decode('utf8', 'ignore').replace('</a href="javascript:;;">', '</a>'))
    return p.subject

def pull_by_html(what, folder, sid):
    whats_by_html = {
            'movie':{'fmt':'https://movie.douban.com/subject/%s/'}, 
            'book':{'fmt':'https://book.douban.com/subject/%s/'}, 
            'music':{'fmt':'https://music.douban.com/subject/7051816/'},
    }
    path = os.path.join(folder, sid)
    if not os.path.isdir(path):
        os.mkdir(path)
    txt = os.path.join(path, 'subject.txt')
    if os.path.isfile(txt):
        return path
    url = whats_by_html[what]['fmt'] % (sid)
    fHtml = cache_url(url, tmp_folder)
    html = None
    with open(fHtml, 'rb') as f:
        html = f.read()
    if html == '' or html  == None:
        print url, ' is 404, Fuck!'
        r = {'name':'',
             'datePublished':'',
             'images':{
                 'large':'',
                 's_ratio_poster':''
                },
            'id':sid
        }
    else:
        r = parse_object_html(html)
        r['id'] = sid
        r['images'] = {'s_ratio_poster':r['image'],
                       'large':r['image'].replace('/s_ratio_poster/', '/large/')
        }
        r.pop('image')
    text = json.dumps(r, indent=4, ensure_ascii=False)
    print txt
    with open(txt, 'wb') as f:
        f.write(text.encode('utf8', 'ignore'))
    save_image(path, r)
    return path


def pull_by_api(fmt, folder, what, id):
    path = folder + os.sep + id
    if not os.path.isdir(path):
        os.mkdir(path)

    txt = os.path.join(path, 'subject.txt')
    if not os.path.isfile(txt):
        url = fmt % (id)
        print url
        text = open_url(url, proxy)
        if text == '':
            print '%s is 404, Fuck!', url
            return
        if text == None:
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
        r = json.loads(text)

        with open(txt, 'wb') as f:
            f.write(text)

        if r.has_key('image'):
            poster = os.path.join(path, 'cover.jpg')
            with open(poster, 'wb') as f:
                f.write(open_url(r['image'].replace('\/', '/')))
        elif r.has_key('images'):
            img = ['small', 'medium','large']
            for i in img:
                poster = os.path.join(path, i + '.jpg')
                if not os.path.isfile(poster):
                    if r['images'][i] != "":
                        with open(poster, 'wb') as f:
                            f.write(open_url(r['images'][i].replace('\/', '/').replace('https', 'http')))
    return path

def get_prefix(r):
    if r.has_key('year'):
        return r['year']
    elif r.has_key('datePublished'):
        return r['datePublished']
    elif r.has_key('attrs') and r['attrs'].has_key('singer'): # music
        return r['attrs']['singer'][0] + '_'
    else:
        prefix = ""

def get_name(r):
    if r.has_key('title'):
        if r['title'] == "":
            return r['id']
        else:
            return r['title']
    elif r.has_key('name'):
        if r['name'] == '':
            return r['id']
        else:
            return r['name']

def archive(source, destination):
    info = os.path.join(source, 'subject.txt')
    if not os.path.isfile(info):
        print info, 'dose not exist'
        return
    with open(info, 'rb') as f:
        text = f.read()
    r = json.loads(text)
    prefix = get_prefix(r)
    name = get_name(r)
    name = name.replace(':', '-').replace('/', '-').replace('\r', '').replace('*', 'x')
    name = prefix + '_' + name
    destination = os.path.join(destination, name)

    if not os.path.isdir(destination):
        try:
            os.rename(source, destination)
        except:
            print destination
            raise

def append_date(path, dates):
    for name in os.listdir(path):
        p = os.path.join(path, name)
        if not os.path.isdir(p):
            continue
        dt = os.path.join(p, 'date.txt')
        if os.path.isfile(dt):
            continue
        content = os.path.join(p, 'subject.txt')
        if not os.path.isfile(content):
            continue
        with open(content, 'rb') as f:
            id = json.loads(f.read())['id']
        with open(dt, 'wb') as f:
            f.write(dates[id])
        print dates[id], 'in', p

def exist(path):
    arrange =[]
    for name in os.listdir(path):
        p = os.path.join(path, name)
        if not os.path.isdir(p):
            continue
        content = os.path.join(p, 'subject.txt')
        if not os.path.isfile(content):
            try:
                i = int(name)
            except:
                continue
            arrange.append(name)
            continue
        with open(content, 'rb') as f:
            text = f.read()
            try:
                arrange.append(json.loads(text)['id'])
            except:
                arrange.append(text)

    return arrange


if __name__ == '__main__':

    if len(sys.argv) > 1:
        identy = sys.argv[1]
    else:
        print 'subject id is need!'
        sys.exit(0)

    # because the Douban deprecated the APIs,
    # we have to parse the html page.
    # I wish someday the Douban can remeber it's beggining mind.
    #if len(sys.argv) > 2:
    #    what = sys.argv[2]
    #else:
    #    what = 'movie'
    #whats_by_api = {
    #        'book':{'fmt':'https://api.douban.com/v2/book/%s'}, 
    #        'music':{'fmt':'https://api.douban.com/v2/music/%s'}, 
    #        'movie':{'fmt':'https://api.douban.com/v2/movie/subject/%s'},
    #}
    #pull_by_api(whats_by_api[what]['fmt'], '.', what, identy)
    if len(sys.argv) > 2 and sys.argv[2] in {'book', 'music', 'movie'}:
        what = sys.argv[2]
    else:
        what = 'movie'
    path = pull_by_html(what, '.', identy)
    archive(identy, '.')
