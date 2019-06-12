#!/usr/bin/env python
# encoding: utf-8
"""
@author: andyning
@time: 2019-06-12 18:05
@desc: 
"""

import sys
sys.path.append("log")

#util.py
from util import util_a
from log.logger import logger

if __name__ == '__main__':
    logger.debug("test loggger.debug")
    log_modules={k:v for k,v in sys.modules.items() if k.find("logger")!=-1}
    print("log_modules=",log_modules)
