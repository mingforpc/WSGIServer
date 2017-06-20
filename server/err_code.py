
ERR_SUCCESS = 0
ERR_INTERNAL_EXCEPTION = 100
ERR_NULL_REQUEST = 101

ERR_MSG = {
    ERR_SUCCESS: 'Success',
    ERR_NULL_REQUEST: 'Blank request',
    ERR_INTERNAL_EXCEPTION: 'Server internal exception',
}


def get_err_msg(err):
    ERR_MSG.get(err, None)
