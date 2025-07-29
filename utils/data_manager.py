import json
from typing import List
from utils.patterns import SingletonMeta, Subject, LogObserver, OrderFactory
from models.product import Product, Book, Electronics, Clothing  # Импортируем все типы продуктов
from models.order import Order

class DataManager(metaclass=SingletonMeta):
    def __init__(self):
        self._items_file = "data/items.json"
        self._orders_file = "data/orders.json"
        self.products: List[Product] = []
        self.orders: List[Order] = []

        self.order_subject = Subject()
        self.order_subject.register(LogObserver())
        self._load_products()
        self._load_orders()

    def _load_products(self) -> None:
        try:
            with open(self._items_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.products = [self._deserialize_product(item) for item in data]
        except FileNotFoundError:
            self.products = []

    def _load_orders(self) -> None:
        try:
            with open(self._orders_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.orders = [Order(**item) for item in data]
        except FileNotFoundError:
            self.orders = []

    def save_products(self) -> None:
        with open(self._items_file, "w", encoding="utf-8") as file:
            json.dump([p.to_dict() for p in self.products], file, ensure_ascii=False, indent=4)

    def save_orders(self) -> None:
        with open(self._orders_file, "w", encoding="utf-8") as file:
            json.dump([o.to_dict() for o in self.orders], file, ensure_ascii=False, indent=4)

    def get_products(self) -> List[Product]:
        return self.products

    def add_book(self, name: str, price: float, quantity: int, author: str) -> Book:
        new_id = max([p.id for p in self.products], default=0) + 1
        product = Book(new_id, name, price, quantity, author)
        self.products.append(product)
        self.save_products()
        return product

    def add_electronics(self, name: str, price: float, quantity: int, warranty_period: int) -> Electronics:
        new_id = max([p.id for p in self.products], default=0) + 1
        product = Electronics(new_id, name, price, quantity, warranty_period)
        self.products.append(product)
        self.save_products()
        return product

    def add_clothing(self, name: str, price: float, quantity: int, size: str) -> Clothing:
        new_id = max([p.id for p in self.products], default=0) + 1
        product = Clothing(new_id, name, price, quantity, size)
        self.products.append(product)
        self.save_products()
        return product

    def add_other(self, name: str, price: float, quantity: int) -> Product:
        new_id = max([p.id for p in self.products], default=0) + 1
        product = Product(new_id, name, price, quantity)
        self.products.append(product)
        self.save_products()
        return product

    def create_order(self, user_id: int, product_id: int, quantity: int) -> Order:
        product = next((p for p in self.products if p.id == product_id), None)
        if not product:
            raise ValueError("Товар не найден")
        if product.quantity < quantity:
            raise ValueError("Недостаточно товара на складе")
        new_id = max([o.id for o in self.orders], default=0) + 1
        order = OrderFactory.create_order(new_id, user_id, product_id, quantity)
        self.orders.append(order)

        product.quantity -= quantity
        self.save_orders()
        self.save_products()

        self.order_subject.notify(f"Новый заказ: {order.to_dict()}")
        return order

    @staticmethod
    def _deserialize_product(data: dict) -> Product:
        """Десериализация продукта в зависимости от типа."""
        product_type = data.pop("type", "other")  # Извлекаем и удаляем поле "type"
        if product_type == "book":
            return Book(**data)
        elif product_type == "electronics":
            return Electronics(**data)
        elif product_type == "clothing":
            return Clothing(**data)
        else:
            return Product(**data)