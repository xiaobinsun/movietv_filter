import logging
from celery import task, shared_task
from django.test import Client

logger = logging.getLogger('movietv')
c = Client()

@task(name='hottest')
def generate_hottest():
    url = '/movietv/statis/hottest/'
    recent = [3, 5, 10, 15, 30]
    rdate = [5, 10, 15, 30, 60, 90, 180, 365]
    for i in recent:
        logger.debug('generate_hottest with days=%s' % i)
        c.get(url, {'days': i})
        for j in rdate:
            logger.debug('generate_hottest with days=%s rdays=%s' % (i, j))
            c.get(url, {'days': i, 'rdays': j})

@task(name='regionbar')
def generate_regionbar():
    url = '/movietv/statis/regionbar/'
    tp = ['剧情', '喜剧', '动作', '爱情', '科幻', '动画', '悬疑',
          '惊悚', '恐怖', '犯罪', '同性', '音乐', '歌舞', '传记',
          '历史', '战争', '西部', '奇幻', '冒险', '灾难', '武侠',
          '情色', '纪录片']
    edate = [5, 10, 15, 30, 60, 90, 120, 180, 200, 250,
             300, 365, 500, 600, 700, 800, 900, 1000]
    # no timerange
    c.get(url)
    for t in tp:
        c.get(url, {'type': t})

    # do not specify start date
    for i in edate:
        c.get(url, {'timerange': ',%s' % i})
        for t in tp:
            c.get(url, {'timerange': ',%s' % i, 'type': t})
