# -*- coding: utf-8 -*-

import hashlib
from os import path

"""
MD5Utils
"""

__author__ = 'Gordon'

_DEBUG = False


def md5_file(fpath):
    """
    :param fpath:
    :return: None or md5 string.
    """
    if not path.exists(fpath):
        if _DEBUG:
            _log('%s not exists.') % fpath
        return None

    md = hashlib.md5()
    with open(fpath, 'rb') as fp:
        while True:
            blk = fp.read(4096)  # 4KB per block
            if not blk: break
            md.update(blk)

    md5 = md.hexdigest()

    _log('file:[%s] md5: %s' % (fpath, md5))
    return md5


def md5_string(string):
    """

    :param string:
    :return:
    """
    md = hashlib.md5()
    md.update(string)
    md5 = md.hexdigest()

    _log('[%s] md5: %s' % (string, md5))
    return md5


def _log(msg):
    """

    :param msg:
    :return:
    """
    if not _DEBUG:
        return

    print '[MD5Utils] %s' % msg


if __name__ == '__main__':
    md5_file('/Users/gordon/work/darling/python/HexoUp/hexoup.py')
    md5_string('hello, world')
