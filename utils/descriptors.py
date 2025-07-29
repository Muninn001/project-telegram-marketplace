class NonEmptyString:
    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name, None)

    def __set__(self, instance, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Поле '{self.name[1:]}' должно быть непустой строкой")
        setattr(instance, self.name, value)

class PositiveInt:
    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name, None)

    def __set__(self, instance, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"Поле '{self.name[1:]}' должно быть положительным целым числом")
        setattr(instance, self.name, value)

class PositiveFloat:
    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name, None)

    def __set__(self, instance, value):
        if not (isinstance(value, float) or isinstance(value, int)) or value <= 0:
            raise ValueError(f"Поле '{self.name[1:]}' должно быть положительным числом")
        setattr(instance, self.name, float(value))

class NonNegativeInt:
    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name, None)

    def __set__(self, instance, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Поле '{self.name[1:]}' должно быть неотрицательным целым числом")
        setattr(instance, self.name, value)