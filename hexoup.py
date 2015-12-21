#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""

Hexo博客更新脚本
"""

__author__ = 'Gordon'

import os
from os import path
from os import system
import time
import ConfigParser
from cn.bleu.utils import MD5Utils

_TITLE = 'title: '  # 标题
_DATE = 'date: '  # 日期
_UPDATE_DATE = 'updated: '  # 更新日期
_CATEGORIES = 'categories: '  # 分类
_END = '---' + '\n\n'

_DATE_FORMATER = '%Y-%m-%d %H:%M:%S'

_DEBUG = True
_TEMP_DIR = '.work'

_username = ''
_server = ''
_work_path = ''
_remote_path = ''
_temp_path = ''

_hash_file = ''
_hash = {}

_documents_pending_upload = []  # 待上传的文件


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

    # 1. 初始化环境
    init_config()
    init_hash()

    # 2. 查找 blog 文件
    files = find_documents()
    if not files:
        return
    else:
        # 3. 准备工作目录
        _temp_path = _work_path + path.sep + _TEMP_DIR
        if not path.exists(_temp_path):
            os.mkdir(_temp_path)
        # 遍历目录或文档
        for fp in files:
            # 4. 处理文档
            handle_work_files(fp)

            # 5. 上传文件到服务器
            upload_documents()


def init_hash():
    """
    初始化 hash 环境
    :return:
    """
    global _hash_file
    global _hash

    _hash_file = path.join(_work_path, '.hash')

    if not path.exists(_hash_file):
        with open(_hash_file, 'w') as fp:
            fp.write('[hash]\n')
        _log('[hash] hash file created.')
    else:
        with open(_hash_file, 'r') as fp:
            config = ConfigParser.ConfigParser()
            config.readfp(fp)
            ks = config.items('hash')
            for key in ks:
                _hash[key[0]] = key[1]

        _log('[hash] env has inited.')


def init_config():
    """
    初始化配置信息
    :return:
    """

    global _work_path
    global _remote_path
    global _username
    global _server

    config = ConfigParser.ConfigParser()
    upath = os.path.expanduser('~')
    _log('[config] user path: %s' % upath)

    u_config_path = path.join(upath, '.hexoup', 'hexoup.cfg')
    _log('[config] config file path: %s' % u_config_path)

    if not path.exists(u_config_path):
        p = path.join(upath, '.hexoup')
        if not path.exists(p):
            os.mkdir(path.join(upath, '.hexoup'))
        save_default_config(u_config_path)
        raise AssertionError('You need modify the "[HOME]/.hexoup/hexoup.cfg" file!!')
    else:
        with open(u_config_path, 'r') as cfg:
            config.readfp(cfg)
            uname = config.get('ssh', 'name').strip()
            userver = config.get('ssh', 'server').strip()

            upath = config.get('path', 'locale').strip()
            rpath = config.get('path', 'remote').strip()
            print '[config] name: %s, server: %s, locale path: %s, remote path: %s' % (
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


def find_documents():
    """
    获取当前目录下博客文件或含有博客文件的目录
    :return: files
    """
    global _work_path

    files = os.listdir(_work_path)
    documents = []

    # 没有文件直接返回
    if not files:
        print 'none files found!!'
        return None

    # 过滤掉非 md 文件
    for fn in files:
        fn = path.join(_work_path, fn)
        if has_document(fn):
            documents.append(fn)

    return documents


def has_document(fp):
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
        return has_document_in_folder(fp)
    else:
        return False


def has_document_in_folder(fpath):
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
            has = has_document_in_folder(fp)
            if has:
                break

        # 非文件夹, 且有'.md'
        elif has_document(fp):
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
                # 如果是目录, 就继续搜索
                handle_work_files(fp)
            elif has_document(fp) and need_modify_document(fp):
                _log('[分析] 找到文档: %s' % fp)
                # 记录 hash 值
                write_document_hash(fp)
                # 生成临时文档
                modify_document(fp)
            else:
                print '[分析] 跳过文档: %s' % fp


def need_modify_document(fpath):
    """
    分析 MD 文件, 并确认是否需要修改. hexo 中 title: xxx 开头的部分为标题, 根据此验证是否已经符合hexo 的标准
    :param fpath:
    :return: True, 需要修改
    """

    # 读取 hash 文件, 如果文件不存在, 则是初次使用
    hash_file = path.join(_work_path, '.hash')
    if not path.exists(hash_file):
        return True
    else:
        return check_hash(fpath)


def write_document_hash(fpath):
    """

    :param fpath:
    :return:
    """
    global _hash
    global _hash_file

    name = MD5Utils.md5_string(path.basename(fpath))
    md5 = MD5Utils.md5_file(fpath)

    _hash[name] = md5

    config = ConfigParser.ConfigParser()
    config.read(_hash_file)
    config.set('hash', name, md5)
    with open(_hash_file, 'w+') as fp:
        config.write(fp)


def check_hash(fpath):
    """

    :param fpath:
    :return:
    """
    global _hash

    # 判断文件 hash 是否改变
    name = MD5Utils.md5_string(path.basename(fpath))
    md5 = MD5Utils.md5_file(fpath)

    if _hash and name in _hash and _hash[name] == md5:
        return False
    else:
        return True


def modify_document(fpath):
    """
    修改 md 文档.在文件开始部分加入:
    title: xxxx
    date: xx/xx/xxxx
    categories: xxxx
    ---
    :param fpath:
    :return:
    """
    global _temp_path
    global _documents_pending_upload

    title_str = _TITLE
    file_path = path.abspath(fpath)
    with open(file_path, 'r') as df:
        for line in df:
            if line.startswith('#'):
                title_str += line[(line.find('#') + 1):].strip()
                break

    title_str += '\n'
    date_str = _DATE + time.strftime(_DATE_FORMATER, time.localtime()) + '\n'
    cat_str = _CATEGORIES + get_categories_by_file(fpath) + '\n'
    update_str = ''

    temp_file_path = path.join(_temp_path, "".join(file_path[(_work_path.__len__() + 1):].split()))

    # 临时文件已经存在, 需要更新该临时文件
    if path.exists(temp_file_path):
        with open(temp_file_path, 'r') as df:
            for line in df:
                # hexo 文档 Front-matter 描述结束
                if line.startswith('---'):
                    break
                else:
                    if line.startswith(_TITLE):
                        title_str = line
                    elif line.startswith(_DATE):
                        date_str = line
                    elif line.startswith(_CATEGORIES):
                        cat_str = line
        # 补充更新时间
        update_str = _UPDATE_DATE + time.strftime(_DATE_FORMATER, time.localtime()) + '\n'

    elif not path.exists(path.dirname(temp_file_path)):
        os.makedirs(path.dirname(temp_file_path))

    with open(temp_file_path, 'w') as df:
        df.write(title_str)
        df.write(date_str)
        if update_str:
            df.write(update_str)

        df.write(cat_str)
        df.write(_END)

        with open(file_path, 'r') as ff:
            for line in ff.readlines():
                df.write(line)

    _documents_pending_upload.append(temp_file_path)


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


def upload_documents():
    """
    上传博客文件到服务端
    :return:
    """
    global _documents_pending_upload

    if _documents_pending_upload:
        for fp in _documents_pending_upload:
            upload_document_single(fp)
    else:
        _log('[upload] No documents to upload')


def upload_document_single(fpath):
    """
    上传文件
    :param fpath:
    :return:
    """

    if path.isdir(fpath):
        for fp in os.listdir(fpath):
            upload_document_single(path.join(fpath, fp))
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

    fname = path.basename(fp)
    print '[scp] upload document to server, title: %s' % fname
    path_to = path.join(_remote_path, fname)
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
