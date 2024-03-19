class Board:
    def __init__(self, id, type, name, description, createdAt, createdBy):
        self.id = id
        self.type = type
        self.name = name
        self.description = description
        self.createdAt = createdAt
        # createdBy é esperado ser um dicionário com 'id', 'type', e 'name'
        self.createdBy = createdBy

    def __repr__(self):
        return f"Board(id='{self.id}', type='{self.type}', name='{self.name}', description='{self.description}', createdAt='{self.createdAt}', createdBy={self.createdBy})"