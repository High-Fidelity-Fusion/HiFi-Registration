
class LinkButton:
    def __init__(self, content, link, attrs=None):
        self.content = content
        self.link = link
        self.attrs = None

class SubmitButton:
    def __init__(self, content, name=None, attrs=None):
        self.content = content
        self.attrs = None
        if name is None:
            self.name = content.lower()
        else:
            self.name = name
