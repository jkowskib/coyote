import socket
import coyote

import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 80))
s.listen(1)

sock, addr = s.accept()
start = time.time()

request = coyote.Request.from_socket(sock)
request.read_body()

print(request.method, request.path, request.version)
print(request.headers)
print(request.body)

coyote.Response(
    version="HTTP/1.1",
    status_code=200,
    status_message="OK",
    headers={"Content-Type": "text/plain"},
    body=b"Hello, world!"
).send(sock)

end = time.time()
print(end - start)

sock.close()
