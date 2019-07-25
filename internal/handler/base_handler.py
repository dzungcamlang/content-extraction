class BaseHandler():
    _text_styles = {}

    def _get_style(self, path=''):
        if path not in self._text_styles:
            return None
        return self._text_styles[path]

    def _set_style(self, path='', val={}):
        self._text_styles[path] = val


class singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(object):
    __metaclass__ = singleton

    records = {}
