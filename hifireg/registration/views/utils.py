class LinkButton:
    def __init__(self, link, content=None, attrs=None):
        self.link = link
        self.content = content if content is not None else link
        self.attrs = attrs


class SubmitButton:
    def __init__(self, name, content=None, attrs=None):
        self.name = name
        self.content = content if content is not None else name
        self.attrs = attrs
