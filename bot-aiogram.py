from aiogram.dispatcher import FSMContext
from config import BOT_TOKEN
from questionExtractor import Quizzer
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
quizzer = Quizzer()
user_answers = {}


class UserState(StatesGroup):
    waiting_for_language = State()
    waiting_for_genre = State()
    request = State()
    get_desired_effect = State()
    if_des_effect_stay_same = State()
    send_recommendation = State()


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer(text='Добро пожаловать, я - MusicUniverse. Я помогу тебе с выбором музыки для твоего дня! '
                              'Вот команды, которые ты можешь использовать.')
    await message.answer(text='/registration - выбери любимого исполнителя и жанр\n'
                              '/request - выбери исполнителя и песню для прослушивания \n'
                              '/clear_my_data - очистить данные о предпочтениях')



@dp.message_handler(commands='registration')
async def registration(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text='Для того, чтобы мои рекомендации лучше тебе подходили, ответь на следующие вопросы.')
    await question_language(message)
    await UserState.waiting_for_language.set()


async def question_language(message: types.Message):
    language = 'Выбери язык, на котором мне искать для тебя музыку'
    lang_kb = types.InlineKeyboardMarkup(row_width=2)
    lang_bt1 = types.InlineKeyboardButton('Английский', callback_data='english')
    lang_bt2 = types.InlineKeyboardButton('Русский', callback_data='russian')
    lang_kb.add(lang_bt1, lang_bt2)
    await bot.send_message(chat_id=message.chat.id,
                           text=language,
                           reply_markup=lang_kb)


async def question_genre(message: types.Message):
    genre = 'Выбери жанр, который ты бы хотел послушать'
    genre_kb = types.InlineKeyboardMarkup(row_width=3)
    genre_bt1 = types.InlineKeyboardButton('Классика', callback_data='classic')
    genre_bt2 = types.InlineKeyboardButton('Поп', callback_data='pop')
    genre_bt4 = types.InlineKeyboardButton('Рок', callback_data='rock')
    genre_bt6 = types.InlineKeyboardButton('Джаз', callback_data='jazz')
    genre_bt7 = types.InlineKeyboardButton('Lo-Fi', callback_data='lo-fi')
    genre_bt8 = types.InlineKeyboardButton('Рэп', callback_data='rap')
    genre_bt9 = types.InlineKeyboardButton('R&B', callback_data='r&b')
    genre_kb.add(genre_bt1, genre_bt2, genre_bt4, genre_bt6, genre_bt7, genre_bt8, genre_bt9)
    await bot.send_message(chat_id=message.chat.id,
                           text=genre,
                           reply_markup=genre_kb)


@dp.callback_query_handler(state=UserState.waiting_for_language)
async def language_cb(callback: types.CallbackQuery):
    query = str(callback.from_user.username)
    same_username = quizzer.answers.find(query=query)
    if same_username is None:
        quizzer.write_answer_to_result_cell(Username=callback.from_user.username,
                                            AnswerSongLanguage=callback.data,
                                            AnswerSongGenre='',
                                            AnswerSongArtist='')
    else:
        quizzer.answers.update_cell(same_username.row, same_username.col + 1, value=callback.data)
    await question_genre(callback.message)
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await UserState.waiting_for_genre.set()


@dp.callback_query_handler(state=UserState.waiting_for_genre)
async def genre_cb(callback: types.CallbackQuery, state: FSMContext):
    query = str(callback.from_user.username)
    same_username = quizzer.answers.find(query=query)
    if same_username is None:
        quizzer.write_answer_to_result_cell(Username=callback.from_user.username,
                                            AnswerSongLanguage='',
                                            AnswerSongGenre=callback.data,
                                            AnswerSongArtist='')
    else:
        quizzer.answers.update_cell(same_username.row, same_username.col + 2, value=callback.data)
    await bot.delete_message(callback.message.chat.id, callback.message.message_id - 3)
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text='Отлично, теперь мои рекомендации будут лучше тебе подходить.\n'
                                'Когда ты придешь в следующий раз, тебе не придется снова отвечать на эти вопросы, '
                                'просто выбери /request, чтобы снова найти музыку. '
                                'Но ты всегда можешь изменить свои ответы, выбрав /clear_my_data в меню')
    await state.finish()
    start_kb = types.InlineKeyboardMarkup()
    start_bt = types.InlineKeyboardButton('Вперёд!', callback_data='lets_start')
    start_kb.add(start_bt)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text='Начнём?',
                           reply_markup=start_kb)


