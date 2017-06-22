
ERR_SUCCESS = 0
ERR_INTERNAL_EXCEPTION = 100
ERR_NULL_REQUEST = 101
ERR_100_CONTINUE_REQUEST = 102

ERR_MSG = {
    ERR_SUCCESS: 'Success',
    ERR_NULL_REQUEST: 'Blank request',
    ERR_INTERNAL_EXCEPTION: 'Server internal exception',
    ERR_100_CONTINUE_REQUEST: 'This request has Expect: 100-continue header',
}


def get_err_msg(err):
    ERR_MSG.get(err, None)
