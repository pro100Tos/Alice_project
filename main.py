from flask import Flask, request, jsonify
from random import randint

STATE_RQUEST_KEY = 'session'
STATE_RESPONS_KEY = 'session_state'
main_baff = []
max_hp = 50

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
    global main_baff, max_hp
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
        if location == 2:
            if user_message == "Отправиться в путь":
                text = "Вы смело шагаете в неизвестность. По пути вам встречается старый заброшенный замок, который, как говорят, охраняется духом древнего воина."
                return make_response(text, state={'location': 11, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Исследовать замок', hide=True),
                                         button('Обойти замок', hide=True),
                                     ])
        if location == 11:
            if user_message == "Исследовать замок":
                text = "Вы входите в замок и чувствуете присутствие чего-то сверхъестественного. Вдруг перед вами возникает дух воина, который требует доказать вашу храбрость."
                return make_response(text, state={'location': 12, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Принять вызов', hide=True),
                                         button('Отступить', hide=True),
                                     ])
        if location == 12:
            if user_message == "Принять вызов":
                if atr[0] > 40:  # типо необходимый уровень силы для победы - больше 40
                    text = "Смело приняв вызов, вы демонстрируете свою силу и мастерство. Дух восхищен и дарит вам магический меч, увеличивающий ваши атрибуты."
                    atr[0] += 5  # увеличиваем силу
                    atr[1] += 5  # увеличиваем защиту
                    return make_response(text, state={'location': 13, 'type_hero': 'warrior', 'atr': atr},
                                         buttons=[
                                             button('Продолжить путешествие', hide=True),
                                         ])
                else:
                    text = "К сожалению, ваша сила оказалась недостаточной. Дух отвергает вас, и вы вынуждены отступить."
                    return make_response(text, state={'location': 11, 'type_hero': 'warrior', 'atr': atr},
                                         buttons=[
                                             button('Покинуть замок', hide=True),
                                         ])
        if location == 13:
            if user_message == "Продолжить путешествие":
                text = "Оснащенный магическим мечом, вы чувствуете себя непобедимым и продолжаете путешествие. По пути вы находите разделенную деревню, где жители просят о вашей помощи в урегулировании конфликта."
                return make_response(text, state={'location': 14, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Помочь деревне', hide=True),
                                         button('Игнорировать и продолжить путешествие', hide=True),
                                     ])

        if location == 14:
            if user_message == "Помочь деревне":
                text = "Вы решаете помочь деревне. Ваше вмешательство и авторитет воина помогают найти компромисс между спорящими сторонами. Благодарные жители дарят вам редкие травы, которые увеличивают ваше здоровье."
                atr[2] += 5  # увеличиваем здоровье
                return make_response(text, state={'location': 15, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Продолжить путешествие', hide=True),
                                     ])
            elif user_message == "Игнорировать и продолжить путешествие":
                text = "Вы решаете не вмешиваться в дела деревни и продолжаете свой путь. Перед вами открываются новые земли и возможности."
                return make_response(text, state={'location': 16, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Исследовать новые земли', hide=True),
                                     ])

        if location == 15:
            if user_message == "Продолжить путешествие":
                text = "С новыми силами вы отправляетесь в новое приключение, где вас ждут неведомые земли и новые испытания."
                return make_response(text, state={'location': 17, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Исследовать неизведанное', hide=True),
                                         button('Вернуться домой', hide=True),
                                     ])
        if location == 17:
            if user_message == "Исследовать неизведанное":
                text = "Отправляясь в неизведанные земли, вы сталкиваетесь с древними руинами, скрытыми в глубине таинственного леса. Здесь, среди забытых артефактов, вы чувствуете, что каждый шаг может быть наполнен как открытиями, так и опасностями."
                return make_response(text, state={'location': 18, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Исследовать руины', hide=True),
                                         button('Пройти мимо', hide=True),
                                     ])
            elif user_message == "Вернуться домой":
                text = "Решив, что приключения должны когда-то закончиться, вы поворачиваете назад, к родным землям. Дома вас ждут с теплотой и радостью, а ваши рассказы о путешествиях становятся любимыми историями на вечерах."
                return make_response(text, state={'location': 19, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Закончить путешествие', hide=True),
                                     ])

        if location == 18:
            if user_message == "Исследовать руины":
                text = "Исследуя древние руины, вы находите потайную комнату, в которой хранится могущественный артефакт. Этот предмет обещает большую силу, но его охраняет страж."
                return make_response(text, state={'location': 20, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Сразиться со стражем', hide=True),
                                         button('Отступить и сохранить находку в тайне', hide=True),
                                     ])
            elif user_message == "Пройти мимо":
                text = "Вы решаете не рисковать и пройти мимо древних руин. Путешествие продолжается, ведя вас через новые земли, полные чудес и опасностей."
                return make_response(text, state={'location': 21, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Продолжить путешествие', hide=True),
                                     ])

        if location == 20:
            if user_message == "Сразиться со стражем":
                if atr[0] > 45:  # проверка силы
                    text = "Ваша мощь и мастерство владения мечом позволяют победить стража. Артефакт теперь ваш. Он увеличивает вашу силу и магию."
                    atr[0] += 10  # увеличиваем силу
                    atr[3] += 10  # увеличиваем магию
                    return make_response(text, state={'location': 22, 'type_hero': 'warrior', 'atr': atr},
                                         buttons=[
                                             button('Продолжить путешествие с новой силой', hide=True),
                                         ])
                else:
                    text = "Попытка сразиться со стражем оказывается неудачной. Вы вынуждены отступить, но знания о существовании артефакта остаются с вами."
                    return make_response(text, state={'location': 18, 'type_hero': 'warrior', 'atr': atr},
                                         buttons=[
                                             button('Попробовать ещё раз', hide=True),
                                             button('Отойти и продолжить путь', hide=True),
                                         ])
        if location == 22:
            text = "Обладая новой силой и магическим артефактом, вы чувствуете, что способны на большее. Впереди много путей, каждый из которых обещает свои приключения и открытия."
            return make_response(text, state={'location': 23, 'type_hero': 'warrior', 'atr': atr},
                                 buttons=[
                                     button('Исследовать Северные горы', hide=True),
                                     button('Отправиться в Южные пустыни', hide=True),
                                     button('Вернуться в родной город', hide=True),
                                 ])

        if location == 23:
            if user_message == "Исследовать Северные горы":
                text = "Северные горы известны своими суровыми условиями и древними тайнами. Поднимаясь по склонам, вы сталкиваетесь с племенем горных троллей, которые не приветствуют посторонних."
                return make_response(text, state={'location': 24, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Переговорить с троллями', hide=True),
                                         button('Сражаться с троллями', hide=True),
                                         button('Обойти их территорию', hide=True),
                                     ])
            elif user_message == "Отправиться в Южные пустыни":
                text = "Южные пустыни - место жаркое и безжизненное. Но даже здесь есть жизнь. На горизонте вы видите караван верблюдов, который, возможно, сможет помочь вам в вашем путешествии."
                return make_response(text, state={'location': 25, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Присоединиться к каравану', hide=True),
                                         button('Продолжить путь в одиночку', hide=True),
                                     ])
            elif user_message == "Вернуться в родной город":
                text = "Возвращение домой всегда сладко. Ваше прибытие в родной город сопровождается радостью и праздником. Здесь вы можете отдохнуть и поделиться историями о своих приключениях."
                return make_response(text, state={'location': 26, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Завершить приключение и остаться дома', hide=True),
                                     ])

        # Продолжение событий в Северных горах и Южных пустынях
        if location == 24:
            if user_message == "Переговорить с троллями":
                text = "Ваши умения в дипломатии помогают установить контакт с троллями. Они рассказывают вам о скрытом сокровище в горах и предлагают помочь вам в обмен на часть добычи."
                return make_response(text, state={'location': 27, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Согласиться на помощь', hide=True),
                                         button('Отказаться и продолжить в одиночку', hide=True),
                                     ])
            elif user_message == "Сражаться с троллями":
                if atr[0] > 55:
                    text = "Ваша мощь позволяет одолеть троллей, открывая путь через горы. Вам удаётся найти путь к забытому храму, скрытому среди скал."
                    return make_response(text, state={'location': 28, 'type_hero': 'warrior', 'atr': atr},
                                         buttons=[
                                             button('Исследовать храм', hide=True),
                                         ])
                else:
                    text = "Битва с троллями оказывается слишком тяжёлой. Вы вынуждены отступить и переосмыслить свои планы."
                    return make_response(text, state={'location': 24, 'type_hero': 'warrior', 'atr': atr},
                                         buttons=[
                                             button('Попробовать переговорить', hide=True),
                                             button('Обойти территорию', hide=True),
                                         ])
            elif user_message == "Обойти их территорию":
                text = "Обход троллей занимает больше времени, но вы избегаете конфликта и находите тихий путь через горы. Впереди новые испытания."
                return make_response(text, state={'location': 29, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Продолжить путь', hide=True),
                                     ])

        # Подобные блоки можно продолжать развивать, добавляя новые сюжетные повороты и варианты развития событий.
        if location == 25:
            if user_message == "Присоединиться к каравану":
                text = "Присоединяясь к каравану, вы обретаете новых друзей и учитесь у них многому о выживании в пустыне. Ваше путешествие становится безопаснее, и вы узнаете о легендарном городе, погребенном под песками."
                return make_response(text, state={'location': 30, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Исследовать погребенный город', hide=True),
                                         button('Продолжить путь с караваном', hide=True),
                                     ])
            elif user_message == "Продолжить путь в одиночку":
                text = "Выбрав одиночное путешествие, вы сталкиваетесь с жестокими условиями пустыни. Но ваша решимость и умения помогают вам находить ресурсы для выживания. Вдруг, на горизонте появляется оазис."
                return make_response(text, state={'location': 31, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Исследовать оазис', hide=True),
                                         button('Игнорировать оазис и продолжить путь', hide=True),
                                     ])

        # Завершение приключения в родном городе
        if location == 26:
            text = "Праздничные гуляния в честь вашего возвращения наполняют вас гордостью и радостью. Вы решаете остаться, чтобы передать свой опыт молодым воинам и помогать своему городу."
            return make_response(text, state={'location': 'end', 'type_hero': 'warrior', 'atr': atr},
                                 buttons=[
                                     button('Закончить игру', hide=True),
                                 ])

        # Исследование погребенного города
        if location == 30:
            if user_message == "Исследовать погребенный город":
                text = "Сопровождаемый новыми друзьями из каравана, вы находите вход в погребенный город. Внутри вас ждут древние артефакты и неизвестные опасности."
                return make_response(text, state={'location': 32, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Продолжить исследования', hide=True),
                                         button('Вернуться к каравану', hide=True),
                                     ])
            elif user_message == "Продолжить путь с караваном":
                text = "Продолжая путь с караваном, вы пересекаете множество торговых путей, каждый из которых раскрывает новые возможности и приключения."
                return make_response(text, state={'location': 33, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Остановиться в следующем городе', hide=True),
                                     ])

        # Исследование оазиса
        if location == 31:
            if user_message == "Исследовать оазис":
                text = "Оазис оказывается спасением в жаре пустыни и домом для разнообразной флоры и фауны. В глубине оазиса вы находите древние руины, кажущиеся забытыми временем."
                return make_response(text, state={'location': 34, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Исследовать руины', hide=True),
                                         button('Наполнить запасы водой и продолжить путь', hide=True),
                                     ])
            elif user_message == "Игнорировать оазис и продолжить путь":
                text = "Игнорируя оазис, вы продолжаете путь по безжизненной пустыне. Жажда и усталость начинают сказываться, но ваша целеустремленность помогает сохранить силы и надежду."
                return make_response(text, state={'location': 35, 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Продолжить путь', hide=True),
                                     ])
        # Завершение исследования погребенного города
        if location == 32:
            if user_message == "Продолжить исследования":
                text = "В глубинах древнего города вы обнаруживаете зал, полный сокровищ и древних манускриптов. Изучив их, вы узнаете о давно забытых знаниях, которые помогут вам в дальнейших приключениях."
                return make_response(text, state={'location': 'end', 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Закончить игру', hide=True),
                                     ])
            elif user_message == "Вернуться к каравану":
                text = "Возвращение к каравану оказывается мудрым решением. Объединив усилия, вы и новые друзья безопасно добираетесь до ближайшего населенного пункта, где ваш герой получает заслуженное признание."
                return make_response(text, state={'location': 'end', 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Закончить игру', hide=True),
                                     ])

        # Завершение пути с караваном
        if location == 33:
            if user_message == "Остановиться в следующем городе":
                text = "Остановка в городе позволяет вам пополнить запасы и обменять информацию с другими путешественниками. Вы находите новых друзей и решаете остаться здесь, чтобы помочь в развитии торговли и защите города."
                return make_response(text, state={'location': 'end', 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Закончить игру', hide=True),
                                     ])

        # Завершение исследования оазиса
        if location == 34:
            if user_message == "Исследовать руины":
                text = "Руины оказываются древним храмом, полным загадок и испытаний. Преодолев все препятствия, вы находите магический артефакт, усиливающий ваши способности. Вы решаете вернуться домой, чтобы изучить его возможности."
                return make_response(text, state={'location': 'end', 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Закончить игру', hide=True),
                                     ])
            elif user_message == "Наполнить запасы водой и продолжить путь":
                text = "Пополнив запасы воды, вы продолжаете свое путешествие, полное трудностей и приключений. В конечном итоге вы возвращаетесь домой, где вас ждет теплый прием и уважение за проявленные упорство и мужество."
                return make_response(text, state={'location': 'end', 'type_hero': 'warrior', 'atr': atr},
                                     buttons=[
                                         button('Закончить игру', hide=True),
                                     ])

        # Завершение пути по безжизненной пустыне
        if location == 35:
            if user_message == "Продолжить путь":
                text = "Долгое путешествие через пустыню заканчивается вашим возвращением в родной город, " \
                       "где вас принимают как героя. Опыт, набранный в путешествии, делает вас мудрее и сильнее. " \
                       "Это приключение окончено, но впереди ещё много других. Хотите начать говую игру?"
                return make_response(text, state={'location': 0, 'type_hero': type_hero, 'atr': atr, 'old_location': 0},
                                     buttons=[
                                         button('Да', hide=True),
                                         button('Нет', hide=True)
                                     ])

        if location == 36:
            text = "Вы заходите в старую таверну и встречаете там знакомого вам" + \
                   " эльфа, с которым вы когда-то вместе обучались стрельбе из лука!" + "\n" + \
                   "Вы хотите поздороваться с ним?"
            return make_response(text,
                                 state={'location': 37, 'type_hero': type_hero, 'atr': atr, 'old_location': location},
                                 buttons=[
                                     button('Поздороваться с ним', hide=True),
                                 ])
        if location == 37:
            if user_message == "Поздороваться с ним" or old_location == 38:
                text = "Эльф по имени Зик узнаёт вас, но выглядит обеспокоенным." + "\n" + \
                       "Вы простие друга рассказать о том, что его тревожит." + "\n" + \
                       "Эльф рассказывает вам о подозрительных, участившихся нападениях гоблинов на его родной город." + \
                       " Вы, как его старый друг, обещаете ему помочь разобраться с этой проблемой!" + "\n" + \
                       "Придя в родной город Зика - Зиланд, куда вы решаете направиться?" + "\n" + \
                       "В таверну, гильдию искателей приключений или к форпосту городской стражи?"
                return make_response(text, state={'location': 38, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В таверну', hide=True),
                    button('В гильдию искателей приключений', hide=True),
                    button('К форпосту городской стражи', hide=True),
                ])
        if location == 38:
            if user_message == "В таверну" or old_location == 39:
                text = "Вы заходите в таверну и решаете собрать информацию о нападениях гоблинов." + \
                       " Один из посетителей - бывалый воин - рассказывает о месте нахождении лагеря гоблинов." + \
                       " Он хорошо охраняется и находится в лесу рядом со старой плотиной, одному туда соваться опасно!" + \
                       " Воин говорит, что видит в вас большой потенциал и решает отдать вам плащ своего попутчика, " + \
                       "которому повезло меньше при встрече с гоблинами." + "\n" + \
                       "Плащ повысил вашу ловкость на 5 очков." + "\n" + \
                       "Куда вы решаете направиться дальше?" + "\n" + \
                       "В лагерь гоблинов, гильдию искателей приключений или к форпосту городской стражи?"
                if old_location != 39:
                    atr[2] += 5
                if old_location != 38:
                    return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('В лагерь гоблинов', hide=True),
                        button('В гильдию искателей приключений', hide=True),
                        button('К форпосту городской стражи', hide=True),
                    ])
                if old_location == 38:
                    return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('В лагерь гоблинов', hide=True),
                        button('К форпосту городской стражи', hide=True),
                    ])
            if user_message == "В гильдию искателей приключений" or old_location == 40:
                text = "Вы подходите к девушке, заведующей гильдией в этом городе." + \
                       " После ваших слов о том, что вы хотите взять заказ на гоблинов," + \
                       " она хмурится и пытается вас отговорить от этой затеи." + \
                       " Очевидно, девушка уже повидала несколько смельчаков, взявшись за" + \
                       " эту работу, но судя по всему они так и не вернулись." + "\n" + \
                       "Понимая, что спорить с вами бесполезно, она советует вам обратиться" + \
                       " за помощью к городской страже и отдаёт вам странный кулон." + \
                       " По её словам, увидев его, городские стражники согласяться вам помочь." + "\n" + \
                       "Куда вы решаете направиться дальше?" + "\n" + \
                       "В лагерь гоблинов, таверну или к форпосту городской стражи?"
                return make_response(text, state={'location': 40, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В лагерь гоблинов', hide=True),
                    button('К форпосту городской стражи', hide=True),
                ])
            if user_message == 'К форпосту городской стражи' or old_location == 38:
                text = "Стражники просят вас покинуть форпост и идти своей дорогой." + \
                       "Куда вы решаете направиться?" + "\n" + \
                       "В лагерь гоблинов?"
                return make_response(text, state={'location': 38, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В таверну', hide=True),
                    button('В гильдию искателей приключений', hide=True),
                ])
        if location == 39:
            if user_message == "В гильдию искателей приключений" or old_location == 40:
                text = "Вы подходите к девушке, заведующей гильдией в этом городе." + \
                       " После ваших слов о том, что вы хотите взять заказ на гоблинов," + \
                       " она хмурится и пытается вас отговорить от этой затеи." + \
                       " Очевидно, девушка уже повидала несколько смельчаков, взявшись за" + \
                       " эту работу, но судя по всему они так и не вернулись." + "\n" + \
                       "Понимая, что спорить с вами бесполезно, она советует вам обратиться" + \
                       " за помощью к городской страже и отдаёт вам странный кулон." + \
                       " По её словам, увидев его, городские стражники согласяться вам помочь." + "\n" + \
                       "Куда вы решаете направиться дальше?" + "\n" + \
                       "В лагерь гоблинов или к форпосту городской стражи?"
                return make_response(text, state={'location': 40, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В лагерь гоблинов', hide=True),
                    button('К форпосту городской стражи', hide=True),
                ])
            if user_message == 'В лагерь гоблинов' or old_location == 46 or old_location == 44:
                text = "Выйдя из города, вы идёте  по лесу." + "\n" + \
                       "Внезапно, на вас нападает отряд гоблинов, скорее всего " + \
                       "это была засада." + "\n" + \
                       "В бой!"
                if type_hero == 'archer':
                    if make_fight(atr[2], 23):
                        return make_response(text, state={'location': 46, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
                    else:
                        return make_response(text, state={'location': 44, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
            if user_message == 'К форпосту городской стражи' or old_location == 41:
                text = "Стражники просят вас покинуть форпост и идти своей дорогой." + "\n" + \
                       "Время позднее, таверна и гильдия уже закрылись." + "\n" + \
                       "Куда вы решаете направиться?" + "\n" + \
                       "В лагерь гоблинов?"
                return make_response(text, state={'location': 41, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В лагерь гоблинов', hide=True),
                ])
        if location == 40:
            if user_message == 'К форпосту городской стражи' or old_location == 41:
                text = "Стражники просят вас покинуть форпост и идти своей дорогой." + \
                       " Увидев кулон, полученный от заведующей гильдией, они извиняются и" + \
                       " ведут вас к своему командиру." + \
                       " Командир Далин, выслушав ваши намеренья, сообщает, что и сам" + \
                       " со своими подчинёными планировал сразить гоблинов, так как на днях" + \
                       " им наконец удалось обнаружить их лагерь." + "\n" + \
                       "Далин уверяет вас, что вы можете расчитывать на его помощь." + "\n" + \
                       "Куда вы решаете направиться?" + "\n" + \
                       "В лагерь гоблинов?"
                return make_response(text, state={'location': 41, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В лагерь гоблинов', hide=True),
                ])
            if user_message == 'В лагерь гоблинов' or old_location == 46 or old_location == 44:
                text = "Выйдя из города, вы идёте  по лесу." + "\n" + \
                       "Внезапно, на вас нападает отряд гоблинов, скорее всего " + \
                       "это была засада." + "\n" + \
                       "В бой!"
                if type_hero == 'archer':
                    if make_fight(atr[2], 23):
                        return make_response(text, state={'location': 46, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
                    else:
                        return make_response(text, state={'location': 44, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
        if location == 41:
            if user_message == 'В лагерь гоблинов' or old_location == 42 or old_location == 44:
                text = "Выйдя из города, вы идёте вместе со стражниками по лесу." + "\n" + \
                       "Внезапно, на вас нападает отряд гоблинов, скорее всего это была засада." + \
                       " Командир Далин уверяет вас, что справиться с ними сам и просит вас" + \
                       " продолжить следовать в лагерь гоблинов." + \
                       "Что вы решаете сделать?" + "\n" + \
                       "Помочь Далину или пробраться в лагерь гоблинов?"
                if type_hero == 'archer':
                    if make_fight(atr[2], 22):
                        return make_response(text, state={'location': 42, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('Помочь Далину', hide=True),
                            button('Пробраться в лагерь гоблинов', hide=True),
                        ])
                    else:
                        return make_response(text, state={'location': 44, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('Помочь Далину', hide=True),
                            button('Пробраться в лагерь гоблинов', hide=True),
                        ])
        if location == 42:
            if user_message == 'Помочь Далину' or (old_location == 43 and debaf == False):
                text = "Вы успешно отражаете все атаки гоблинов и отправляетесь вместе с Далином" + \
                       " в их лагерь." + "\n" + \
                       "Далин предлогает перед тем, как нападать на гоблинов, разрушить плотину и" + \
                       " затопить их лагерь." + "\n" + \
                       "Что вы решаете сделать?" + "\n" + \
                       "Разрушить плотину, просто пойти в атаку или поджечь лес?"
                return make_response(text, state={'location': 43, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location, 'debaf': debaf}, buttons=[
                    button('Разрушить плотину', hide=True),
                    button('Просто пойти в атаку', hide=True),
                    button('Поджечь лес', hide=True),
                ])
            if user_message == 'Пробраться в лагерь гоблинов' or (old_location == 43 and debaf):
                text = "Вы оставляете отряд Далина разбираться с гоблинами, организававших засаду, а" + \
                       " сами проникаете в их лагерь." + "\n" + \
                       "Что вы решаете сделать?" + "\n" + \
                       "Разрушить плотину, просто пойти в атаку или поджечь лес?"
                return make_response(text, state={'location': 43, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location, 'debaf': True}, buttons=[
                    button('Разрушить плотину', hide=True),
                    button('Просто пойти в атаку', hide=True),
                    button('Поджечь лес', hide=True),
                ])
        if location == 43:
            if user_message == 'Просто пойти в атаку' or old_location == 45 or old_location == 44:
                if debaf:
                    text = "В лагере оказалось ещё больше гоблинов чем было в засаде." + "\n" + \
                           "В бой!"
                    if make_fight(atr[2] + atr[0], 90):
                        return make_response(text, state={'location': 45, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location, 'debaf': debaf}, buttons=[
                            button('В бой!', hide=True),
                        ])
                else:
                    text = "В лагере оказалось ещё больше гоблинов чем было в засаде." + "\n" + \
                           "Хорошо, что вы не один! В бой!"
                    if make_fight(atr[2] + atr[0], 80):
                        return make_response(text, state={'location': 45, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location, 'debaf': debaf}, buttons=[
                            button('В бой!', hide=True),
                        ])
            if user_message == 'Разрушить плотину' or old_location == 44:
                if debaf:
                    text = "Вы разрушаете плотину и лагерь гоблинов смывает водой." + "\n" + \
                           " Вы получаете в награду за свою помощь новую броню эльфийской работы." + "\n" + \
                           " Ваше здоровье увеличилось на 20 очков." + "\n" + \
                           "Однако, вам также пришлось уплатить долг " + \
                           "за вред нанесённый окружающей среде, для этого вам пришлось " + \
                           ' продать ваше "кольцо ветра".' + "\n" + \
                           " Все ваши атрибуты понизились на 1 очко." + "\n" + \
                           " Хотите ли вы закончить своё путешествие?"
                    if old_location != 44:
                        atr[0] += 19
                        atr[1] -= 1
                        atr[2] -= 1
                        atr[3] -= 1
                    return make_response(text, state={'location': 44, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location, 'debaf': debaf}, buttons=[
                        button('Да', hide=True),
                        button('Нет', hide=True),
                    ])
                else:
                    text = "Вы разрушаете плотину и лагерь гоблинов смывает водой." + "\n" + \
                           "Ответственность за разрушение плотины капитан Далин берёт на себя." + \
                           " Вы получаете в награду за свою помощь новую броню эльфийской работы." + "\n" + \
                           " Ваше здоровье увеличилось на 20 очков." + "\n" + \
                           " Хотите ли вы закончить своё путешествие?"
                    if old_location != 44:
                        atr[0] += 20
                    return make_response(text, state={'location': 44, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location, 'debaf': debaf}, buttons=[
                        button('Да', hide=True),
                        button('Нет', hide=True),
                    ])
            if user_message == 'Поджечь лес' or old_location == 44:
                text = "Вы поджигаете лес и теперь гобилам некуда бежать." + "\n" + \
                       "Огонь перекидывается на их лагерь и большенство гоблинов " + \
                       " погибает, лишь не многие смогли переплыть реку и сбежать." + "\n" + \
                       "Лагерь уничтожен и ваша работа выполнена." + "\n" + \
                       "Вы получаете в награду за свою помощь новую броню эльфийской работы. " + \
                       " Ваше здоровье увеличилось на 20 очков." + "\n" + \
                       "Однако, вам также пришлось уплатить долг " + \
                       "за вред нанесённый окружающей среде, для этого вам пришлось " + \
                       ' продать ваше "кольцо ветра".' + "\n" + \
                       " Все ваши атрибуты понизились на 1 очко." + "\n" + \
                       " Хотите ли вы закончить своё путешествие?"
                if old_location != 44:
                    atr[0] += 19
                    atr[1] -= 1
                    atr[2] -= 1
                    atr[3] -= 1
                return make_response(text, state={'location': 44, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location, 'debaf': debaf}, buttons=[
                    button('Да', hide=True),
                    button('Нет', hide=True),
                ])
        if location == 44:
            text = "К сожалению вы терпете поражение, хотите ли вы начать своё путешествие заново?"
            return end_work(text, event)
        if location == 45:
            text = "Вам удалось выстоять под тяжёлым натиском гоблинов." + "\n" + \
                   "После зачистки лагеря вы находите раненого камандира Далина, к счастью " + \
                   "рана не смертельна. Вы помогаете ему добраться до лекаря и " + \
                   "в награду за свою помощь новую броню эльфийской работы." + "\n" + \
                   " Ваше здоровье увеличилось на 20 очков." + "\n" + \
                   " Хотите ли вы закончить своё путешествие?"
            return make_response(text, state={'location': 44, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Да', hide=True),
                button('Нет', hide=True),
            ])
        if location == 46:
            text = "Вам удалось выстоять под тяжёлым натиском гоблинов." + "\n" + \
                   "Вы добираетесь до лагеря гоблинов. " + "\n" + \
                   "Что вы решаете сделать?" + "\n" + \
                   "Разрушить плотину, просто пойти в атаку или поджечь лес?"
            return make_response(text, state={'location': 43, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location, 'debaf': True}, buttons=[
                button('Разрушить плотину', hide=True),
                button('Просто пойти в атаку', hide=True),
                button('Поджечь лес', hide=True),
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
                       "Выяснилось, что мертвецы вышли из древних захоронений в пещерах." \
                       "Несмотря на щедрую оплату, никто не решался спуститься в подземелья." \
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
                   "На вас со злобным рычанием выскакивает мертвец." \
                   "Вам придётся вступить с ним в бой."
            if type_hero == 'wizard':
                if make_fight(atr[3], 23):
                    return make_response(text, state={'location': 77, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('В бой!', hide=True)
                    ])
                else:
                    return make_response(text, state={'location': 78, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('В бой!', hide=True)
                    ])
        if location == 77:
            if user_message == 'В бой!':
                text = "Пламя окутало мертвеца, оставив от него горсть пепла. " \
                       "Вы победили в этой схватке. " \
                       "Вы можете продолжить путь."
                return make_response(text, state={'location': 79, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Продолжить путь', hide=True)
                ])
        if location == 78:
            if user_message == 'В бой!':
                text = "К сожалению, вы терпите поражение." \
                       "Вам удалось сбежать, но мертвец смог ранить вас." \
                       "Ваше здоровье понижено на 10 очков." \
                       "Вы можете продолжить путь."
                atr[0] -= 10
                if 'зелье лечения' in main_baff:
                    return make_response(text, state={'location': 79, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('Использовать зелье лечения', hide=True),
                        button('Продолжить путь', hide=True)
                    ])
                else:
                    return make_response(text, state={'location': 79, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('Продолжить путь', hide=True)
                    ])
        if location == 79:
            if user_message == 'Использовать зелье лечения':
                text = "Вы используете зелье лечения. Вы снова полностью здоровы. " \
                       "Вы продолжаете путь." \
                       "Впереди вас ждёт винтвая лестница вниз." \
                       "Вы спускаетесь по ней и останавливаетесь на пороге освещённого зала." \
                       "Предчуствие подсказывает вам быть осторожными."
                del main_baff[main_baff.index('зелье лечения')]
                atr[0] = max_hp
            elif user_message == 'Продолжить путь':
                text = "Вы продолжаете путь." \
                       "Впереди вас ждёт винтвая лестница вниз." \
                       "Вы спускаетесь по ней и останавливаетесь на пороге освещённого зала." \
                       "Предчуствие подсказывает вам быть осторожными."

            return make_response(text, state={'location': 80, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Войти в зал', hide=True)
            ])
        if location == 80:
            if user_message == 'Войти в зал':
                if make_fight(atr[2], 15):
                    text = "Вы входите зал, и вдруг из стены в вас летит стрела," \
                           "но вам чудом удаётся увернуться от ловушки."
                else:
                    text = "Вы входите зал, и вдруг из стены в вас летит стрела," \
                           "которая попадает вам в ногу. Ваше здоровье понижено на 5 очков."
                    atr[0] -= 5
                text = text + "Вы решаете осмотреться. Зал оказывается гробницей." \
                              "Вокруг множество гробов, а в них пока ещё спящие мертвецы." \
                              "Впереди вы замечаете две двери. В какую войдёте?"
                return make_response(text, state={'location': 81, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Левая дверь', hide=True),
                    button('Правая дверь', hide=True)
                ])
            if main_baff.count('рычаг') == 1 and \
                    (user_message == 'Использовать зелье лечения' or user_message == 'Уйти'):
                if user_message == 'Использовать зелье лечения':
                    text = 'Вы используете зелье лечения. Вы снова полностью здоровы. ' \
                           'Вам осталось обследовать ещё одну комнату.'
                    del main_baff[main_baff.index('зелье лечения')]
                    atr[0] = max_hp
                else:
                    text = 'Вы вернулись в зал. Вам осталось обследовать ещё одну комнату.'
                if old_location == 83:
                    return make_response(text, state={'location': 81, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('Правая дверь', hide=True)
                    ])
                else:
                    return make_response(text, state={'location': 81, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('Левая дверь', hide=True)
                    ])
            if main_baff.count('рычаг') == 2 and \
                    (user_message == 'Использовать зелье лечения' or user_message == 'Уйти'):
                text = 'Выходя из комнаты вы слышите странный щелчок и видите, как в стене открывается потайной проход.' \
                       'Громкий звук заставил мертвецов проснуться, и они, преградив дорогу, бросились на вас.'
                return make_response(text, state={'location': 84, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В бой!', hide=True),
                ])
        if location == 81:
            if user_message == 'Левая дверь':
                text = "Вы открываете левую дверь. За ней находится просторная комната. " \
                       "Ваш взгляд падает на сундук, на котором... Лежит маленький дракон! " \
                       "Ваш визит не остался незамеченным - дракон начал расправлять крылья, яростно сверкнув глазами."
                if 'мясо' in main_baff:
                    return make_response(text, state={'location': 82, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('Предложить дракону мясо', hide=True),
                        button('Вступить в бой', hide=True)
                    ])
                else:
                    return make_response(text, state={'location': 82, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('Убежать', hide=True),
                        button('Вступить в бой', hide=True)
                    ])
            elif user_message == 'Правая дверь':
                text = "За правой дверью вы находите старый алтарь. Потёртая каменная плита гласит: " \
                       "'Ваша сила - в вашей крови. Крови, которую вы получили от своих предков.'. " \
                       "В алтаре есть щель для монет. Что будете делать?"
                return make_response(text, state={'location': 83, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Кинуть монету', hide=True),
                    button('Ничего не делать', hide=True)
                ])
        if location == 82:
            if user_message == 'Предложить дракону мясо':
                text = "Увидев в вашей руке мясо, дракон с любопытсвом принюхался. " \
                       "Он осторожно подошёл к вам и начал есть из ваших рук. " \
                       "Вам удалось приручить маленького дракона. Теперь он будет помогать вам в битвах. " \
                       "Что собираетесь делать дальше?"
                del main_baff[main_baff.index('мясо')]
                main_baff.append('дракон')
                atr[3] += 10
                return make_response(text, state={'location': 83, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Открыть сундук', hide=True),
                    button('Уйти', hide=True)
                ])
            elif user_message == 'Вступить в бой':
                if make_fight(atr[3], 28):
                    text = "Вам удалось одолеть маленького дракона. Чешуя дракона обладает целебными свойствами. " \
                           "Вы получили чешую дракона. Что собираетесь делать дальше?"
                    return make_response(text, state={'location': 83, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('Открыть сундук', hide=True),
                        button('Уйти', hide=True)
                    ])
                else:
                    text = "К сожалению, вы потерпели поражение. Дракон нанёс вам сильные ожоги. " \
                           "Ваше здоровье понижено на 20 очков. " \
                           "Вам удалось убежать из комнаты, и по пути вы задеваете какой-то рычаг."
            elif user_message == 'Убежать':
                text = "Вы решаете убежать от битвы, но на выходе из комнаты вас настигает пламя дракона. " \
                       "Ваше здоровье понижено на 25 очков. " \
                       "Вам удалось убежать из комнаты, и по пути вы задеваете какой-то рычаг."
            if "зелье лечения" in main_baff:
                main_baff.append('рычаг')
                return make_response(text, state={'location': 80, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Использовать зелье лечения', hide=True),
                    button('Уйти', hide=True)
                ])
            else:
                main_baff.append('рычаг')
                return make_response(text, state={'location': 80, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Уйти', hide=True)
                ])
        if location == 83:
            if user_message == 'Открыть сундук':
                text = "В сундуке вы находите магический свиток. Ваш интеллект повышен на 5 очков. " \
                       "Продвигаясь к выходу вы замечаете рычаг. Вы нажимаете на него, но ничего не происходит."
                main_baff.append('рычаг')
                return make_response(text, state={'location': 80, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Уйти', hide=True)
                ])
            if user_message == 'Кинуть монету':
                text = "Кинув монету, вы видете, как вокруг алтаря появилось слабое свечение. " \
                       "Вы чувствуете слабость, но ощущаете, что стали сильнее. " \
                       "Ваше максимальное здоровье снижено на 5 очков. Ваша сила увеличилась на 5 очков." \
                       "Вы заметили рычаг и нажали на него. Ничего не произошло."
                max_hp = 45
                atr[1] += 5
            elif user_message == "Ничего не делать":
                text = "Вы решаете ничего не делать. Вы заметили рычаг и нажали на него. Ничего не произошло."
            main_baff.append('рычаг')
            return make_response(text, state={'location': 80, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Уйти', hide=True)
            ])
        if location == 84:
            if user_message == 'В бой!':
                if type_hero == 'wizard':
                    if make_fight(atr[3], 30):
                        text = "В храбом бою вам удалось одолеть мертвецов. " \
                               "На одном из них вы замечаете зачарованный доспех."
                        if atr[1] >= 15:
                            text += "Вы надеваете этот доспех, который наполняет вас магической силой. " \
                                    "Ваш интеллект повышен на 10 очков."
                        else:
                            text += "К сожалению, этот доспех слишком тяжёл для вас."
                    else:
                        atr[0] -= 20
                        if atr[0] <= 0:
                            text = "К сожалению вы терпите поражение, хотите ли вы начать своё путешествие заново?"
                            return end_work(text, event)
                        text = "Вы храбро бились, но силы были не равны, и без потерь вам уйти не удалось. " \
                               "Ваше здоровье снижено на 20 очков."
                if 'зелье лечения' in main_baff:
                    return make_response(text, state={'location': 85, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('Продолжить путь', hide=True),
                        button('Использовать зелье лечения', hide=True)
                    ])
                else:
                    return make_response(text, state={'location': 85, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('Продолжить путь', hide=True)
                    ])
        if location == 85:
            if user_message == 'Использовать зелье лечения':
                del main_baff[main_baff.index('зелье лечения')]
                atr[0] = max_hp
                text = "Вы используете зелье лечения. Вы снова полностью здоровы. Вы продолжаете путь. " \
                       "Спустя долгое время блуждания по корридорам вы натыкаетесь на массивную дверь."
            elif user_message == 'Продолжить путь':
                text = "Вы продолжаете путь. Спустя долгое время блуждания по корридорам " \
                        "вы натыкаетесь на массивную дверь."
            return make_response(text, state={'location': 86, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Открыть дверь', hide=True)
            ])
        if location == 86:
            if user_message == 'Открыть дверь':
                text = "За дверью находится просторное комната, оплетённая корнями. В центре комнаты находится трон," \
                       "на котором сидит человек в чёрном балахоне. Он вас заметил и злобно усмехнулся: " \
                       "'Тоже пришёл за камнем цветка? Боюсь ты опоздал.'"
                return make_response(text, state={'location': 87, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Поговорить с колдуном', hide=True),
                ])
        if location == 87:
            if user_message == 'Поговорить с колдуном':
                text = "Колдун сообщил вам, что ему удалось найти цветок Зла " \
                       "и с помощь его силы он собирается поднять армию мертвецов и захватить власть над королеством." \
                       "Колдун вступает с вами в бой."
                if type_hero == 'wizard':
                    if make_fight(atr[3], 35):
                        return make_response(text, state={'location': 8, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
                    else:
                        text = "К сожалению вы терпите поражение, хотите ли вы начать своё путешествие заново?"
                        return end_work(text, event)
        if location == 88:
            text = "Это был трудный бой, но вам удалось справиться со злым колдуном. " \
                   "Теперь мертвецы больше не потревожат жителей города по ночам." \
                   " Вы замечаете на груди колдуна алый камень." \
                   "Скорее всего это и есть тот самый камень цветка Зла."
            return make_response(text, state={'location': 89, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Взять камень', hide=True),
                button('Уйти', hide=True)
            ])
        if location == 89:
            if user_message == 'Взять камень':
                text = "Теперь вы стали обладателем огромной магической силы, заключённой в камне. " \
                       "Но теперь вашей душой завладела тьма и вы будете распространять её, пока не придёт тот, " \
                       "кто сможет сравниться с вами по силе и свергнет вас, либо мир не погрузиться во тьму." \
                       "Начать новое приключение?"
            if user_message == 'Уйти':
                text = "Вы уходите и проход за вами заваливает камнями. " \
                       "Вы вернулись в город, где вас встречают как героя. Вы заслужили денежное вознаграждение." \
                       "Ваше приключение окончено, но впререди ждут другие. Начать новое приключение?"
                return make_response(text, state={'location': 0, 'type_hero': type_hero, 'atr': atr, 'old_location': 0},
                                     buttons=[
                                         button('Да', hide=True),
                                         button('Нет', hide=True)
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
