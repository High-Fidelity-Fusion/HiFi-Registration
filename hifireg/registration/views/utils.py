
class LinkButton:
    def __init__(self, text, link):
        self.text = text
        self.link = link

class SubmitButton:
    def __init__(self, text, name=None):
        self.text = text
        if name is None:
            self.name = text.lower()
        else:
            self.name = name