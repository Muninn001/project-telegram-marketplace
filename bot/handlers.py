from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from loguru import logger

from config import config
from utils.data_manager import DataManager
from bot.states import OrderStates, AddProductStates

# Создаем роутер
router = Router()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    text = "Добро пожаловать в Marketplace Bot!\n"
    text += "Доступные команды:\n"
    text += "/browse - просмотреть список товаров\n"
    if message.from_user.id in config.admin_id:
        text += "/add - добавить новый товар (только для админа)\n"
    await message.reply(text)
    logger.info(f"Пользователь {message.from_user.id} вызвал /start")

# Обработчик команды /browse
@router.message(Command("browse"))
async def cmd_browse(message: Message, state: FSMContext):
    data_manager = DataManager()
    products = data_manager.get_products()

    # Если товаров нет
    if not products:
        await message.reply("Список товаров пуст.")
        return

    # Выводим список товаров
    text = "Текущие товары:\n"
    for product in products:
        text += f"{product.id}. {product.name} - {product.price} руб. (в наличии: {product.quantity})\n"
    await message.reply(text)

    # Запрашиваем ID товара
    await message.reply("Введите ID товара, который хотите купить:")
    await state.set_state(OrderStates.choosing_product)  # Устанавливаем состояние выбора товара
    logger.info(f"Пользователь {message.from_user.id} просматривает товары")

# Обработчик команды /add
@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    if message.from_user.id not in config.admin_id:
        await message.reply("У вас нет прав на добавление товаров.")
        return
    await message.reply(
        "Выберите тип товара:\n"
        "1. Книга\n"
        "2. Электроника\n"
        "3. Одежда\n"
        "4. Другое"
    )
    await state.set_state(AddProductStates.waiting_type)
    logger.info(f"Администратор {message.from_user.id} начал добавление товара")

# Обработчик выбора типа товара
@router.message(StateFilter(AddProductStates.waiting_type))
async def add_product_type(message: Message, state: FSMContext):
    product_type = message.text.strip()
    if product_type not in ["1", "2", "3", "4"]:
        await message.reply("Неверный выбор. Пожалуйста, введите 1, 2, 3 или 4.")
        return

    await state.update_data(product_type=product_type)
    await message.reply("Введите название нового товара:")
    await state.set_state(AddProductStates.waiting_name)

# Обработчик добавления названия товара
@router.message(StateFilter(AddProductStates.waiting_name))
async def add_name(message: Message, state: FSMContext):
    if not message.text.strip():
        await message.reply("Название товара не может быть пустым. Попробуйте снова.")
        return
    await state.update_data(name=message.text)
    await message.reply("Введите цену товара:")
    await state.set_state(AddProductStates.waiting_price)

# Обработчик добавления цены товара
@router.message(StateFilter(AddProductStates.waiting_price))
async def add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError("Цена должна быть положительным числом.")
    except ValueError:
        await message.reply("Цена должна быть положительным числом. Попробуйте снова.")
        return
    await state.update_data(price=price)
    await message.reply("Введите количество товара:")
    await state.set_state(AddProductStates.waiting_quantity)

# Обработчик добавления количества товара
@router.message(StateFilter(AddProductStates.waiting_quantity))
async def add_quantity(message: Message, state: FSMContext):
    data = await state.get_data()
    product_type = data.get("product_type")

    try:
        quantity = int(message.text)
        if quantity < 0:
            raise ValueError("Количество должно быть неотрицательным целым числом.")
    except ValueError:
        await message.reply("Количество должно быть неотрицательным целым числом. Попробуйте снова.")
        return

    await state.update_data(quantity=quantity)

    # Если тип товара "Другое", завершаем добавление
    if product_type == "4":
        await finalize_product(message, state)
    else:
        await add_specific_fields(message, state)

