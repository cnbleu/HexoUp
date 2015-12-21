#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

' description '

__author__ = 'Gordon'

RE_CODE = r'"(.*?)"'


def main(cmd):
    """

    application interface
    :param cmd:
    :return: None
    """
    print 'start codes handler, cmd: %d' % cmd

    filelist()


def filelist():
    # get current fiel dir
    fs = os.listdir(os.path.curdir)

    if not fs:
        print 'path is not a dir.'
        return

    for f in fs:
        # 非隐藏文件, 非文件夹
        if not f.startswith('.') and not os.path.isdir(f):
            print 'name: %s, path: %s' % (f.title(), os.path.abspath(f))

            if f.endswith('.java'):
                lines = open(f, "rw").readlines()
                count = 0
                while count < lines.__len__():
                    data = lines[count]
                    print 'line origin data: %s' % data

                    if data.strip().startswith('@Element'):
                        next_data = lines[count + 1]
                        handleline(data, next_data, count)
                        count += 2
                        return
                    else:
                        count += 1

                # TODO
                return


def handleline(data, next_data, count):
    """
    处理数据
    :param data:
    :param next_data:
    :param count:
    :return: None
    """

    data = data.strip()
    next_data = next_data.strip()
    print 'lines(%d): ,\ndata: %s\nnext: %s' % (count, data, next_data)

    codes = re.split('\(', data)
    if codes:
        print 're: %s' % codes
        name = find_name_with_comma(codes[1]).strip()

        if name:
            print 'result: %s' % name


def find_name_with_comma(code):
    """
    根据‘,’找到需要修改的名字
    :param code:
    :return:
    """
    if not isinstance(code, str):
        raise AssertionError

    if code.__contains__(','):
        cd = re.split(',', code)
        if not cd:
            return None

        print 'find_name, spilt ","%s: ' % cd

        for c in cd:
            result = find_name_with_equal(c)
            if result:
                return result

    return None


def find_name_with_equal(code):
    """
    根据‘=’找到需要修改的名字
    :param code:
    :return:
    """
    if not isinstance(code, str):
        raise AssertionError

    result = re.split(r'\s+=', code)
    if result and 'name' == result[0]:
        return result[1]
    else:
        return None


# if started by command, execute 'main()'.
if __name__ == '__main__':
    main(1)
