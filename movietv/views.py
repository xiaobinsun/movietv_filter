import logging
from datetime import datetime, timedelta
from io import BytesIO

import math
import pandas as pd
import matplotlib.font_manager as mfm
import matplotlib.pyplot as plt
import matplotlib.colors as pltc
from random import sample

from django.shortcuts import render, redirect, resolve_url
from django.views.generic import TemplateView
from django.db import connection
from django.db.models import F, Q, OuterRef, Subquery
from django.core.paginator import Paginator
from django.contrib.staticfiles.finders import find as find_static_file
from django.http import FileResponse
from django.conf import settings

from .utils import BraceMessage as _, hash6, flatten2D
from .models import MovieTv as MT, Participant as Par, Score, Tag

logger = logging.getLogger('movietv')

all_colors = [k for k, v in pltc.cnames.items()]

class HomePageView(TemplateView):
    template_name = 'index.html'

class StatisPageView(TemplateView):
    template_name = 'statis.html'

def pagination_render(page):
    ptor = page.paginator
    afmt = '<button type="button" id="{}"> {} </button>'
    rstr = ''
    if ptor.count == 0:
        return rstr

    if page.has_previous():
        rstr += afmt.format(page.previous_page_number(), '上一页')
    else:
        rstr += afmt.format('#', '上一页')

    prevdot = lastdot = False

    if page.number >= 7:
        prevdot = True

    if page.number + 5 < ptor.num_pages:
        lastdot = True

    if prevdot:
        rstr += afmt.format(1, 1)
        rstr += afmt.format(2, 2)
        rstr += afmt.format('#', '...')
        rstr += afmt.format(page.number - 2, page.number - 2)
        rstr += afmt.format(page.number - 1, page.number - 1)
        rstr += afmt.format(page.number, page.number)
    else:
        for i in range(1, page.number + 1):
            rstr += afmt.format(i, i)

    if lastdot:
        rstr += afmt.format(page.number + 1, page.number + 1)
        rstr += afmt.format(page.number + 2, page.number + 2)
        rstr += afmt.format('#', '...')
        rstr += afmt.format(ptor.num_pages - 1, ptor.num_pages - 1)
        rstr += afmt.format(ptor.num_pages, ptor.num_pages)
    else:
        for i in range(page.number + 1, ptor.num_pages + 1):
            rstr += afmt.format(i, i)

    if page.has_next():
        rstr += afmt.format(page.next_page_number(), '下一页')
    else:
        rstr += afmt.format('#', '下一页')

    return rstr

