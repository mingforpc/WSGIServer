#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import select, socket
#
# response = b"hello world"
#
# serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# serversocket.bind(('', 8080))
# serversocket.listen(1)
# serversocket.setblocking(0)
#
# inputs = [serversocket, ]
#
# while True:
#     rlist, wlist, xlist = select.select(inputs, [], [])
#     for sock in rlist:
#         if sock == serversocket:
#             con, addr = serversocket.accept()
#             inputs.append(con)
#         else:
#             data = sock.recv(1024)
#             if data:
#                 sock.send(response)
#                 inputs.remove(sock)
#                 sock.close()



def deco(func):

    print("before myfunc() called.")
    func()
    print("after myfunc() called.")
    # return func
    return func

@deco
def myfunc():
    print(" myfunc() called.")

myfunc()