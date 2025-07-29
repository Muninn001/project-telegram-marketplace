from utils.descriptors import PositiveInt

class Order:
    user_id: int = PositiveInt()
    product_id: int = PositiveInt()
    quantity: int = PositiveInt()

    def __init__(self, id: int, user_id: int, product_id: int, quantity: int):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    def to_dict(self) -> dict:
        return {"id": self.id, "user_id": self.user_id, "product_id": self.product_id, "quantity": self.quantity}