@dp.message_handler(commands='request')
async def request(message: types.Message):
    await UserState.request.set()
    user_answers[message.from_user.username] = {}
    await mood(message)


async def mood(message: types.Message):
    mood_kb = types.InlineKeyboardMarkup(row_width=2)
    mood_bt1 = types.InlineKeyboardButton('Радостно, воодушевлённо', callback_data='joyfull')
    mood_bt2 = types.InlineKeyboardButton('Грустно, тоскливо', callback_data='sadness')
    mood_bt3 = types.InlineKeyboardButton('Уныло, одиноко', callback_data='nostalgia')
    mood_bt4 = types.InlineKeyboardButton('Романтично, уютно', callback_data='love')
    mood_kb.add(mood_bt1, mood_bt2, mood_bt3, mood_bt4)
    await bot.send_message(message.chat.id, 'Давай определим твоё настроение. Как ты себя чувствуешь?',
                           reply_markup=mood_kb)


async def desired_effect(message: types.Message):
    emo_state_kb = types.InlineKeyboardMarkup(row_width=1)
    emo_state_bt1 = types.InlineKeyboardButton('Хочу остаться в этом состоянии', callback_data='stay_same')
    emo_state_bt2 = types.InlineKeyboardButton('Хочу зарядиться энергией', callback_data='need_energy')
    emo_state_bt3 = types.InlineKeyboardButton('Хочу успокоиться и расслабиться', callback_data='calm_down')
    emo_state_bt4 = types.InlineKeyboardButton('Хочу поднять себе настроение', callback_data='upbeat')
    emo_state_kb.add(emo_state_bt1, emo_state_bt2, emo_state_bt3, emo_state_bt4)
    await bot.send_message(message.chat.id, 'Ты хочешь поддержать это настроение или изменить его',
                           reply_markup=emo_state_kb)


@dp.callback_query_handler(state=UserState.request)
async def mood_cb(callback: types.CallbackQuery):
    user_answers[callback.from_user.username]["mood"] = callback.data
    quizzer.add_answer_to_request_list(Username=callback.from_user.username,
                                       AnswerMood=callback.data,
                                       AnswerDesiredEffect='')
    await desired_effect(callback.message)
    await UserState.get_desired_effect.set()


@dp.callback_query_handler(state=UserState.get_desired_effect)
async def desired_effect_cb(callback: types.CallbackQuery, state: FSMContext):
    quizzer.add_answer_to_request_list(Username=callback.from_user.username,
                                       AnswerMood='',
                                       AnswerDesiredEffect=callback.data)
    if callback.data == 'stay_same':
        await UserState.if_des_effect_stay_same.set()
        await if_des_eff_stay_same(callback, state)
    else:
        user_answers[callback.from_user.username]["des_eff"] = callback.data
        await UserState.send_recommendation.set()
        await send_rcmmndtn(callback, state)


async def get_songs(callback: types.CallbackQuery, filters):
    all_songs = quizzer.songs.get_all_records()  # Получаем все данные из таблицы
    query = str(callback.from_user.username)
    same_username = quizzer.answers.find(query=query, in_column=1)
    if same_username is None:
        await bot.send_message(chat_id=callback.message.chat.id,
                               text="Пользователь не найден в базе данных. Пожалуйста, зарегистрируйся.")
        return
    index = same_username.row
    song_language = quizzer.answers.get(f'B{index}')[0][0]
    song_genre = quizzer.answers.get(f'C{index}')[0][0]
    filtered_songs = []

    for song in all_songs:
        if (song["SongGenre"] == song_genre and
                song["SongLanguage"] == song_language and
                song["DesiredEffect"] == filters["des_eff"]):
            filtered_songs.append(f"{song['SongNameAndArtist']} \n({song['SongLinkSpotify']})")

    return filtered_songs


