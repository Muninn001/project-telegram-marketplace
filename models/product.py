from utils.descriptors import NonEmptyString, PositiveFloat, NonNegativeInt

class Product:
    name: str = NonEmptyString()
    price: float = PositiveFloat()
    quantity: int = NonNegativeInt()

    def __init__(self, id: int, name: str, price: float, quantity: int):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "type": "other"  # Базовый тип
        }


class Book(Product):
    author: str = NonEmptyString()

    def __init__(self, id: int, name: str, price: float, quantity: int, author: str):
        super().__init__(id, name, price, quantity)
        self.author = author

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({"author": self.author, "type": "book"})
        return base_dict


class Electronics(Product):
    warranty_period: int = NonNegativeInt()

    def __init__(self, id: int, name: str, price: float, quantity: int, warranty_period: int):
        super().__init__(id, name, price, quantity)
        self.warranty_period = warranty_period

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({"warranty_period": self.warranty_period, "type": "electronics"})
        return base_dict


class Clothing(Product):
    size: str = NonEmptyString()

    def __init__(self, id: int, name: str, price: float, quantity: int, size: str):
        super().__init__(id, name, price, quantity)
        self.size = size

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({"size": self.size, "type": "clothing"})
        return base_dict