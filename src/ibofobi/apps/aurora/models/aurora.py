from ibofobi.apps.aurora.utils import bittorrent

from django.core import meta

TORRENT_STATUS = (
    ('wk', 'Working'),
    ('pa', 'Paused'),
    ('fi', 'Finished'),
    ('er', 'Error'),
)
class Torrent(meta.Model):
    """I hold the persistent information of a torrent."""
    name = meta.CharField(maxlength=50)
    status = meta.CharField(maxlength=2, choices=TORRENT_STATUS, default='wk')

    downloaded = meta.IntegerField(default=0)
    uploaded = meta.IntegerField(default=0)

    created = meta.DateTimeField(auto_now_add=True)
    completed = meta.DateTimeField(blank=True, null=True)

    def is_paused(self):
        return self.status == 'pa'

    def get_eta_display(self):
        import datetime
        from django.models.aurora import fetchers
        from django.utils.timesince import timesince

        try:
            if self.fetcher.download_rate:
                seconds = (self.metainfo.total_bytes - self.downloaded) / self.fetcher.download_rate
                days = seconds / (24 * 60 * 60)
                seconds = seconds % (24 * 60 * 60)
                
                now = datetime.datetime.now()
                delta = datetime.timedelta(days=days, seconds=seconds)

                return timesince(now, now + delta)

            else:
                return ''

        except fetchers.FetcherDoesNotExist:
            return ''

    def get_downloaded_percent(self):
        return self.downloaded * 100.0 / self.metainfo.total_bytes

    def __repr__(self):
        return self.name

    def __getattr__(self, name):
        if name == 'fetcher':
            from django.models.aurora import fetchers
            self.fetcher = fetchers.get_object(pk=self.id)
            return self.fetcher
        elif name == 'metainfo':
            from django.models.aurora import metainfos
            self.metainfo = metainfos.get_object(pk=self.id)
            return self.metainfo
        else:
            raise AttributeError, name

    class META:
        admin = meta.Admin()

class Metainfo(meta.Model):
    """I hold the persistent metainformation about a torrent (i.e. the torrent-file.)"""
    torrent = meta.OneToOneField(Torrent, primary_key=True)
    # BEWARE -- metainfo is base64-encoded
    metainfo = meta.TextField()

    # Cached from the parsed metainfo, filled in by _pre_save
    total_bytes = meta.IntegerField()

    def get_parsed(self):
        """Return the parsed metainfo (BitTorrent.ConvertedMetainfo)."""
        if not hasattr(self, 'metainfo_parsed'):
            from BitTorrent.bencode import bdecode
            from BitTorrent.ConvertedMetainfo import ConvertedMetainfo

            import base64

            # Interesting keys in metainfo:
            #   'hashes', 'infohash', 'is_batch', 'name', 'name_fs', 'orig_files',
            #   'piece_length', 'reported_errors', 'show_encoding_errors', 'sizes',
            #   'total_bytes']
            self.metainfo_parsed = ConvertedMetainfo(bdecode(base64.decodestring(self.metainfo)))

        return self.metainfo_parsed

    def _pre_save(self):
        p = self.get_parsed()
        self.total_bytes = p.total_bytes

    def __getattr__(self, *args):
        p = self.get_parsed()
        return getattr(p, *args)
        
TORRENT_FETCHER_STATUS = (
    ('ld', 'Loading'),
    ('ck', 'Checking'),
    ('dl', 'Downloading'),
    ('sd', 'Seeding'),
    ('fi', 'Finishing'),
)
class Fetcher(meta.Model):
    """I hold the ephemeral status of a torrent being fetched."""
    torrent = meta.OneToOneField(Torrent, primary_key=True)
    status = meta.CharField(maxlength=2, choices=TORRENT_FETCHER_STATUS)

    process_id = meta.IntegerField()
    created = meta.DateTimeField()
    updated = meta.DateTimeField(auto_now=True)

    upload_rate = meta.IntegerField(default=0)
    download_rate = meta.IntegerField(default=0)

    peers = meta.IntegerField(default=0)
    seeds = meta.IntegerField(default=0)
    copies = meta.FloatField(max_digits=6, decimal_places=1, default=0.0)

    def kill_process(self):
        import os, signal
        os.kill(self.process_id, signal.SIGTERM)

    class META:
        admin = meta.Admin()

MESSAGE_SEVERITIES = (
    ('dbg', 'Debug'),
    ('inf', 'Informational'),
    ('err', 'Error'),
)
class Message(meta.Model):
    """I hold a message from a fetcher."""
    torrent = meta.ForeignKey(Torrent, blank=True, null=True)
    logged = meta.DateTimeField(auto_now_add=True)
    severity = meta.CharField(maxlength=3, choices=MESSAGE_SEVERITIES)
    content = meta.TextField()

    class META:
        admin = meta.Admin()

    def _module_debug(torrent, content):
        Message(torrent=torrent, severity='dbg', content=content.strip()).save()
    def _module_info(torrent, content):
        Message(torrent=torrent, severity='inf', content=content.strip()).save()
    def _module_error(torrent, content):
        Message(torrent=torrent, severity='err', content=content.strip()).save()
