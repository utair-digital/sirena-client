class BaseError(Exception):
    http_code = None
    error_code = None
    message = None
    internal_message = None

    def __init__(self, message=None, error_code=None, http_code=None, internal_message=None):
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        self.http_code = http_code or self.http_code
        self.internal_message = internal_message or self.internal_message

        assert self.message, 'Message not implemented!'
        assert self.error_code, 'Error code not implemented!'
        assert self.http_code, 'Http code not implemented!'

        super(BaseError, self).__init__(message)

    def __str__(self):
        '''Текстовое представление'''
        base = f'{self.http_code}:{self.error_code}: {self.message}'
        if self.internal_message:
            return '{0} {{{1}}}'.format(base, self.internal_message)
        return base
