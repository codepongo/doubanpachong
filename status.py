import util
import json
import os
def crawler(u, n):
    url = 'https://m.douban.com/rexxar/api/v2/status/user_timeline/'
    path = n + os.sep + 'status'
    if not os.path.isdir(path):
        os.makedirs(path)
    url += u
    query = ''
    while True:
        print url + query
        status = json.loads(util.open_url(url + query))
        count = len(status["items"]) 
        if count <= 0:
            break
        for item in status['items']:
            item = item["status"]
            jpath = os.path.join(path, item['id'] + '.json')
            if os.path.isfile(jpath):
                break
                #continue
            with open(jpath, 'wb') as f:
                f.write(json.dumps(item))
                idx = 0
            for image in item['images']:
                img_url = image['large']["url"]
                suffix = img_url[img_url.rfind('/')+1:]
                with open(os.path.join(path, item['id'] + '_' + str(idx) + '.' + suffix), 'wb') as f:
                    f.write(util.open_url(img_url))
                idx += 1
        query = '?max_id=' + status["items"][len(status['items'])-1]["status"]["id"]




if __name__ == '__main__':
    user_id = '48512229'
    user = 'zhuhuotui'
    crawler(user_id, user)
    sys.exit(0)
