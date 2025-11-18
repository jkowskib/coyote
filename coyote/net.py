import socket

from coyote.errors import BodyAlreadyRead, InvalidStatusHeader, InvalidHeader, IncompleteBody


class StreamHTTPSocket:
    def __init__(self, soc: socket.socket) -> None:
        self.__soc: socket.socket = soc
        self.__buffer: bytearray = bytearray()
        self.__buffer_cursor: int = 0

        self.__status: tuple | None = None
        self.__headers: dict[str, str] = {}
        self.__body: bytearray = bytearray()

        self.__body_complete: bool = False
        self.__headers_complete: bool = False

    @property
    def status(self) -> tuple:
        return self.__status

    @property
    def headers(self) -> dict[str, str]:
        return self.__headers

    @property
    def body(self):
        if not self.__body_complete:
            raise IncompleteBody("sockets body has not been read")
        return self.__body

    def read(self, buffer_size: int) -> int:
        """
        Reads from the socket given a buffer size and returns the number of bytes read, also runs parsing
        on the buffer if any data can be parsed with the buffer read in.
        :param buffer_size: size of buffer to read
        :return: number of bytes read
        """
        if self.__headers_complete:
            return -1

        data = self.__soc.recv(buffer_size)
        self.__buffer.extend(data)
        self.__parse_buffer()
        return len(data)

    def read_body(self, buffer_size: int) -> int:
        """
        Reads in the body of the HTTP message from the socket. Only can be run once.
        :param buffer_size: size of buffer to read
        :return: number of bytes read in for the body
        """
        if self.__body_complete:
            raise BodyAlreadyRead("the body for this socket is already read")

        body_size = self.__headers.get("Content-Length", "-1")
        if not body_size.isdigit() or body_size == "-1":
            self.__body_complete = True
            return 0

        body_size = int(body_size)

        read_bytes = 0

        while read_bytes < body_size:
            data = self.__soc.recv(
                min(buffer_size, body_size - read_bytes)
            )
            self.__body.extend(data)
            read_bytes += len(data)

        self.__body_complete = True

        return read_bytes

    def discard_body(self, buffer_size: int) -> None:
        """
        Reads and discards body of request if it's not needed to ensure socket is clear
        :param buffer_size: The size of buffer to read
        :return: None
        """
        if self.__body_complete:
            raise BodyAlreadyRead("the body for this socket is already read")

        body_size = self.__headers.get("Content-Length", "-1")
        if not body_size.isdigit() or body_size == "-1":
            self.__body_complete = True
            return

        body_size = int(body_size)

        read_bytes = 0

        while read_bytes < body_size:
            data = self.__soc.recv(
                min(buffer_size, body_size - read_bytes)
            )
            read_bytes += len(data)

        self.__body_complete = True

    def __parse_buffer(self) -> None:
        """
        Attempts to fill fields from the buffer (skips running if there is not enough data to parse)
        :return: None
        """
        while True:
            region = self.__buffer[self.__buffer_cursor:]
            if not region:
                return

            line_end = region.find(b"\r\n")

            if line_end == -1:
                return

            self.__buffer_cursor += line_end + 2

            parse_region = region[:line_end].decode("utf-8")
            if len(parse_region) == 0:
                self.__headers_complete = True
                self.__body.extend(self.__buffer[self.__buffer_cursor:])
                return
            elif self.__status is None:
                status_parts = parse_region.split(" ", 2)
                if len(status_parts) != 3:
                    raise InvalidStatusHeader(
                        f"socket returned an invalid status header (expected 3 parts, got {len(parse_region)})")
                self.__status = (status_parts[0], status_parts[1], status_parts[2])
            else:
                header_parts = parse_region.split(": ", 1)
                if len(header_parts) != 2:
                    raise InvalidHeader(f"socket returned an invalid header \"{parse_region}\"")
                self.__headers[header_parts[0]] = header_parts[1]


def send_http_message(
        sock: socket.socket,
        status: tuple[str, str, str],
        headers: dict[str, str],
        body: bytes
) -> None:
    data = bytearray()

    if len(status) != 3:
        raise InvalidStatusHeader("status header does not contain the correct number of parts")

    data.extend(status[0].encode("utf-8") + " ".encode("utf-8"))
    data.extend(status[1].encode("utf-8") + " ".encode("utf-8"))
    data.extend(status[2].encode("utf-8") + " ".encode("utf-8"))
    data.extend("\r\n".encode("utf-8"))

    for key, value in headers.items():
        data.extend(key.encode("utf-8") + ": ".encode("utf-8"))
        data.extend(value.encode("utf-8"))
        data.extend("\r\n".encode("utf-8"))

    data.extend("\r\n".encode("utf-8"))

    data.extend(body)

    return sock.sendall(data)
