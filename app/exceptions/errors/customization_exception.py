class BusinessFailException(Exception):
    """ 业务处理失败异常 """
    def __init__(self, message):
        self.message = message

class BusinessErrorException(Exception):
    """ 业务处理错误异常 """
    def __init__(self, code, message):
        self.code = code
        self.message = message