# Обработчик добавления специфических полей
async def add_specific_fields(message: Message, state: FSMContext):
    data = await state.get_data()
    product_type = data.get("product_type")

    if product_type == "1":  # Книга
        await message.reply("Введите автора книги:")
    elif product_type == "2":  # Электроника
        await message.reply("Введите срок гарантии (в месяцах):")
    elif product_type == "3":  # Одежда
        await message.reply("Введите размер одежды:")

    await state.set_state(AddProductStates.waiting_specific_field)

# Обработчик завершения добавления товара
@router.message(StateFilter(AddProductStates.waiting_specific_field))
async def finalize_product(message: Message, state: FSMContext):
    data_manager = DataManager()
    data = await state.get_data()
    product_type = data.get("product_type")
    name = data.get("name")
    price = data.get("price")
    quantity = data.get("quantity")
    specific_field = message.text.strip()

    # Создаем товар в зависимости от типа
    if product_type == "1":  # Книга
        product = data_manager.add_book(name, price, quantity, specific_field)
    elif product_type == "2":  # Электроника
        try:
            warranty_period = int(specific_field)
            if warranty_period < 0:
                raise ValueError("Срок гарантии должен быть неотрицательным.")
        except ValueError:
            await message.reply("Срок гарантии должен быть неотрицательным числом. Попробуйте снова.")
            return
        product = data_manager.add_electronics(name, price, quantity, warranty_period)
    elif product_type == "3":  # Одежда
        product = data_manager.add_clothing(name, price, quantity, specific_field)
    else:  # Другое
        product = data_manager.add_other(name, price, quantity)

    await message.reply(f"Товар '{product.name}' добавлен с ID {product.id}.", reply_markup=None)
    await state.clear()
    logger.info(f"Администратор добавил товар {product.id}")

# Обработчик команды /cancel
@router.message(Command("cancel"), StateFilter("*"))
async def cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.reply("Действие отменено.", reply_markup=ReplyKeyboardRemove())
        logger.info(f"Пользователь {message.from_user.id} отменил действие")

# Обработчик выбора товара
@router.message(StateFilter(OrderStates.choosing_product))
async def process_product_id(message: Message, state: FSMContext):
    data_manager = DataManager()
    try:
        product_id = int(message.text)
    except ValueError:
        await message.reply("ID должен быть числом. Пожалуйста, попробуйте снова.")
        return

    # Поиск товара по ID
    product = next((p for p in data_manager.get_products() if p.id == product_id), None)
    if not product:
        await message.reply("Товар с таким ID не найден. Попробуйте снова.")
        return

    # Проверка наличия товара
    if product.quantity == 0:
        await message.reply("Извините, товар закончился.")
        return

    # Сохраняем ID товара в состоянии
    await state.update_data(product_id=product_id)
    await message.reply(f"Сколько штук товара '{product.name}' вы хотите купить?")
    await state.set_state(OrderStates.choosing_quantity)  # Переходим к выбору количества
    logger.info(f"Пользователь {message.from_user.id} выбрал товар {product_id}")

# Обработчик выбора количества
@router.message(StateFilter(OrderStates.choosing_quantity))
async def process_quantity(message: Message, state: FSMContext):
    data_manager = DataManager()
    data = await state.get_data()
    product_id = data.get("product_id")
    try:
        quantity = int(message.text)
    except ValueError:
        await message.reply("Количество должно быть числом. Попробуйте снова.")
        return
    product = next((p for p in data_manager.get_products() if p.id == product_id), None)
    if not product:
        await message.reply("Ошибка: товар не найден.")
        await state.clear()  # Очищаем состояние
        return
    if quantity <= 0:
        await message.reply("Количество должно быть положительным.")
        return
    if quantity > product.quantity:
        await message.reply(f"Максимальное количество доступно: {product.quantity}. Введите меньшее число.")
        return
    order = data_manager.create_order(message.from_user.id, product_id, quantity)
    await message.reply(f"Заказ #{order.id} создан! Спасибо за покупку.", reply_markup=ReplyKeyboardRemove())
    await state.clear()  # Очищаем состояние
    logger.info(f"Пользователь {message.from_user.id} создал заказ {order.id}")