from flask import Flask, request, jsonify
from random import randint

STATE_RQUEST_KEY = 'session'
STATE_RESPONS_KEY = 'session_state'

app = Flask(__name__)


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    return jsonify(handler(request.json, response))


def say_hello():
    var = randint(0, 2)
    hello_text = [
        'Привет, ты готов к новому приключению?',
        'Привет, готов ли ты стать героем и покарать древнее зло?',
        'Привет, отправляемся спасать мир?',
    ]
    return hello_text[var]


def say_goodbye():
    var = randint(0, 4)
    goodbye_text = [
        'Тогда, довстречи!',
        'Как хочешь, пока-пока!',
        'Ладно, твоё право, возращайся поскорее!',
        'Ладно, сыграем в другой раз!',
        'Как хочешь, прощай!',
    ]
    return goodbye_text[var]


def say_help():
    help_text = "После выбора персонажа, война, лучника или мага" + \
                " вы можете пройти их сюжетную линию, для этого " + \
                " вам требуется внимательно вслушиваться или вчитываться в предложенные" + \
                " Алисой варианты действий." + \
                " На благоприятный исход вашего выбора, также влияют атрибуты" + \
                " вашего персонажа." + \
                " Вы можете поинтересоваться своими атрибутами, для этого" + \
                ' скажите Алисе "Покажи мои атрибуты".'
    return help_text


def end_work(text, event):
    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            'text': text,
            'end_session': 'true'
        },
    }


def create_hero():
    text = "Тогда, скажи мне кто-ты? Воин, Лучник или Маг?"
    return text


def show_atributs(mas):
    hp, power, agility, mind = tuple(mas)
    text = "\n".join(["Здоровье: " + str(hp), "Сила: " + str(power), "Ловкость: " + str(agility),
                      "Интелект: " + str(mind)])
    return text


def make_fight(n, m):
    if n + randint(0, n) // 4 >= m:
        return True
    return False


def make_response(text, tts=None, card=None, state=None, buttons=None):
    resposne = {
        'text': text,
        'tts': tts if tts is not None else text,
    }
    if card is not None:
        resposne['card'] = card
    webhook_response = {
        'response': resposne,
        'version': '1.0',
        'end_session': 'false'
    }
    if state is not None:
        webhook_response[STATE_RESPONS_KEY] = state
    if buttons:
        resposne['buttons'] = buttons
    return webhook_response


def button(title, payload=None, url=None, hide=False):
    button = {
        'title': title,
        'hide': hide
    }
    if payload is not None:
        button['payload'] = payload
    if url is not None:
        button['url'] = url
    return button


