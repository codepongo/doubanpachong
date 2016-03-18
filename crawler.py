import shutil
import os
import collect
import subject
import settings
import util

def crawler(who, what, fmt):
    if not os.path.isdir(settings.tmp_folder):
        os.mkdir(settings.tmp_folder)
    path = who + os.sep + what
    if not os.path.isdir(path):
        os.makedirs(path)
    exists = subject.exist(path)

    subjects = collect.feed_from_collect(what, who)

    ids = []
    dates = {}
    for s in subjects:
        url = s['url'][:-1]
        id = url[url.rfind('/')+1:]
        ids.append(id)
        dates[id] = s['date']

    for id in ids:
        if not id in exists:
            util.sleep(settings.interval)
            src = subject.pull(fmt, settings.tmp_folder, what, id)
            subject.archive(src, os.path.join(who, what))
            print '[%s] -> [%s]' % (src, os.path.join(who, what))


    subject.append_date(path, dates)


    
if __name__ == '__main__':
    util.open_url_and_keep_alive('http://www.douban.com/', settings.proxy)
    users = ['zhuhuotui']
    whats = {
            'book':{'fmt':'http://api.douban.com/v2/book/%s'}, 
            'music':{'fmt':'http://api.douban.com/v2/music/%s'}, 
            'movie':{'fmt':'http://api.douban.com/v2/movie/subject/%s'},
            }
    for u in users:
        for k, v in whats.items():
            crawler(u, k, v['fmt'])
    shutil.rmtree(settings.tmp_folder)

