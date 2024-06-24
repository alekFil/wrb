from datetime import datetime, timedelta

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


def upcase_first_letter(s):
    return s[0].upper() + s[1:]


class ChooseParams(StatesGroup):
    start = State()
    get_tasks = State()
    game = State()


@router.message(StateFilter(None), Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    intro = (
        "<b>Добро пожаловать в бота Work and Rest!</b>\n"
        "Для дальнейшей работы нажмите кнопку загрузки задач"
    )

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Загрузить задачи",
        callback_data="tasks__")
    )
    builder.adjust(1)

    await message.answer(
        text=intro,
        reply_markup=builder.as_markup()
    )

    await state.set_state(ChooseParams.start)


@router.callback_query(ChooseParams.start, F.data.startswith("tasks__"))
async def price_chosen(callback: types.CallbackQuery, state: FSMContext):
    instruction = (
        "Ок, загружаем задачи.\n"
        "Пришлите мне сообщение с перечислением задач, которые Вы будете "
        "отслеживать сегодня, через запятую. Жду Вашего сообщения"
    )

    await callback.message.edit_text(text=instruction)
    await state.set_state(ChooseParams.get_tasks)
    await callback.answer()


@router.message(ChooseParams.get_tasks, F.text)
async def echo(message: Message, state: FSMContext):

    tasks = map(str.strip, message.text.split(','))
    tasks = map(upcase_first_letter, tasks)

    zero = timedelta()

    dict_tasks = {idx: ele for idx, ele in enumerate(tasks)}
    time_tasks = {idx: zero for idx in range(0, len(dict_tasks))}

    builder = InlineKeyboardBuilder()
    for elem in dict_tasks:
        builder.add(types.InlineKeyboardButton(
            text=upcase_first_letter(dict_tasks[elem]),
            callback_data="start_task__" + str(elem) + '__0')
        )

    builder.add(types.InlineKeyboardButton(
        text="Завершить",
        callback_data="stop__")
    )
    builder.adjust(1)

    await message.answer(
        text='Начнем игру! Нажмите на задачу, которую сейчас начинаете '
             'выполнять',
        reply_markup=builder.as_markup()
    )

    await state.update_data(tasks=dict_tasks)
    await state.update_data(time_tasks=time_tasks)
    await state.update_data(time_last_task=None)
    await state.update_data(last_task=None)
    await state.set_state(ChooseParams.game)


@router.callback_query(ChooseParams.game, F.data.startswith("start_task__"))
async def price_chosen(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    tasks = user_data['tasks']
    time_tasks = user_data['time_tasks']
    last_task = user_data['last_task']
    time_last_task = user_data['time_last_task']
    action = callback.data.split("__")[1]

    now_time = datetime.now()

    if time_last_task is not None:
        delta_last_task = now_time - time_last_task
        time_tasks[int(last_task)] += delta_last_task

    now_time_text = (
        '{0:%d} {0:%b} {0:%Y} at {0:%H}-{0:%M}'
        .format(now_time)
    )

    time_text = ''
    for elem in time_tasks:
        time_text = (
                time_text + '\n' +
                tasks[elem][:7] + '...' + ' - ' +
                str(time_tasks[elem]).split('.', 2)[0]
        )

    game_text = (
        f"Текущая задача:\n"
        f"{tasks[int(action)][:15]+'...'}\n"
        f"Начало ее выполнения \n"
        f" - {now_time_text}.\n\n"
        f"Накопленное время выполнения (часы:минуты:секунды):"
        f"{time_text}"
    )

    builder = InlineKeyboardBuilder()
    for elem in tasks:
        text = upcase_first_letter(tasks[elem])
        if str(elem) == action:
            text = '[Активно] ' + text
        builder.add(types.InlineKeyboardButton(
            text=text,
            callback_data='start_task__' + str(elem))
        )
    builder.add(types.InlineKeyboardButton(
        text="Завершить",
        callback_data="stop__")
    )
    builder.adjust(1)

    await callback.message.edit_text(text=game_text,
                                     reply_markup=builder.as_markup())
    await state.update_data(last_task=action)
    await state.update_data(time_last_task=now_time)
    await callback.answer()


@router.message(ChooseParams.start, F.text)
async def echo(message: Message):
    understand = (
        "Я Вас не понимаю, для дальнейшей работы нажмите 'Загрузить задачи' "
        "и следуйте инструкциям выше."
    )

    await message.answer(text=understand)


@router.message(StateFilter(None), F.text)
async def echo(message: Message):
    understand = (
        "Я Вас не понимаю, для дальнейшей работы нажмите /start"
    )

    await message.answer(text=understand)


@router.message(F.text)
async def echo(message: Message):
    understand = (
        'Таймер уже запущен, используйте его'
    )

    await message.answer(text=understand)


@router.callback_query(F.data.startswith("stop__"))
async def stop(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    # exception KeyError: 'tasks'
    tasks = user_data['tasks']
    time_tasks = user_data['time_tasks']

    time_text = ''
    for elem in time_tasks:
        time_text = (
                time_text + '\n' +
                tasks[elem][:7] + '...' + ' - ' +
                str(time_tasks[elem]).split('.', 2)[0]
        )

    remember = (
        f"Накопленное время выполнения (часы:минуты:секунды):"
        f"{time_text}"
        f"\n"
        f"Сохранено " + '{0:%d} {0:%b} {0:%Y}'
        .format(datetime.now())
    )

    stop_text = (
        "<b>Таймер остановлен!</b>\n"
        "Для перезапуска нажмите /start"
    )

    await callback.message.edit_text(text=remember, reply_markup=None)
    await callback.message.answer(text=stop_text, reply_markup=None)
    await state.clear()
    await callback.answer()
