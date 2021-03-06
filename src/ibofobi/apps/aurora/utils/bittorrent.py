# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

# BitTorrent is a stinking heap of dung, so I have to
# work around it with these hacks,

import sys
if not hasattr(sys, 'argv'):
    sys.argv = ['/usr/bin/python']
    import BitTorrent
    import BitTorrent.configfile
    del sys.argv

from BitTorrent import ConvertedMetainfo
from BitTorrent.defaultargs import get_defaults
from BitTorrent import configfile

uiname = 'btdownloadheadless'
defaults = get_defaults(uiname)
config, _ = configfile.parse_configuration_and_args(defaults, uiname, [], 0, 1)

ConvertedMetainfo.set_filesystem_encoding('utf-8', None)
