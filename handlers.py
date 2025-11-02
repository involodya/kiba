import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb

logger = logging.getLogger(__name__)

router = Router()


# FSM состояния для публикации вакансии
class VacancyForm(StatesGroup):
    waiting_for_company_name = State()
    waiting_for_contact = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_salary = State()
    waiting_for_location = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    user = await db.get_user(message.from_user.id)
    
    if user:
        if user['user_type'] == 'company':
            await message.answer(
                f"С возвращением, {user['company_name']}! 👋\n"
                "Выберите действие:",
                reply_markup=kb.get_company_menu()
            )
        else:
            await message.answer(
                "С возвращением! 👋\n"
                "Выберите действие:",
                reply_markup=kb.get_recruiter_menu()
            )
    else:
        await message.answer(
            "Добро пожаловать в платформу найма! 👋\n\n"
            "Выберите, кто вы:",
            reply_markup=kb.get_start_keyboard()
        )
    
    logger.info(f"Пользователь {message.from_user.id} (@{message.from_user.username}) начал работу с ботом")


@router.message(F.text == "👔 Я компания (нанимаю)")
async def register_company(message: Message, state: FSMContext):
    """Регистрация как компания"""
    await message.answer(
        "Отлично! Введите название вашей компании:",
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(VacancyForm.waiting_for_company_name)
    logger.info(f"Пользователь {message.from_user.id} начал регистрацию как компания")


@router.message(VacancyForm.waiting_for_company_name)
async def process_company_name(message: Message, state: FSMContext):
    """Сохранение названия компании"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=kb.get_start_keyboard())
        return
    
    await state.update_data(company_name=message.text)
    await message.answer(
        "Введите ваш контакт для связи (например, @username или телефон):",
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(VacancyForm.waiting_for_contact)


@router.message(VacancyForm.waiting_for_contact)
async def process_company_contact(message: Message, state: FSMContext):
    """Сохранение контакта компании"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=kb.get_start_keyboard())
        return
    
    data = await state.get_data()
    company_name = data['company_name']
    
    await db.save_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        user_type='company',
        company_name=company_name,
        contact=message.text
    )
    
    await state.clear()
    await message.answer(
        f"Регистрация завершена! ✅\n"
        f"Компания: {company_name}\n"
        f"Контакт: {message.text}\n\n"
        "Теперь вы можете публиковать вакансии.",
        reply_markup=kb.get_company_menu()
    )
    logger.info(f"Компания {company_name} (ID: {message.from_user.id}) зарегистрирована")


@router.message(F.text == "🔍 Я рекрутер (ищу вакансии)")
async def register_recruiter(message: Message):
    """Регистрация как рекрутер"""
    await db.save_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        user_type='recruiter'
    )
    
    await message.answer(
        "Вы зарегистрированы как рекрутер! ✅\n"
        "Теперь вы можете просматривать вакансии.",
        reply_markup=kb.get_recruiter_menu()
    )
    logger.info(f"Рекрутер {message.from_user.id} (@{message.from_user.username}) зарегистрирован")


