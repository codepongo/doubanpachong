import os
import time
import json
from settings import *
from util import *

def pull(fmt, folder, what, id):
    path = folder + os.sep + id
    if not os.path.isdir(path):
        os.mkdir(path)

    txt = os.path.join(path, 'subject.txt')
    if not os.path.isfile(txt):
        url = fmt % (id)
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
                            f.write(open_url(r['images'][i].replace('\/', '/')))
    return path

def archive(source, destination):
    info = os.path.join(source, 'subject.txt')
    if not os.path.isfile(info):
        print info
        return
    with open(info, 'rb') as f:
        text = f.read()
    r = json.loads(text)

    if r.has_key('year'):
        prefix = r['year'] + '_'
    elif r.has_key('attrs') and r['attrs'].has_key('singer'):
        prefix = r['attrs']['singer'][0] + '_'
    else:
        prefix = ""
    if r['title'] == "":
        destination = os.path.join(destination, r['id'])
    else:
        name = (prefix + r['title']).replace(':', '-').replace('/', '-').replace('\r', '')
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
            arrange.append(json.loads(f.read())['id'])
    return arrange