async def get_songs_stay_same(callback: types.CallbackQuery, filters):
    all_songs = quizzer.songs.get_all_records()  # Получаем все данные из таблицы
    query = str(callback.from_user.username)
    same_username = quizzer.answers.find(query=query, in_column=1)
    if same_username is None:
        await bot.send_message(chat_id=callback.message.chat.id,
                               text="Пользователь не найден в базе данных. Пожалуйста, зарегистрируйся.")
        return
    index = same_username.row
    song_language = quizzer.answers.get(f'B{index}')[0][0]
    song_genre = quizzer.answers.get(f'C{index}')[0][0]
    filtered_songs = []

    for song in all_songs:
        if (song["SongGenre"] == song_genre and
                song["SongLanguage"] == song_language and
                song["SongMood"] == filters["mood"]):
            filtered_songs.append(f"{song['SongNameAndArtist']} \n({song['SongLinkSpotify']})")

    return filtered_songs


async def send_rcmmndtn(callback: types.CallbackQuery, state: FSMContext):
    songs = await get_songs(callback, user_answers[callback.from_user.username])

    if songs:
        response = "Вот подходящие песни:\n" + "\n".join(songs)
        await bot.send_message(chat_id=callback.message.chat.id, text=response, disable_web_page_preview=True)
        await bot.send_message(chat_id=callback.message.chat.id,
                               text='Понравилась рекомендация? Оставь отзыв о моей работе! https://forms.gle/JoiWwk7xNLwNWx6k6',
                               disable_web_page_preview=True)
    await state.finish()


async def if_des_eff_stay_same(callback: types.CallbackQuery, state: FSMContext):
    songs = await get_songs_stay_same(callback, user_answers[callback.from_user.username])

    if songs:
        response = "Вот подходящие песни:\n" + "\n".join(songs)
        await bot.send_message(chat_id=callback.message.chat.id, text=response, disable_web_page_preview=True)
        await bot.send_message(chat_id=callback.message.chat.id,
                               text='Понравилась рекомендация? Оставь отзыв о моей работе! https://forms.gle/JoiWwk7xNLwNWx6k6',
                               disable_web_page_preview=True)
    await state.finish()


@dp.message_handler(commands='clear_my_data')
async def clear_my_data(message: types.Message):
    reply_markup = types.InlineKeyboardMarkup()
    butt1 = types.InlineKeyboardButton('Да', callback_data='yes')
    butt2 = types.InlineKeyboardButton('Нет', callback_data='menu')
    reply_markup.add(butt1, butt2)
    await bot.send_message(message.chat.id, 'Ты уверен, что хочешь очистить свои данные??', reply_markup=reply_markup)


@dp.callback_query_handler()
async def dialog(callback: types.CallbackQuery):
    if callback.data == 'menu':
        await bot.send_message(chat_id=callback.message.chat.id,
                               text='/registration - выбери любимого исполнителя и жанр \n'
                                    '/request - выбери исполнителя и песню для прослушивания \n'
                                    '/choose_playlist - выбери плейлист для прослушивания \n'
                                    '/clear_my_data - очистить данные о предпочтениях')
    if callback.data == 'lets_start':
        await UserState.request.set()
        user_answers[callback.from_user.username] = {}
        await request(callback.message)
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if callback.data == 'yes':
        query = str(callback.from_user.username)
        username = quizzer.answers.find(query=query)
        if username is None:
            await bot.send_message(callback.message.chat.id, 'Ты ещё не прошёл регистрацию. \n'
                                                             'Для того, чтобы зарегистрироваться, введи /registration')
        else:
            quizzer.answers.delete_rows(username.row)
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
            await bot.send_message(callback.message.chat.id,
                                   'Готово! Для того, чтобы снова зарегистрироваться, введи /registration')


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp,
                           skip_updates=True)
