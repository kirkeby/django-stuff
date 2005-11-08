__version__ = "0.32"
from load import loadFile, load, Parser, l
from dump import dump, dumpToFile, Dumper, d
from stream import YamlLoaderException, StringStream, FileStream
from timestamp import timestamp

try:
    from ypath import ypath
except NameError:
    def ypath(expr,target='',cntx=''):
        raise NotImplementedError("ypath requires Python 2.2")

import sys
if sys.hexversion < 0x02010000:
    raise 'YAML is not tested for pre-2.1 versions of Python'
