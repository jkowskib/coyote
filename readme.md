# Coyote
A pure Python implementation on an HTTP/1.1 server and client parts

### Goal
To create a pure Python implementation of both HTTP requests and responses to
have a good starting point for developing web servers, proxys and more.

> Important to note this only implements raw sockets, interfaces for listening for
> requests or creating routes is not included. That must be implemented by you but
> reading and writing requests and responses is complete in Coyote.

### Features
- Request object
- Response object
- Streamed body content
- Streamed HTTP parsing for better performance