def filter(request):
    form = request.GET.get('form', None)
    tp = request.GET.get('type', None)
    region = request.GET.get('region', None)
    scorerange = request.GET.get('scorerange', None)
    votesrange = request.GET.get('votesrange', None)
    timerange = request.GET.get('timerange', None)
    orderby = request.GET.get('orderby', 'S')
    pagenum = request.GET.get('page', 1)
    pagecnt = request.GET.get('pagecnt', 30)

    logdict = {}
    msg = 'Request: '
    if form is not None:
        msg += 'form({form}) '
        logdict['form'] = form
    if tp is not None:
        msg += 'type({type}) '
        logdict['type'] = tp
    if region is not None:
        msg += 'region({region}) '
        logdict['region'] = region
    if scorerange is not None:
        msg += 'scorerange({scorerange}) '
        logdict['scorerange'] = scorerange
    if votesrange is not None:
        msg += 'votesrange({votesrange}) '
        logdict['votesrange'] = votesrange
    if timerange is not None:
        msg += 'timerange({timerange}) '
        logdict['timerange'] = timerange
    if orderby is not None:
        msg += 'orderby({orderby}) '
        logdict['orderby'] = orderby
    if pagenum is not None:
        msg += 'page({page}) '
        logdict['page'] = pagenum
    if pagecnt is not None:
        msg += 'pagecnt({pagecnt}) '
        logdict['pagecnt'] = pagecnt
    logger.debug(_(msg, **logdict))

    ss = se = vs = ve = ts = te = None
    if scorerange is not None:
        ss = scorerange.split(',')[0]
        se = scorerange.split(',')[1]
        ss = None if len(ss) == 0 else ss
        se = None if len(se) == 0 else se

    if votesrange is not None:
        vs = votesrange.split(',')[0]
        ve = votesrange.split(',')[1]
        vs = None if len(vs) == 0 else vs
        ve = None if len(ve) == 0 else ve

    if timerange is not None:
        ts = timerange.split(',')[0]
        te = timerange.split(',')[1]
        ts = None if len(ts) == 0 else ts
        te = None if len(te) == 0 else te

    query = Q()

    formdict = {'电影': 'movie', '电视剧': 'tv'}
    if form is not None:
        query &= Q(type__exact=formdict[form])

    tpq = Q()
    if tp is not None:
        for t in tp.split(','):
            tpq |= Q(tag__tag__contains=t)
    query &= tpq

    if region is not None:
        query &= Q(region__contains=region)

    if timerange is not None:
        if ts is not None:
            edate = datetime.today() - timedelta(days=int(ts))
            query &= Q(release_date__lte=edate)
        if te is not None:
            sdate = datetime.today() - timedelta(days=int(te))
            query &= Q(release_date__gte=sdate)

    if scorerange is not None \
        or votesrange is not None:
        lS = Score.objects.filter(id__exact=OuterRef('id')).order_by('-score_date')
        query &= Q(score__score_date=Subquery(lS.values('score_date')[:1]))

    if scorerange is not None:
        if ss is not None:
            query &= Q(score__score__gte=ss)
        if se is not None:
            query &= Q(score__score__lte=se)

    if votesrange is not None:
        if vs is not None:
            query &= Q(score__votes__gte=vs)
        if ve is not None:
            query &= Q(score__votes__lte=ve)

    qS = MT.objects.filter(query)

    orderDict = {'S': '-score__score',
                 's': 'score__score',
                 'V': '-score__votes',
                 'v': 'score__votes',
                 'D': '-release_date',
                 'd': 'release_date',
    }
    if orderby is not None:
        qS = qS.order_by(orderDict[orderby])

    qS = qS.distinct().values('id', 'title', 'release_date', 'type', 'region',
                   'score__score', 'score__votes')

    logger.debug(str(qS.query))

    paginator = Paginator(qS, int(pagecnt))
    rpage = paginator.get_page(pagenum)

    return render(request, 'filter.html', {'rpage': rpage,
                                'baseurl': 'https://movie.douban.com/subject/',
                                'pagination': pagination_render(rpage)})

def calvdiff(x, days):
    sdate = datetime.today() - timedelta(days=int(days))
    x = x.sort_values('score_date')
    idx = x['score_date'].searchsorted(sdate)

    if len(x) - idx - 1 > 1:
        idx += 1
    elif idx == len(x) - 1:
        idx -= 1

    date_diff = x.iloc[-1].score_date - x.iloc[idx].score_date
    votes_diff = int(x.iloc[-1].votes - x.iloc[idx].votes)
    vavg = math.ceil(votes_diff / date_diff.days)

    return pd.Series({'title': x.iloc[-1].id__title,
                      'release_date': x.iloc[-1].id__release_date,
                      'score': x.iloc[-1].score,
                      'votes': x.iloc[-1].votes,
                      'vavg': vavg})


def celebrity(request):
    names = request.GET.get('names')

    params = []
    logdict = {}
    msg = 'Statistic[celebrity]: '
    if names is not None:
        params.append(names.strip())
        msg += 'names({names}) '
        logdict['names'] = names

    logger.debug(_(msg, **logdict))

    today = datetime.today()
    fil = 'images/' + today.strftime('%Y-%m-%d') + '-celebrity-' + \
                hash6(params) + '.svg'
    if find_static_file(fil) is not None:
        return render(request, 'img.html', {'imgpath': fil})

    query = Q()
    for s in names.split(','):
        s = s.strip()
        sq = Q()
        for n in s.split(' '):
            sq &= Q(celebrity_id__name__contains=n)

        query |= sq

    lS = Score.objects.filter(id__exact=OuterRef('subject_id')).order_by('-score_date')
    query &= Q(subject_id__score__score_date=Subquery(lS.values('score_date')[:1]))
    query &= Q(subject_id__release_date__year__gt=1000)

    qS = Par.objects.filter(query).annotate(cid=F('celebrity_id'),
                                        sid=F('subject_id'),
                                        name=F('celebrity_id__name'),
                                        title=F('subject_id__title'),
                                        rdate=F('subject_id__release_date'),
                                        score=F('subject_id__score__score'),
                                        ).values('cid', 'name', 'sid', 'title',
                                                'rdate', 'score', 'role')

    logger.debug(str(qS.query))

    df = pd.DataFrame(qS)

    gps = df.groupby(['cid', 'role'])

    nplot = len(gps)
    if nplot > 8:
        nplot = 8

    nrows = math.ceil(nplot / 2)
    ncols = 2 if nrows > 1 else nplot

    plt.style.use('ggplot')

    fig, axs = plt.subplots(nrows, ncols, squeeze=False)
    fig.set_size_inches(12, 16)

    fontpath = '/usr/share/fonts/source-han-serif/SourceHanSerifSC-Regular.otf'
    font = mfm.FontProperties(fname=fontpath)

    roleDict = {'director': '导演', 'actor': '演员', 'scriptwriter': '编剧'}
    gen = flatten2D(axs)
    try:
        for crtuple, group in gps:
            ax = next(gen)
            group = group.sort_values('rdate')
            group['avgscore'] = df['score'].expanding().mean()
            logger.debug(df.loc[:, ['name', 'role', 'rdate', 'score', 'avgscore']])
            ax.plot(group['rdate'], group['avgscore'], marker='.')
            txt = group.iloc[0]['name'] + '(' + roleDict[group.iloc[0]['role']] + ')'
            ax.text(0.05, 0.9, txt, transform=ax.transAxes,
                        fontproperties=font)
    except StopIteration:
        pass

    absfil = settings.STATICFILES_DIRS[0] + fil
    fig.savefig(absfil)

    return render(request, 'img.html', {'imgpath': fil})


