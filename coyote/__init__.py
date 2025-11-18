import socket

from coyote.errors import MissingRequiredFields
from coyote.net import StreamHTTPSocket, send_http_message

HTTP_VERSION = "HTTP/1.1"


class Request:
    def __init__(
            self,
            method: str,
            path: str,
            version: str,
            headers: dict[str, str],
            body: bytes | None = None,
            stream: net.StreamHTTPSocket | None = None
    ):
        self.method = method
        self.path = path
        self.version = version
        self.headers = headers
        self.__body: bytes | None = body
        self.__stream: StreamHTTPSocket | None = stream

        if self.__body is None and self.__stream is None:
            raise MissingRequiredFields("a StreamHTTPSocket must be given if the body is not already specified")

    @property
    def body(self) -> bytes:
        if self.__body is None:
            return self.__stream.body
        else:
            return self.__body

    @staticmethod
    def from_socket(sock, buffer_size: int = 1024) -> "Request":
        stream = net.StreamHTTPSocket(sock)

        while True:
            if stream.read(buffer_size) == -1:
                break

        return Request(
            method=stream.status[0],
            path=stream.status[1],
            version=stream.status[2],
            headers=stream.headers,
            stream=stream
        )

    def read_body(self, buffer_size: int = 1024) -> int:
        return self.__stream.read_body(buffer_size)

    def send(self, sock: socket.socket) -> None:
        send_http_message(
            sock,
            (self.method, self.path, self.version),
            self.headers,
            self.body
        )


class Response:
    def __init__(
            self,
            version: str,
            status_code: int,
            status_message: str,
            headers: dict[str, str],
            body: bytes | None = None,
            stream: net.StreamHTTPSocket = None
    ):
        self.version = version
        self.status_code = status_code
        self.status_message = status_message
        self.headers = headers
        self.__body: bytes | None = body
        self.__stream: StreamHTTPSocket | None = stream

        if self.__body is None and self.__stream is None:
            raise MissingRequiredFields("a StreamHTTPSocket must be given if the body is not already specified")

    @property
    def body(self) -> bytes:
        if self.__body is None:
            return self.__stream.body
        else:
            return self.__body

    @staticmethod
    def from_socket(sock, buffer_size: int = 1024) -> "Response":
        stream = net.StreamHTTPSocket(sock)

        while True:
            if stream.read(buffer_size) == -1:
                break

        return Response(
            version=stream.status[0],
            status_code=stream.status[1],
            status_message=stream.status[2],
            headers=stream.headers,
            stream=stream
        )

    def read_body(self, buffer_size: int = 1024) -> int:
        return self.__stream.read_body(buffer_size)

    def send(self, sock: socket.socket) -> None:
        send_http_message(
            sock,
            (self.version, str(self.status_code), self.status_message),
            self.headers,
            self.body
        )