def handler(event, context):
    text = say_hello()
    atr = [0, 0, 0, 0]  # atr - атрибуты
    type_hero = "None"
    old_location = 0
    if 'request' in event and \
            'original_utterance' in event['request'] \
            and len(event['request']['original_utterance']) > 0:
        state = event.get('state').get(STATE_RQUEST_KEY, {})
        intents = event['request'].get('nlu', {}).get('intents')
        location = state.get('location')
        atr = state.get("atr")
        type_hero = state.get("type_hero")
        old_location = state.get('old_location')
        user_message = "".join(str(event['request']['original_utterance']).split("."))
        main_baff = []
        max_hp = 50
        debaf = False
        try:
            debaf = state.get('debaf')
        except Exception:
            pass
        false_flag = True
        try:
            false_flag = state.get('false_flag')
        except Exception:
            pass
        if 'gooodbye' in intents:
            text = say_goodbye()
            return end_work(text, event)
        if not false_flag:
            if user_message == 'Нет' or 'No' in intents:
                text = say_goodbye()
                return end_work(text, event)
        if user_message == "Помощь" or 'Help' in intents:
            text = say_help() + "\n" + \
                   "Хотите ли вы продолжить путешествие?"
            if false_flag:
                location, old_location = old_location, location
            return make_response(text, state={'location': old_location, 'type_hero': 'archer', 'atr': atr,
                                              'old_location': location, 'debaf': debaf, 'false_flag': False},
                                 buttons=[
                                     button('Продолжить путешествие', hide=True),
                                 ])
        if user_message == "Покажи мои атрибуты" or 'show_atr' in intents:
            text = show_atributs(atr) + "\n" + \
                   "Хотите ли вы продолжить путешествие?"
            if false_flag:
                location, old_location = old_location, location
            return make_response(text, state={'location': old_location, 'type_hero': 'archer', 'atr': atr,
                                              'old_location': location, 'debaf': debaf, 'false_flag': False},
                                 buttons=[
                                     button('Продолжить путешествие', hide=True),
                                 ])
        if location == 0:
            if user_message == 'Да' or 'Yes' in intents:
                text = create_hero()
                return make_response(text, state={'location': 1, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location},
                                     buttons=[
                                         button('Воин', hide=True),
                                         button('Лучник', hide=True),
                                         button('Маг', hide=True)
                                     ])
            else:
                text = say_goodbye()
                return end_work(text, event)
        if location == 1:
            if user_message == "Маг":
                atr = [50, 10, 10, 20]
                text = "Отлично! Вот ваши атрибуты:" + "\n" + show_atributs(atr)
                return make_response(text,
                                     state={'location': 70, 'type_hero': 'wizard', 'atr': atr, 'old_location': location},
                                     buttons=[
                                         button('Отправиться в путь', hide=True),
                                     ])
            if user_message == "Лучник" or old_location == 31:
                atr = [50, 10, 20, 10]
                text = "Отлично! Вот ваши атрибуты:" + "\n" + show_atributs(atr)
                return make_response(text, state={'location': 31, 'type_hero': 'archer', 'atr': atr,
                                                  'old_location': location},
                                     buttons=[
                                         button('Отправиться в путь', hide=True),
                                     ])
            if user_message == "Воин":
                atr = [50, 20, 10, 10]
                text = "Отлично! Вот ваши атрибуты:" + "\n" + show_atributs(atr)
                return make_response(text, state={'location': 2, 'type_hero': 'warrior', 'atr': atr,
                                                  'old_location': location},
                                     buttons=[
                                         button('Отправиться в путь', hide=True),
                                     ])
        if location == 70:
            text = "Ваше путешествие начинается в тихом горном городке Прехевилль." \
                   "Преххевиль стал известен на весь мир в первую очередь как образовательный и научный центр," \
                   "поскольку именно здесь был построен Харлондский университет магии." \
                   "Вы можете передохнуть в трактире, или направиться в Харлондский университет."

            return make_response(text, state={'location': 71, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Отправиться в Харлондский университет', hide=True),
                button('Отправиться в трактир', hide=True),
            ])
        if location == 71:
            if user_message == 'Отправиться в трактир':
                text = "Вы решаете пойти в трактир." \
                       "В трактире вас встречает шум разговоров, чей-то смех, запах еды и выпивки." \
                       "Вечером в таких местах всегда много народу." \
                       "Вы решаете поговорить с трактирщиком." \
                       "- Добро пожаловать, путник. Не желаете чего нибудь? Еда, выпивка или снять комнату??"
                return make_response(text, state={'location': 73, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Спросить о последних новостях', hide=True),
                    button('Уйти', hide=True),
                ])
            if user_message == 'Отправиться в Харлондский университет':
                text = "Вы отправляетесь в Харлондский университет, где вам разрешают посетить их библиотеку. " \
                       "Вы решаете провести время за чтением. Какую книгу выберете?"
                return make_response(text, state={'location': 72, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Записки плута', hide=True),
                    button('Путь гнева', hide=True),
                    button('Ловкость ума', hide=True)
                ])
        if location == 72:
            if user_message == 'Записки плута':
                text = 'Ваша ловкость повышена на 3 очка'
            if user_message == 'Путь гнева':
                text = 'Ваша сила повышена на 3 очка'
            if user_message == 'Ловкость ума':
                text = "Ваш интеллект повышен на 3 очка."
            return make_response(text, state={'location': 73, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Уйти', hide=True),
                button('Отправиться в трактир', hide=True)
            ])
        if location == 73:
            if user_message == 'Спросить о последних новостях':
                text = "- Да какие тут новости? Пару пьных драк, да мелкие кражи." \
                       "Город у нас тихий, событий почти нет." \
                       "Хотя недавно один фермер утверждал, что видел какие-то огни в пещерах, мол призраки ходят." \
                       "Да только не верит ему никто, преукрасить да приврать он горазд, так ещё и пьяница."
                return make_response(text, state={'location': 74, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Спросить о пещерах', hide=True),
                    button('Уйти', hide=True),
                ])
            if user_message == 'Уйти':
                text = "День подходит к концу, и вы решаете закончить ваши дела на сегодня."
                return make_response(text, state={'location': 75, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Завершить день', hide=True),
                ])
        if location == 74:
            if user_message == 'Спросить о гротах':
                text = "- Вокруг этих пещер много всяких историй и легенд ходит." \
                       "Дело в том, что там находятся вякие древние гробницы, да святилища" \
                       "Вот и видят там призраков и прочую нечисть." \
                       "Есть ещё одна легенда о Цветке Зла. Говорят, что растёт такой в одной из пещер, " \
                       "и что серцевина его - волшебный камень, способный сделать кого угодно могущественным. " \
                       "Но при этом человек очень злым становиться."
                return make_response(text, state={'location': 75, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Завершить день', hide=True),
                    button('Отправиться в Харлондский университет', hide=True)
                ])
            if user_message == 'Уйти':
                text = "День подходит к концу, и вы решаете закончить ваши дела на сегодня."
                return make_response(text, state={'location': 75, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Завершить день', hide=True),
                ])
        if location == 75:
            if user_message == 'Завершить день':
                text = "День закончился и город затих. Ночью случился настоящий переполох. " \
                       "На город напала восставшая нежить." \
                       "Стража города отбивалась изо всех сил и под утро им удалось очистить город." \
                       "Жители города в ужасе. Предположительно,мертвецы полезли из древних захоронений в пещерах," \
                       "но, несмотря на щедрую оплату, никто не решался спуститься в подземелья, " \
                       "чтобы успокоить мёртвых и найти причину их восстания." \
                       "Вы вызыватесть добровольцем. Перед спуском в подземелья, " \
                       "вы решаете сходить на рынок и подготовиться. Чем запасётесь?"
                return make_response(text, state={'location': 75, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Едой', hide=True),
                    button('Лекарствами', hide=True),
                    button('Магическими артефактами', hide=True),
                ])
        if location == 75:
            if user_message == 'Лекарствами':
                text = "Вы приобрели зелье лечения." \
                       "Теперь вы чувствуете, что готовы к тому, что ждёт вас в подземельях."
                main_baff.append('зелье лечения')
            if user_message == 'Магическими артефактами':
                text = "Вы приобрели кулон Скрытого глаза. Ваша ловкость повышена на 5 очков." \
                       "Теперь вы чувствуете, что готовы к тому, что ждёт вас в подземельях."
                atr[2] += 5
            if user_message == 'Едой':
                text = "На голодный желудок ничего путного не выйдет.Вы приобрели вяленое мясо." \
                       " Теперь вы чувствуете, что готовы к тому, что ждёт вас в подземельях."
                main_baff.append('мясо')
            return make_response(text, state={'location': 76, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location})
        if location == 76:
            text = "Вы входите в подземелья. Кромешная тьма расступается перед светом вашего факела." \
                   "Вдруг в углу вы замечаете чьё-то движение. " \
                   "Вам придётся вступить с ним в бой."
            return make_response(text, state={'location': 77, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('В бой!', hide=True),
            ])
        text = "Извините я вас не поняла." + "\n" + \
               "Хотите ли вы продолжить путешествие?"
        return make_response(text, state={'location': old_location, 'type_hero': 'archer', 'atr': atr,
                                          'old_location': location, 'debaf': debaf, 'false_flag': False},
                             buttons=[
                                 button('Продолжить путешествие', hide=True),
                             ])
    return make_response(text, state={'location': 0, 'type_hero': type_hero, 'atr': atr, 'old_location': 0},
                         buttons=[
                             button('Да', hide=True),
                             button('Нет', hide=True)
                         ])


if __name__ == '__main__':
    app.run()