def hottest(request):
    days = request.GET.get('days', 3)
    rdays =request.GET.get('rdays', None)
    counts = request.GET.get('counts', 30)

    params = []
    logdict = {}
    msg = 'Statistic[hottest]: '
    if days is not None:
        params.append('days='+days)
        msg += 'days({days}) '
        logdict['days'] = days
    if rdays is not None:
        params.append('rdays='+rdays)
        msg += 'rdays({rdays}) '
        logdict['rdays'] = rdays
    if counts is not None:
        params.append('counts='+str(counts))
        msg += 'counts({counts}) '
        logdict['counts'] = counts

    logger.debug(_(msg, **logdict))

    today = datetime.today()
    fil = 'images/' + today.strftime('%Y-%m-%d') + '-hottest-' + hash6(params) + '.svg'
    if find_static_file(fil) is not None:
        return render(request, 'img.html', {'imgpath': fil})
        #return FileResponse(open(absfil, 'rb'))

    sdate = today - timedelta(days=700)
    query = Q(id__release_date__gte=sdate)
    if rdays is not None:
        edate = today - timedelta(days=int(rdays))
        query &= Q(id__release_date__lte=edate)

    qS = Score.objects.filter(query).values('id', 'score_date', 'score', 'votes',
                                            'id__title', 'id__release_date')

    logger.debug(str(qS.query))

    df = pd.DataFrame(qS)
    df['score_date'] = pd.to_datetime(df['score_date'])
    df['id__release_date'] = pd.to_datetime(df['id__release_date'])

    sdate = datetime.today() - timedelta(days=int(days))
    df = df.groupby(by='id', sort=False).filter(lambda x:
                                x['score_date'].max() >= sdate
                                           and len(x) > 1)
    df = df.groupby(by='id', sort=False).apply(calvdiff, days=days)
    df = df.sort_values('vavg', ascending=False)
    df = df[:counts]

    # plot
    plt.style.use('ggplot')

    fig, ax = plt.subplots()
    fig.set_size_inches(9, 6)
    fig.patch.set_visible(False)

    color = sample(all_colors, counts)
    df['vavg'].plot.barh(ax=ax, color=color)
    #ax.get_yaxis().set_visible(False)
    ax.set_yticklabels([i for i in range(1, counts + 1)])
    ax.invert_yaxis()
    #ax.patch.set_visible(False)
    ax.legend().set_visible(False)

    fontpath = '/usr/share/fonts/source-han-serif/SourceHanSerifSC-Regular.otf'
    font = mfm.FontProperties(fname=fontpath)
    for idx in range(counts):
        ax.annotate('{}({})'.format(df.iloc[idx].title, df.iloc[idx].score),
                    (df.iloc[idx].vavg + 30, idx),
                    url='https://movie.douban.com/subject/'+str(df.index[idx])+'/',
                    fontproperties=font, va='center')
        '''
        ax.text(df.iloc[idx].vavg + 30, idx,
                '{}({})'.format(df.iloc[idx].title, df.iloc[idx].score),
                url='https://movie.douban.com/subject/' + str(df.index[idx]) + '/',
                fontproperties=font,
                va='center')
        '''

    absfil = settings.STATICFILES_DIRS[0] + fil
    fig.savefig(absfil)

    return render(request, 'img.html', {'imgpath': fil})
    #return FileResponse(open(absfil, 'rb'))
