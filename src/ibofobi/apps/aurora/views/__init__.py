# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core.extensions import render_to_response
from django.core.extensions import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.httpwrappers import HttpResponseRedirect

from django.models.aurora import torrents
from django.models.aurora import metainfos
from django.models.aurora import fetchers
from django.models.aurora import messages

import traceback
import base64
import urllib
import os

from ibofobi.apps.aurora.utils import bittorrent
from ibofobi.apps.aurora.utils.daemonize import daemonize

from BitTorrent.bencode import bdecode
from BitTorrent.ConvertedMetainfo import ConvertedMetainfo

AURORA_FETCHER_COMMAND = '/home/sune/bin/shell/aurora-fetcher'

def index(request):
    return render_to_response('aurora/index', {
            'torrents': torrents.get_list(),
            'fetchers': fetchers.get_list(),
            'aurora_messages': messages.get_list(order_by=['-logged'], limit=7),
        })
index = staff_member_required(index)

def torrent(request, t_id):
    torrent = get_object_or_404(torrents, pk=t_id)
    try:
        fetcher = fetchers.get_object(pk=torrent.id)
    except fetchers.FetcherDoesNotExist:
        fetcher = None
    msgs = messages.get_list(order_by=['-logged'], limit=30, torrent__id__exact=torrent.id)
    return render_to_response('aurora/torrent', {
            'torrent': torrent,
            'fetcher': fetcher,
            'aurora_messages': msgs,
        })
torrent = staff_member_required(torrent)

def pause(request, t_id):
    torrent = get_object_or_404(torrents, pk=t_id)
    torrent.status = 'st'
    torrent.save()

    try:
        fetcher = fetchers.get_object(pk=torrent.id)
        fetcher.kill_process()
    except fetchers.FetcherDoesNotExist:
        pass

    return HttpResponseRedirect('..')
pause = staff_member_required(pause)

def resume(request, t_id):
    torrent = get_object_or_404(torrents, pk=t_id)
    torrent.status = 'wk'
    torrent.save()
    return HttpResponseRedirect('..')
resume = staff_member_required(resume)

def add(request):
    if request.POST:
        errors = {}

        url = request.POST['url']
        if url:
            try:
                f = urllib.urlopen(url)
                content = f.read()
                f.close()

                metainfo = ConvertedMetainfo(bdecode(content))
                name = metainfo.name_fs[:50]
    
            except Exception, e:
                err = traceback.format_exception_only(e.__class__, e)
                errors.setdefault('url', []).append(''.join(err))
                
        else:
            try:
                torrent = request.FILES['torrent']
                content = torrent['content']
                metainfo = ConvertedMetainfo(bdecode(content))
                name = metainfo.name_fs[:50]

            except Exception, e:
                err = traceback.format_exception_only(e.__class__, e)
                errors.setdefault('torrent', []).append(''.join(err))

        if errors:
            return render_to_response('aurora/add', locals())

        else:
            t = torrents.Torrent(name=name)
            t.save()
            m = metainfos.Metainfo(torrent=t, metainfo=base64.encodestring(content))
            m.save()

            if AURORA_FETCHER_COMMAND:
                if os.fork():
                    return HttpResponseRedirect('..')

                else:
                    try:
                        daemonize()
                        os.execv(AURORA_FETCHER_COMMAND, ['fetcher', str(t.id)])
                    except:
                        os._exit(0)

    else:
        return render_to_response('aurora/add')
add = staff_member_required(add)
