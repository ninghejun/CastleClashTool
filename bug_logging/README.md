引言
----
作为一个python新手，偶尔会遇到一些奇怪的问题。最近遇到一个问题，python中的module并不是只被import一次的，从而导致我们的logger组件会输出重复日志。

**基于module import机制的单例是不可靠的,有可能会被多次import从而创建出多个实例。**

下面简单和大家分享一下。


问题描述
----
之前看到过文章，说python中的包只会被import一次，所以可以用module内的全局变量来实现单例。
[参考链接：Python单例模式终极版](https://blog.csdn.net/GhostFromHeaven/article/details/7671914)

但是我的这个case发现并不是如此，我们有一个logger.py放在log这个目录下，然后外部有两个py文件对它进行import。代码结构如下：
    
    .
    ├── README.md
    ├── log
    │   ├── __init__.py
    │   └── logger.py
    ├── main.py
    └── util.py

其中logger.py的代码如下：

    import logging
    import logging.handlers
    
    
    def get_logger():
        logger = logging.getLogger("a")
        logger.setLevel(logging.DEBUG)
        stdout_handler = logging.StreamHandler()
        logger.addHandler(stdout_handler)
        return logger
    
    
    logger = get_logger()
    
我们有理由相信，不管logger这个模块被import几次，logger = get_logger()这行代码只会执行一次，只会有一个logger实例。

然后，util.py和main.py都会import这个logger，代码如下

util.py:

    from logger import logger

    def util_a():
        pass


main.py:

    from util import util_a
    from log.logger import logger
    
    if __name__ == '__main__':
        logger.debug("test loggger.debug")

我们认为，运行main.py将输出一行日志，test loggger.debug。
然而，实际运行main.py,结果是两行日志：
    
    $ python3 main.py 
    test loggger.debug
    test loggger.debug         

这是怎么回事呢？
        
问题原因
----
经过排查代码（实际项目远比这个demo复杂，所以排查代码也不容易），我们发现，代码中存在两种import方式：

    from logger import logger
    from log.logger import logger

很可能是这两种方式import导致的。将这两种import改成一致，日志就只有一行了。
之所以可以用两种方式import， 是因为我们项目中，将log这个路径加入到了sys.path中。所以两种方式都可以搜索到。

这两种方式import的是同一个python文件，为什么python会import两次呢？难道python没有智能地判断这两种不同的import写法，其实是import同一个.py文件吗？

我们来验证一下，我们知道，所有import的module，都在sys.modules里面，所以将它输出来看一下，考虑到module众多，所以只过滤出logger相关的module，代码如下：
    
    log_modules={k:v for k,v in sys.modules.items() if k.find("logger")!=-1}
    print("log_modules=",log_modules)
    
运行一下，得到结果：
    
    log_modules= {'logger': <module 'logger' from 'log/logger.py'>, 'log.logger': <module 'log.logger' from '/Users/andyning/PycharmProjects/learn_python/log/logger.py'>}
    
果然，我们发现sys.modules含有 logger和 log.logger 这两个module，这两个module分别import了一次，从而调用了两次get_logger()这个函数。
而两次logging.getLogger会返回同一个logger对象，只是增加了两个handler，从而输出了两行重复的日志。

所以基于module import机制的单例是不可靠的。假如我们这里不是logger组件，而是别的单例组件，那么我们这两种不同的import方式，就会产生两个实例，从而保证不了单例。

参考资料：
[python官方文档 导入系统](https://docs.python.org/zh-cn/3/reference/import.html)

解决方案
----

查到了原因，就很容易解决。
首先，我们把所有import都改成同一种写法， 

    from log.logger import logger
    
其次，保不准别人新增代码的时候，还会使用不同的import方式，所以需要在logger.py组件中加上保护，要保证就算多次impot仍然是幂等的，不会有什么副作用。

这种做法，当然就是module里面只声明class和function，不定义任何变量也不调用任何函数，自然就不会有什么副作用了。

当然，针对logger这个特殊情况，我们可以简单地对logger.handlers加一个判断就可以了：

    def get_logger():
        logger = logging.getLogger("a")
        if logger.handlers:
            return logger
        logger.setLevel(logging.DEBUG)
        stdout_handler = logging.StreamHandler()
        logger.addHandler(stdout_handler)
        return logger

改完之后，就ok了，日志只有一行了。

经验总结
----
1. 基于module import机制的单例是不可靠的,有可能会被多次import从而创建出多个实例，需要注意加上幂等性保护
2. 一个module应该只有一种方式import，这也是python的哲学，所以项目中的子目录不要加入到sys.path中

    
示例代码
----
[github代码链接](https://github.com/ninghejun/learn_python/tree/master/bug_logging)