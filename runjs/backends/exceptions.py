class JSException(Exception):
    """Base exception for javascript engine wrapper."""

    pass


class ArgumentError(JSException):
    pass


class JSFunctionNotExists(JSException):
    pass


class JSRuntimeException(JSException):
    """Javascript runtime exception with a stacktrace."""

    def __init__(self, msg, traceback):
        self.msg = msg
        self.traceback = traceback
        super().__init__()


class JSConversionException(JSException):
    """Exception on converting a javascript type to/from python type."""

    pass
