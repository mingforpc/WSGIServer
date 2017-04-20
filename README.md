# WSGIServer
A simpe wsgi server, just for leanring wsgi. learn from *Tornado*
```python
from server.http import WSGIServer
from server.request import WSGIRequest
from server.io_multiplex import IOMultiplex

if __name__ == "__main__":
    server = WSGIServer(WSGIRequest, "0.0.0.0", 8888)
    server.set_blocking(0)
    # SET YOUR OWN APP HERE
    from test.helloworld.helloworld.wsgi import application as app
    server.set_app(app)
    server.start()
    IOMultiplex.initialized().start()
```
