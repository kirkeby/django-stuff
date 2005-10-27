from BitTorrent import ConvertedMetainfo
from BitTorrent.defaultargs import get_defaults
from BitTorrent import configfile

uiname = 'btdownloadheadless'
defaults = get_defaults(uiname)
config, _ = configfile.parse_configuration_and_args(defaults, uiname, [], 0, 1)

ConvertedMetainfo.set_filesystem_encoding('utf-8', None)
