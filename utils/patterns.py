from loguru import logger # type: ignore

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Observer:
    def update(self, message: str):
        raise NotImplementedError()

class Subject:

    def __init__(self):
        self._observers = []

    def register(self, observer: Observer) -> None:

        self._observers.append(observer)

    def notify(self, message: str) -> None:

        for observer in self._observers:
            observer.update(message)

class LogObserver(Observer):
    def update(self, message: str):
        logger.info(message)

class ProductFactory:

    @staticmethod
    def create_product(id: int, name: str, price: float, quantity: int):
        from models.product import Product
        return Product(id, name, price, quantity)

class OrderFactory:
    @staticmethod
    def create_order(id: int, user_id: int, product_id: int, quantity: int):
        from models.order import Order
        return Order(id, user_id, product_id, quantity)
