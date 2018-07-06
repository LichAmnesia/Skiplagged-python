# -*- coding: utf-8 -*-
# @Author: Shen Huang
# @Date:   2018-06-15 16:46:18
# @Last Modified by:   Shen Huang
# @Last Modified time: 2018-06-28 18:11:02

from skiplagged import Skiplagged
import logging


logging.config.fileConfig('logging.conf')
logger = logging.getLogger('main')


def main():
    sk = Skiplagged()
    # sk._call()
    sk._test()


if __name__ == '__main__':
    main()
