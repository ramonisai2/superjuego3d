"""Compatibilidad para el inventario antiguo.

El runtime actual usa el inventario por cantidades en ``game.player.Player``.
Esta clase queda como adaptador minimo para herramientas viejas que importen
``Inventory`` directamente.
"""


class Inventory:
    def __init__(self, max_slots=20):
        self.max_slots = int(max_slots)
        self.items = {}

    def add_item(self, item, amount=1):
        item = str(item)
        amount = max(1, int(amount))
        if self.used_slots() + amount > self.max_slots:
            return False
        self.items[item] = int(self.items.get(item, 0)) + amount
        return True

    def remove_item(self, item, amount=1):
        item = str(item)
        amount = max(1, int(amount))
        if not self.has_item(item, amount):
            return False
        self.items[item] = int(self.items.get(item, 0)) - amount
        if self.items[item] <= 0:
            self.items.pop(item, None)
        return True

    def has_item(self, item, amount=1):
        return int(self.items.get(str(item), 0)) >= max(1, int(amount))

    def used_slots(self):
        return sum(max(0, int(amount)) for amount in self.items.values())
