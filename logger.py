import logging

def createLogger(name,level,state=None):

    logger = logging.getLogger('%sLogger'%(name))
    logger.setLevel(level)

    file_handler = logging.FileHandler('./Logs/%sLog.log'%(name))
    file_handler.setLevel(level)

    formatter = logging.Formatter(
	    '\n%(asctime)s :: %(levelname)s :: %(message)s',
	    '%d %b %Y - %H:%M')

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    ########## FOR DEVELOPMENT ONLY
    if state == 'DEVELOPMENT':
        logger.addHandler(logging.StreamHandler())

    return logger