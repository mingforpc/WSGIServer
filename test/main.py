
from server.http import WSGIServer
from server.request import WSGIRequest
from server.io_multiplex import IOMultiplex

import atexit

if __name__ == "__main__":
    server = WSGIServer(WSGIRequest, "0.0.0.0", 8888)
    server.set_blocking(0)
    # server = WSGIServer(HTTPRequest, '', 8888)
    from test.helloworld.helloworld.wsgi import application as app
    atexit.register(server.close)
    server.set_app(app)
    print("start")
    server.start()
    print("IO Started")
    IOMultiplex.initialized().start()