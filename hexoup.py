#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""

Hexo博客更新脚本
"""

__author__ = 'Gordon'

import os
from os import system
from os import path
import shutil
import time
import ConfigParser
from cn.bleu.utils import MD5Utils

_TITLE = 'title: '  # 标题
_DATE = 'date: '  # 日期
_CATEGORIES = 'categories: '  # 分类
_END = '---' + '\n\n'

_DATE_FORMATER = '%m/%d/%Y'

_DEBUG = True
_TEMP_DIR = '.work'

_username = ''
_server = ''
_work_path = ''
_remote_path = ''
_temp_path = ''


# interface
def main():
    print 'Hexo博客更新工具'
    app_main()


def app_main():
    """
    工具执行入口
    :return:
    """
    global _work_path
    global _temp_path

    # 1. 加载默认配置文件
    load_config()

    # 2. 查找 blog 文件
    files = get_blog_files()
    if not files:
        return
    else:
        # 3. 清理临时工作目录
        _temp_path = _work_path + path.sep + _TEMP_DIR
        if path.exists(_temp_path):
            shutil.rmtree(_temp_path)
        else:
            os.mkdir(_temp_path)

        for fp in files:
            _log('找到博客文件: %s' % fp)
            # 4. 处理文档
            handle_work_files(fp)

            # 5. 上传文件到服务器
            upload_blog_to_server()


def load_config():
    """
    加载配置文件
    :return:
    """

    global _work_path
    global _remote_path
    global _username
    global _server

    config = ConfigParser.ConfigParser()
    upath = os.path.expanduser('~')
    _log('user path: %s' % upath)

    u_config_path = path.join(upath, '.hexoup', 'hexoup.cfg')
    _log('config path: %s' % u_config_path)

    if not path.exists(u_config_path):
        p = path.join(upath, '.hexoup')
        if not path.exists(p):
            os.mkdir(path.join(upath, '.hexoup'))
        save_default_config(u_config_path)
        raise AssertionError('请修改$[HOME]/.hexoup/hexoup.cfg')
    else:
        with open(u_config_path, 'r') as cfg:
            config.readfp(cfg)
            uname = config.get('ssh', 'name').strip()
            userver = config.get('ssh', 'server').strip()

            upath = config.get('path', 'locale').strip()
            rpath = config.get('path', 'remote').strip()
            print 'HexoupConfig=>>\nname: %s, server: %s, locale path: %s, remote path: %s' % (
                uname, userver, upath, rpath)

            _username = uname
            _server = userver
            _work_path = path.abspath(upath)
            _remote_path = rpath


def save_default_config(config_path):
    """
    生成并保存默认的配置文件信息
    :param config_path: 配置文件保存地址
    :return:
    """
    with open(config_path, 'w') as cf:
        cf.write('[ssh]\n')
        cf.write('#ssh username\n')
        cf.write('name =  \n')
        cf.write('#ssh server\n')
        cf.write('server =  \n')
        cf.write('\n\n')

        cf.write('[path]\n')
        cf.write('#locale blog path\n')
        cf.write('locale =  \n')
        cf.write('#remote blog path\n')
        cf.write('remote =  \n')


def get_blog_files():
    """
    获取当前目录下的博客文件
    :return: files
    """
    global _work_path

    files = os.listdir(_work_path)
    new_files = []

    # 没有文件直接返回
    if not files:
        print 'none files found!!'
        return None

    # 过滤掉非 md 文件
    for fn in files:
        fn = path.join(_work_path, fn)
        if has_blog_file(fn):
            new_files.append(fn)

    return new_files


def has_blog_file(fp):
    """
    判断是否含有博客文件
    :param fp:
    :return: True, 含有博客文件
    """
    fname = path.basename(fp)
    if fname.endswith('.md'):
        return True
    elif fname.startswith("."):
        return False
    elif path.isdir(fp):
        return has_blog_file_in_folder(fp)
    else:
        return False


def has_blog_file_in_folder(fpath):
    """
    文件夹内是否有博客文件
    :param fpath:
    :return: True, 有博客文件
    """
    # 一个文件夹下, 只要有一个'.md'文件,即认为有博客文件
    has = False
    for fp in os.listdir(fpath):
        fp = path.join(fpath, fp)
        # 文件夹, 再次判断
        if path.isdir(path.join(fpath, fp)):
            has = has_blog_file_in_folder(fp)
            if has:
                break

        # 非文件夹, 且有'.md'
        elif has_blog_file(fp):
            has = True
            break

    return has


def handle_work_files(fpath):
    """
    处理目标文件夹
    :param fpath:
    :return:
    """
    if path.isdir(fpath):
        for fp in os.listdir(fpath):
            fp = path.join(fpath, fp)
            if path.isdir(fp):
                handle_work_files(fp)
            elif has_blog_file(fp) and need_alert_md_file(fp):
                alert_md_file(fp)
            else:
                print 'skip file: %s' % fp


def need_alert_md_file(f):
    """
    分析 MD 文件, 并确认是否需要修改. hexo 中 title: xxx 开头的部分为标题, 根据此验证是否已经符合hexo 的标准
    :param f:
    :return: True, 需要修改
    """
    with open(path.abspath(f), "r") as df:
        # 读取第一行, 如果不是 title: xxxx开始的, 则认为该文件不符合 hexo 规则,需要修改
        line = df.readline()
        return not line.startswith('title')


def alert_md_file(f):
    """
    修改 MD 文件.在文件开始部分加入:
    title: xxxx
    date: xx/xx/xxxx
    categories: xxxx
    ---
    :param f:
    :return:
    """
    global _temp_path

    title_str = _TITLE
    file_path = path.abspath(f)
    with open(file_path, 'r') as df:
        for line in df:
            if line.startswith('#'):
                title_str += line[(line.find('#') + 1):].strip()
                break

    title_str += '\n'
    date_str = _DATE + time.strftime(_DATE_FORMATER, time.localtime()) + '\n'
    cat_str = _CATEGORIES + get_categories_by_file(f) + '\n'

    temp_file_path = os.path.join(_temp_path, "".join(file_path[(_work_path.__len__() + 1):].split()))
    if not path.exists(path.dirname(temp_file_path)):
        os.makedirs(path.dirname(temp_file_path))

    with open(temp_file_path, 'w') as df:
        df.write(title_str)
        df.write(date_str)
        df.write(cat_str)
        df.write(_END)

        with open(file_path, 'r') as ff:
            for line in ff.readlines():
                df.write(line)

    return temp_file_path


def get_categories_by_file(f):
    """
    获取文章的分类
    :param f:
    :return:
    """
    fname = path.abspath(f).strip()
    last = fname.rfind(os.sep)
    categories = fname[(fname.rfind(os.sep, 0, last) + 1): last]
    return categories


def upload_blog_to_server():
    """
    上传博客文件到服务端
    :return:
    """
    global _temp_path

    for fp in os.listdir(_temp_path):
        upload_file_to_server(path.join(_temp_path, fp))


def upload_file_to_server(fpath):
    """
    上传文件
    :param fpath:
    :return:
    """

    if path.isdir(fpath):
        for fp in os.listdir(fpath):
            upload_file_to_server(path.join(fpath, fp))
    else:
        execute_upload_to_server(fpath)


def execute_upload_to_server(fp):
    """
    执行上传命令
    :param fp:
    :return:
    """

    global _username
    global _server
    global _remote_path

    print 'upload blog file to server, file: %s' % fp
    if _remote_path.endswith('/'):
        path_to = r'%s%s' % (_remote_path, path.basename(fp))
    else:
        path_to = r'%s/%s' % (_remote_path, path.basename(fp))

    # path_to = r'~/temp/%s' % path.basename(fp)
    path_from = fp

    system('scp %s %s@%s:%s' % (path_from, _username, _server, path_to))


def _log(msg):
    """
    打印日志信息
    :param msg: 日志内容
    :return:
    """
    if _DEBUG:
        print msg


# execute from commandlins
if __name__ == '__main__':
    main()
