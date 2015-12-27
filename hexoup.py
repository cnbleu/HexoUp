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

_DEBUG = True
_WORK_DIR = '.work'
_WORK_HASH = '.hash'

_CONTENT_TITLE = 'title: %s\n'  # 标题
_CONTENT_DATE = 'date: %s\n'  # 日期
_CONTENT_UPDATE_DATE = 'updated: %s\n'  # 更新日期
_CONTENT_CATEGORIES = 'categories: \n'  # 分类
_CONTENT_TAGS = 'tag: \n'  # 分类
_CONTENT_END = '---' + '\n\n'

_FILE_CATEGORIES = '.categories'  # 保存默认分类的文件
_FILE_TAGS = '.tags'  # 保存默认标签的文件
_FILE_IGNORE = '.ignore'  # 忽略当前文件夹

_DATE_FORMATER = '%Y-%m-%d %H:%M:%S'

_username = ''
_server = ''
_work_path = ''
_remote_path = ''
_temp_path = ''

_hash_file = ''
_hash = {}

_documents_pending = []  # 待上传的文件


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
        # 遍历目录或文档
        for fp in files:
            # 4. 处理文档
            process_documents(fp)
        # 5. 上传文件到服务器
        upload_documents()


def init_hash():
    """
    初始化 hash 环境
    :return:
    """
    global _hash_file
    global _hash

    _hash_file = path.join(_temp_path, _WORK_HASH)

    if not path.exists(_hash_file):
        with open(_hash_file, 'w') as fp:
            fp.write('[hash]\n')
        _log('[哈希校验] 初始化哈希环境.')
    else:
        with open(_hash_file, 'r') as fp:
            config = ConfigParser.ConfigParser()
            config.readfp(fp)
            ks = config.items('hash')
            for key in ks:
                _hash[key[0]] = key[1]

        _log('[哈希校验] 文件哈希值读取成功.')


def init_config():
    """
    初始化配置信息
    :return:
    """

    global _work_path
    global _temp_path
    global _remote_path
    global _username
    global _server

    config = ConfigParser.ConfigParser()
    upath = os.path.expanduser('~')
    _log('[初始化] 用户目录: %s' % upath)

    u_config_path = path.join(upath, '.hexoup', 'hexoup.cfg')
    _log('[初始化] 配置文件目录: %s' % u_config_path)

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
            print '[初始化] name: %s, server: %s, locale path: %s, remote path: %s' % (
                uname, userver, upath, rpath)

            _username = uname
            _server = userver
            _work_path = path.abspath(upath)
            _remote_path = rpath

    # 准备工作目录
    _temp_path = path.join(_work_path, _WORK_DIR)
    if not path.exists(_temp_path):
        os.mkdir(_temp_path)


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


def process_documents(fpath):
    """
    处理目标目标文档
    :param fpath:
    :return:
    """
    if path.isdir(fpath):
        for fp in os.listdir(fpath):
            fp = path.join(fpath, fp)
            if path.isdir(fp):
                # 如果是目录, 就继续搜索
                process_documents(fp)
            elif has_document(fp) and need_modify_document(fp):
                _log('[文档分析] 找到文档: %s' % fp[(_work_path.__len__() + 1):])
                # 记录 hash 值
                write_document_hash(fp)
                # 生成临时文档
                modify_document(fp)
            else:
                print '[文档分析] 跳过文档: %s' % fp[(_work_path.__len__() + 1):]


