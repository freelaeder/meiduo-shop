from django.urls import converters


class UsernameConverter:
    """
    再次验证用户输入的名字
    """
    regex = '[a-zA-Z0-9_-]{5,20}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return str(value)
