#!/usr/bin/env python
# encoding: utf-8
"""
@author: andyning
@time: 2019-06-12 18:10
@desc: 
"""

import logging
import logging.handlers


def get_logger():
    logger = logging.getLogger("a")
    # if logger.handlers:     #取消注释即可修复日志重复的bug
    #     return logger
    logger.setLevel(logging.DEBUG)
    stdout_handler = logging.StreamHandler()
    logger.addHandler(stdout_handler)
    return logger


logger = get_logger()
