class Inventory:
    def __init__(self):
        self.items = []
        self.max_slots = 20

    def add_item(self, item):
        if len(self.items) < self.max_slots:
            self.items.append(item)
            return True
        return False

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def has_item(self, item, amount=1):
        return self.items.count(item) >= amount
