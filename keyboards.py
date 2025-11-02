from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_start_keyboard():
    """Клавиатура выбора роли при старте"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👔 Я компания (нанимаю)")],
            [KeyboardButton(text="🔍 Я рекрутер (ищу вакансии)")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_company_menu():
    """Меню для компаний"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Опубликовать вакансию")],
            [KeyboardButton(text="📋 Мои вакансии")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_recruiter_menu():
    """Меню для рекрутеров"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Смотреть вакансии")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_cancel_keyboard():
    """Клавиатура отмены"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )
    return keyboard


def get_pagination_keyboard(current_page: int, total_pages: int):
    """Клавиатура пагинации для листания вакансий"""
    buttons = []
    
    # Кнопки навигации
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{current_page - 1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"{current_page + 1}/{total_pages}", callback_data="current_page"))
    
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page_{current_page + 1}"))
    
    buttons.append(nav_buttons)
    
    # Кнопка закрытия
    buttons.append([InlineKeyboardButton(text="✖️ Закрыть", callback_data="close")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
