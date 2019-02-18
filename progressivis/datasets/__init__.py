import os
import os.path
import six
from progressivis import ProgressiveError
from .random import generate_random_csv, generate_random_multivariate_normal_csv
from .wget import wget_file
import bz2
import zlib

from functools import partial

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
Z_CHUNK_SIZE = 16*1024*32

def get_dataset(name, **kwds):
    if not os.path.isdir(DATA_DIR):
        os.mkdir(DATA_DIR)
    if name == 'bigfile':
        return generate_random_csv('%s/bigfile.csv'%DATA_DIR, 1000000, 30)
    if name == 'bigfile_mvn':
        return generate_random_multivariate_normal_csv('%s/bigfile_mvn.csv'%DATA_DIR, 900000)
    if name == 'smallfile':
        return generate_random_csv('%s/smallfile.csv'%DATA_DIR, 30000, 10)
    if name == 'warlogs':
        return wget_file(filename='%s/warlogs.vec.bz2'%DATA_DIR,
                         url='http://www.cs.ubc.ca/labs/imager/video/2014/QSNE/warlogs.vec.bz2',
                         **kwds)
    if name.startswith('cluster:'):
        fname = name[len('cluster:'):] + ".txt"
        return wget_file(filename='%s/%s'%(DATA_DIR, fname),
                         url='http://cs.joensuu.fi/sipu/datasets/%s'%fname)
    raise ProgressiveError('Unknown dataset %s'%name)

if six.PY3:
    import lzma
    compressors = dict(bz2=dict(ext='.bz2', factory=bz2.BZ2Compressor),
                        zlib=dict(ext='.zlib', factory=zlib.compressobj),
                        gzip=dict(ext='.gz', factory=partial(zlib.compressobj, wbits=zlib.MAX_WBITS|16)),
                        lzma=dict(ext='.xz', factory=lzma.LZMACompressor)
                        )
else:
    compressors = dict(bz2=dict(ext='.bz2', factory=bz2.BZ2Compressor),
                        zlib=dict(ext='.zlib', factory=zlib.compressobj),
                        gzip=dict(ext='.gz', factory=partial(zlib.compressobj,
                                                        zlib.Z_DEFAULT_COMPRESSION,
                                                        zlib.DEFLATED, zlib.MAX_WBITS|16)))


def get_dataset_compressed(name, compressor, **kwds):
    source_file = get_dataset(name, **kwds)
    dest_file = source_file+compressor['ext']
    if os.path.isfile(dest_file):
        return dest_file
    compressor = compressor['factory']()
    with open(source_file, 'rb') as rdesc:
        with open(dest_file, 'wb') as wdesc:
            while True:
                data = rdesc.read(Z_CHUNK_SIZE)
                if not data:
                    break
                wdesc.write(compressor.compress(data))
            wdesc.write(compressor.flush())
    return dest_file

def get_dataset_bz2(name, **kwds):
    return get_dataset_compressed(name, compressors['bz2'], **kwds)

def get_dataset_zlib(name, **kwds):
    return get_dataset_compressed(name, compressors['zlib'], **kwds)

def get_dataset_gz(name, **kwds):
    return get_dataset_compressed(name, compressors['gzip'], **kwds)

if six.PY3:
    def get_dataset_lzma(name, **kwds):
        return get_dataset_compressed(name, compressors['lzma'], **kwds)
else:
    def get_dataset_lzma(name, **kwds):
        raise ValueError("lzma compression is not supported in Python 2.x")

__all__ = ['get_dataset', 'get_dataset_bz2','get_dataset_zlib','get_dataset_gz',
               'get_dataset_lzma', 'generate_random_csv']
