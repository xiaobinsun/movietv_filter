import logging
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, resolve_url
from django.views.generic import TemplateView
from django.db import connection
from django.db.models import Q, OuterRef, Subquery
from django.core.paginator import Paginator

from .utils import BraceMessage as _
from .models import MovieTv as MT, Score, Tag

logger = logging.getLogger('movietv')

class HomePageView(TemplateView):
    template_name = 'index.html'

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

    qS = qS.values('id', 'title', 'release_date', 'type', 'region',
                   'score__score', 'score__votes')

    logger.debug(str(qS.query))

    paginator = Paginator(qS, int(pagecnt))
    rpage = paginator.get_page(pagenum)

    return render(request, 'filter.html', {'rpage': rpage,
                                'baseurl': 'https://movie.douban.com/subject/',
                                'pagination': pagination_render(rpage)})