def need_modify_document(fpath):
    """
    分析 MD 文件, 并确认是否需要修改. hexo 中 title: xxx 开头的部分为标题, 根据此验证是否已经符合hexo 的标准
    :param fpath:
    :return: True, 需要修改
    """
    # 如果当前文件夹存在.ignore文件, 则忽略当前文件夹
    if path.exists(path.join(path.dirname(fpath), _FILE_IGNORE)):
        _log('[文档分析] 文档需要被忽略, 文件名: %s' % path.basename(fpath))
        return False

    # 读取 hash 文件, 如果文件不存在, 则是初次使用
    hash_file = path.join(_temp_path, '.hash')
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
    global _documents_pending

    # 文章标题
    content_title = _CONTENT_TITLE % path.basename(fpath)
    # 文章创建日期
    content_create_date = ''
    # 文章更新日期
    content_update_date = ''
    # 文章分类
    content_categories = _CONTENT_CATEGORIES
    # 文章标签
    content_tags = _CONTENT_TAGS

    # 临时文件
    temp_file_path = path.join(_temp_path, "".join(fpath[(_work_path.__len__() + 1):].split()))

    # 临时文件已经存在, 需要更新该临时文件
    if path.exists(temp_file_path):
        with open(temp_file_path, 'r') as df:
            for line in df:
                # hexo 文档 Front-matter 描述结束
                if line.startswith('---'):
                    break
                else:
                    if line.startswith(_CONTENT_TITLE):
                        content_title = line
                    elif line.startswith(_CONTENT_DATE):
                        content_create_date = line

        # 临时文件已存在, 则需要保持创建日期不变, 更新更新时间
        content_update_date = _CONTENT_UPDATE_DATE % time.strftime(_DATE_FORMATER, time.localtime())
    elif not path.exists(path.dirname(temp_file_path)):
        os.makedirs(path.dirname(temp_file_path))

    # 如果不存在创建日期, 则初始化
    if not content_create_date:
        content_create_date = _CONTENT_DATE % time.strftime(_DATE_FORMATER, time.localtime())

    # TODO next主题似乎对分类的支持不是特别好,暂时屏蔽分类功能
    # 构造分类
    # categories = find_categories_by_path(fpath)
    # if categories:
    #     for cate in categories:
    #         content_categories += ('- ' + cate + '\n')
    #     content_categories += '\n'

    # 构造标签
    tags = find_tags_by_path(fpath)
    if tags:
        for tag in tags:
            content_tags += ('- ' + tag + '\n')
        content_tags += '\n'

    with open(temp_file_path, 'w') as df:
        # 写入标题
        df.write(content_title)
        # 写入创建时间
        df.write(content_create_date)
        # 写入更新时间
        if content_update_date:
            df.write(content_update_date)
        # 写入分类
        if content_categories != _CONTENT_CATEGORIES:
            df.write(content_categories)
        # 写入标签
        if content_tags != _CONTENT_TAGS:
            df.write(content_tags)
        # 写入结束符
        df.write(_CONTENT_END)

        with open(fpath, 'r') as ff:
            for line in ff.readlines():
                df.write(line)

    # 记录待上传文件
    _documents_pending.append(temp_file_path)


def find_categories_by_path(fp):
    """
    根据文件路径获取预设的分类
    :param fp:
    :return:
    """
    categories = find_meta_by_path(fp)
    categories.append(path.basename(path.dirname(fp)))
    return categories


def find_tags_by_path(fp):
    """
    根据文件路径获取预设的标签
    :param fp:
    :return:
    """

    return find_meta_by_path(fp, _FILE_TAGS)


def find_meta_by_path(fp, meta=_FILE_CATEGORIES):
    """
    根据文件路径获取预设的数值
    :param fp:
    :param meta: 指定的文件类型
    :return: [], 数值列表
    """

    metas = []
    fpath = path.dirname(fp)
    while True:
        if fpath == _work_path:
            break

        if path.isdir(fpath):
            for f in os.listdir(fpath):
                if path.basename(f) == meta:
                    with open(path.join(fpath, f), 'r') as cf:
                        for line in cf.readlines():
                            metas.append(line)
            fpath = path.dirname(fpath)

    return metas


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
    global _documents_pending

    if _documents_pending:
        for fp in _documents_pending:
            upload_document_single(fp)
    else:
        _log('[上传文档] 没有符合条件的文档')


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
    path_to = path.join(_remote_path, fname)
    # path_to = r'~/temp/%s' % path.basename(fp)
    path_from = fp

    system('scp %s %s@%s:%s' % (path_from, _username, _server, path_to))
    print '[>>>>>>>] 文档已上传: %s' % fname


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
