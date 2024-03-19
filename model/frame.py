class Frame:
    def __init__(self, id, title):
        self.id = id
        self.title = title
        

    def __repr__(self):
        return f"Frame(id='{self.id}', title='{self.title}')"