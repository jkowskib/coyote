class BodyAlreadyRead(Exception):
    pass

class IncompleteBody(Exception):
    pass

class HeadersAlreadyRead(Exception):
    pass

class HeadersNotSent(Exception):
    pass

class InvalidStatusHeader(Exception):
    pass

class InvalidHeader(Exception):
    pass

class IncorrectRequestType(Exception):
    pass

class MissingRequiredFields(Exception):
    pass