@router.message(F.text == "🔙 Главное меню")
async def main_menu(message: Message, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await cmd_start(message, state)


@router.message(F.text == "➕ Опубликовать вакансию")
async def create_vacancy(message: Message, state: FSMContext):
    """Начало процесса публикации вакансии"""
    user = await db.get_user(message.from_user.id)
    
    if not user or user['user_type'] != 'company':
        await message.answer("Только компании могут публиковать вакансии!")
        return
    
    await message.answer(
        "Давайте создадим новую вакансию! 📝\n\n"
        "Введите название вакансии:",
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(VacancyForm.waiting_for_title)


@router.message(VacancyForm.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    """Обработка названия вакансии"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Создание вакансии отменено.", reply_markup=kb.get_company_menu())
        return
    
    await state.update_data(title=message.text)
    await message.answer(
        "Введите описание вакансии (требования, обязанности):",
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(VacancyForm.waiting_for_description)


@router.message(VacancyForm.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Обработка описания вакансии"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Создание вакансии отменено.", reply_markup=kb.get_company_menu())
        return
    
    await state.update_data(description=message.text)
    await message.answer(
        "Введите зарплату (например: 100,000 - 150,000 руб):",
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(VacancyForm.waiting_for_salary)


@router.message(VacancyForm.waiting_for_salary)
async def process_salary(message: Message, state: FSMContext):
    """Обработка зарплаты"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Создание вакансии отменено.", reply_markup=kb.get_company_menu())
        return
    
    await state.update_data(salary=message.text)
    await message.answer(
        "Введите локацию (город или 'Удаленно'):",
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(VacancyForm.waiting_for_location)


@router.message(VacancyForm.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    """Обработка локации и финальное сохранение вакансии"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Создание вакансии отменено.", reply_markup=kb.get_company_menu())
        return
    
    data = await state.get_data()
    user = await db.get_user(message.from_user.id)
    
    vacancy_id = await db.create_vacancy(
        company_id=message.from_user.id,
        title=data['title'],
        description=data['description'],
        salary=data['salary'],
        location=message.text,
        contact=user['contact']
    )
    
    await state.clear()
    await message.answer(
        f"✅ Вакансия успешно опубликована!\n\n"
        f"📌 {data['title']}\n"
        f"💰 {data['salary']}\n"
        f"📍 {message.text}\n"
        f"📝 {data['description']}\n"
        f"📞 Контакт: {user['contact']}",
        reply_markup=kb.get_company_menu()
    )
    logger.info(f"Вакансия ID {vacancy_id} создана компанией {user['company_name']}")


@router.message(F.text == "📝 Смотреть вакансии")
async def view_vacancies(message: Message):
    """Просмотр вакансий"""
    user = await db.get_user(message.from_user.id)
    
    if not user or user['user_type'] != 'recruiter':
        await message.answer("Только рекрутеры могут просматривать вакансии!")
        return
    
    await show_vacancies_page(message, 0)


async def show_vacancies_page(message: Message, page: int):
    """Отображение страницы с вакансиями"""
    per_page = 1  # Одна вакансия на страницу для удобства
    total_count = await db.get_vacancies_count()
    
    if total_count == 0:
        await message.answer("Пока нет доступных вакансий. 🤷", reply_markup=kb.get_recruiter_menu())
        return
    
    total_pages = (total_count + per_page - 1) // per_page
    
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1
    
    vacancies = await db.get_vacancies(limit=per_page, offset=page * per_page)
    
    if not vacancies:
        await message.answer("Вакансии не найдены.", reply_markup=kb.get_recruiter_menu())
        return
    
    vacancy = vacancies[0]
    text = (
        f"📌 <b>{vacancy['title']}</b>\n\n"
        f"💰 Зарплата: {vacancy['salary']}\n"
        f"📍 Локация: {vacancy['location']}\n\n"
        f"📝 Описание:\n{vacancy['description']}\n\n"
        f"📞 Контакт: {vacancy['contact']}\n\n"
        f"Вакансия {page + 1} из {total_count}"
    )
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=kb.get_pagination_keyboard(page, total_pages)
    )


@router.callback_query(F.data.startswith("page_"))
async def paginate_vacancies(callback: CallbackQuery):
    """Обработка пагинации вакансий"""
    page = int(callback.data.split("_")[1])
    
    per_page = 1
    total_count = await db.get_vacancies_count()
    total_pages = (total_count + per_page - 1) // per_page
    
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1
    
    vacancies = await db.get_vacancies(limit=per_page, offset=page * per_page)
    vacancy = vacancies[0]
    
    text = (
        f"📌 <b>{vacancy['title']}</b>\n\n"
        f"💰 Зарплата: {vacancy['salary']}\n"
        f"📍 Локация: {vacancy['location']}\n\n"
        f"📝 Описание:\n{vacancy['description']}\n\n"
        f"📞 Контакт: {vacancy['contact']}\n\n"
        f"Вакансия {page + 1} из {total_count}"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.get_pagination_keyboard(page, total_pages)
    )
    await callback.answer()


@router.callback_query(F.data == "current_page")
async def current_page_callback(callback: CallbackQuery):
    """Обработка нажатия на текущую страницу"""
    await callback.answer("Вы на этой странице")


@router.callback_query(F.data == "close")
async def close_vacancies(callback: CallbackQuery):
    """Закрытие списка вакансий"""
    await callback.message.delete()
    await callback.answer("Закрыто")


@router.message(F.text == "📋 Мои вакансии")
async def my_vacancies(message: Message):
    """Просмотр собственных вакансий (заглушка)"""
    await message.answer(
        "Функция просмотра ваших вакансий будет добавлена в следующей версии.",
        reply_markup=kb.get_company_menu()
    )


@router.message(F.text == "❌ Отмена")
async def cancel_action(message: Message, state: FSMContext):
    """Универсальная отмена действия"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        user = await db.get_user(message.from_user.id)
        if user and user['user_type'] == 'company':
            await message.answer("Действие отменено.", reply_markup=kb.get_company_menu())
        else:
            await message.answer("Действие отменено.", reply_markup=kb.get_recruiter_menu())
