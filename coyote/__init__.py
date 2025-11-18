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
        """
        An HTTP Request object
        :param method: HTTP Method
        :param path: Path of the request
        :param version: HTTP Version
        :param headers: HTTP Headers
        :param body: Body of the request (if any)
        :param stream: StreamHTTPSocket for streamed request (if any)
        :raises MissingRequiredFields: if a body nor a stream are given
        """
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
        """
        Gets the request body (if any)
        :return: bytes
        :raises IncompleteBody: if the body is not processed yet for a streamed Request
        """
        if self.__body is None:
            return self.__stream.body
        else:
            return self.__body

    @staticmethod
    def from_socket(sock, buffer_size: int = 1024) -> "Request":
        """
        Read a socket and build a Request object
        :param sock: socket to read from
        :param buffer_size: size of buffer
        :return: Request object
        """
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
        """
        Reads the body of the request
        :param buffer_size: buffer size to use
        :return: Number of bytes read
        :raises BodyAlreadyRead: if this method is called multiple times
        """
        return self.__stream.read_body(buffer_size)

    def send(self, sock: socket.socket) -> None:
        """
        Send Request to a socket in full
        :param sock: socket to send to
        :return: None
        """
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
        """
        HTTP Response object
        :param version: HTTP Version
        :param status_code: HTTP Status code
        :param status_message: HTTP Status message
        :param headers: HTTP Headers
        :param body: Response body (if any)
        :param stream: StreamHTTPSocket for streamed response reading (if any)
        :raises MissingRequiredFields: if a body nor a stream are given
        """
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
        """
        Read a socket and build a Response object
        :param sock: socket to read from
        :param buffer_size: size of buffer
        :return: Response object
        """
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
        """
        Reads body from a Response
        :param buffer_size: buffer size to use
        :return: number of bytes read
        :raises BodyAlreadyRead: if this method is called multiple times
        """
        return self.__stream.read_body(buffer_size)

    def send(self, sock: socket.socket) -> None:
        """
        Send Response to a socket in full
        :param sock: socket to send to
        :return: None
        """
        send_http_message(
            sock,
            (self.version, str(self.status_code), self.status_message),
            self.headers,
            self.body
        )
