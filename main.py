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
                                     state={'location': 2, 'type_hero': 'wizard', 'atr': atr, 'old_location': location},
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
        if location == 31:
            text = "Вы заходите в старую таверну и встречаете там знакомого вам" + \
                   " эльфа, с которым вы когда-то вместе обучались стрельбе из лука!" + "\n" + \
                   "Вы хотите поздороваться с ним?"
            return make_response(text,
                                 state={'location': 32, 'type_hero': type_hero, 'atr': atr, 'old_location': location},
                                 buttons=[
                                     button('Поздороваться с ним', hide=True),
                                 ])
        if location == 32:
            if user_message == "Поздороваться с ним" or old_location == 33:
                text = "Эльф по имени Зик узнаёт вас, но выглядит обеспокоенным." + "\n" + \
                       "Вы простие друга рассказать о том, что его тревожит." + "\n" + \
                       "Эльф рассказывает вам о подозрительных, участившихся нападениях гоблинов на его родной город." + \
                       " Вы, как его старый друг, обещаете ему помочь разобраться с этой проблемой!" + "\n" + \
                       "Придя в родной город Зика - Зиланд, куда вы решаете направиться?" + "\n" + \
                       "В таверну, гильдию искателей приключений или к форпосту городской стражи?"
                return make_response(text, state={'location': 33, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В таверну', hide=True),
                    button('В гильдию искателей приключений', hide=True),
                    button('К форпосту городской стражи', hide=True),
                ])
        if location == 33:
            if user_message == "В таверну" or old_location == 34:
                text = "Вы заходите в таверну и решаете собрать информацию о нападениях гоблинов." + \
                       " Один из посетителей - бывалый воин - рассказывает о месте нахождении лагеря гоблинов." + \
                       " Он хорошо охраняется и находится в лесу рядом со старой плотиной, одному туда соваться опасно!" + \
                       " Воин говорит, что видит в вас большой потенциал и решает отдать вам плащ своего попутчика, " + \
                       "которому повезло меньше при встрече с гоблинами." + "\n" + \
                       "Плащ повысил вашу ловкость на 5 очков." + "\n" + \
                       "Куда вы решаете направиться дальше?" + "\n" + \
                       "В лагерь гоблинов, гильдию искателей приключений или к форпосту городской стражи?"
                if old_location != 34:
                    atr[2] += 5
                if old_location != 33:
                    return make_response(text, state={'location': 34, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('В лагерь гоблинов', hide=True),
                        button('В гильдию искателей приключений', hide=True),
                        button('К форпосту городской стражи', hide=True),
                    ])
                if old_location == 33:
                    return make_response(text, state={'location': 34, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location}, buttons=[
                        button('В лагерь гоблинов', hide=True),
                        button('К форпосту городской стражи', hide=True),
                    ])
            if user_message == "В гильдию искателей приключений" or old_location == 35:
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
                return make_response(text, state={'location': 35, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В лагерь гоблинов', hide=True),
                    button('К форпосту городской стражи', hide=True),
                ])
            if user_message == 'К форпосту городской стражи' or old_location == 33:
                text = "Стражники просят вас покинуть форпост и идти своей дорогой." + \
                       "Куда вы решаете направиться?" + "\n" + \
                       "В лагерь гоблинов?"
                return make_response(text, state={'location': 33, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В таверну', hide=True),
                    button('В гильдию искателей приключений', hide=True),
                ])
        if location == 34:
            if user_message == "В гильдию искателей приключений" or old_location == 35:
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
                return make_response(text, state={'location': 35, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В лагерь гоблинов', hide=True),
                    button('К форпосту городской стражи', hide=True),
                ])
            if user_message == 'В лагерь гоблинов' or old_location == 41 or old_location == 39:
                text = "Выйдя из города, вы идёте  по лесу." + "\n" + \
                       "Внезапно, на вас нападает отряд гоблинов, скорее всего " + \
                       "это была засада." + "\n" + \
                       "В бой!"
                if type_hero == 'archer':
                    if make_fight(atr[2], 23):
                        return make_response(text, state={'location': 41, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
                    else:
                        return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
            if user_message == 'К форпосту городской стражи' or old_location == 36:
                text = "Стражники просят вас покинуть форпост и идти своей дорогой." + "\n" + \
                       "Время позднее, таверна и гильдия уже закрылись." + "\n" + \
                       "Куда вы решаете направиться?" + "\n" + \
                       "В лагерь гоблинов?"
                return make_response(text, state={'location': 36, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В лагерь гоблинов', hide=True),
                ])
        if location == 35:
            if user_message == 'К форпосту городской стражи' or old_location == 36:
                text = "Стражники просят вас покинуть форпост и идти своей дорогой." + \
                       " Увидев кулон, полученный от заведующей гильдией, они извиняются и" + \
                       " ведут вас к своему командиру." + \
                       " Командир Далин, выслушав ваши намеренья, сообщает, что и сам" + \
                       " со своими подчинёными планировал сразить гоблинов, так как на днях" + \
                       " им наконец удалось обнаружить их лагерь." + "\n" + \
                       "Далин уверяет вас, что вы можете расчитывать на его помощь." + "\n" + \
                       "Куда вы решаете направиться?" + "\n" + \
                       "В лагерь гоблинов?"
                return make_response(text, state={'location': 36, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В лагерь гоблинов', hide=True),
                ])
            if user_message == 'В лагерь гоблинов' or old_location == 41 or old_location == 39:
                text = "Выйдя из города, вы идёте  по лесу." + "\n" + \
                       "Внезапно, на вас нападает отряд гоблинов, скорее всего " + \
                       "это была засада." + "\n" + \
                       "В бой!"
                if type_hero == 'archer':
                    if make_fight(atr[2], 23):
                        return make_response(text, state={'location': 41, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
                    else:
                        return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
        if location == 36:
            if user_message == 'В лагерь гоблинов' or old_location == 37 or old_location == 39:
                text = "Выйдя из города, вы идёте вместе со стражниками по лесу." + "\n" + \
                       "Внезапно, на вас нападает отряд гоблинов, скорее всего это была засада." + \
                       " Командир Далин уверяет вас, что справиться с ними сам и просит вас" + \
                       " продолжить следовать в лагерь гоблинов." + \
                       "Что вы решаете сделать?" + "\n" + \
                       "Помочь Далину или пробраться в лагерь гоблинов?"
                if type_hero == 'archer':
                    if make_fight(atr[2], 22):
                        return make_response(text, state={'location': 37, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('Помочь Далину', hide=True),
                            button('Пробраться в лагерь гоблинов', hide=True),
                        ])
                    else:
                        return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('Помочь Далину', hide=True),
                            button('Пробраться в лагерь гоблинов', hide=True),
                        ])
        if location == 37:
            if user_message == 'Помочь Далину' or (old_location == 38 and debaf == False):
                text = "Вы успешно отражаете все атаки гоблинов и отправляетесь вместе с Далином" + \
                       " в их лагерь." + "\n" + \
                       "Далин предлогает перед тем, как нападать на гоблинов, разрушить плотину и" + \
                       " затопить их лагерь." + "\n" + \
                       "Что вы решаете сделать?" + "\n" + \
                       "Разрушить плотину, просто пойти в атаку или поджечь лес?"
                return make_response(text, state={'location': 38, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location, 'debaf': debaf}, buttons=[
                    button('Разрушить плотину', hide=True),
                    button('Просто пойти в атаку', hide=True),
                    button('Поджечь лес', hide=True),
                ])
            if user_message == 'Пробраться в лагерь гоблинов' or (old_location == 38 and debaf):
                text = "Вы оставляете отряд Далина разбираться с гоблинами, организававших засаду, а" + \
                       " сами проникаете в их лагерь." + "\n" + \
                       "Что вы решаете сделать?" + "\n" + \
                       "Разрушить плотину, просто пойти в атаку или поджечь лес?"
                return make_response(text, state={'location': 38, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location, 'debaf': True}, buttons=[
                    button('Разрушить плотину', hide=True),
                    button('Просто пойти в атаку', hide=True),
                    button('Поджечь лес', hide=True),
                ])
        if location == 38:
            if user_message == 'Просто пойти в атаку' or old_location == 40 or old_location == 39:
                if debaf:
                    text = "В лагере оказалось ещё больше гоблинов чем было в засаде." + "\n" + \
                           "В бой!"
                    if make_fight(atr[2] + atr[0], 90):
                        return make_response(text, state={'location': 40, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location, 'debaf': debaf}, buttons=[
                            button('В бой!', hide=True),
                        ])
                else:
                    text = "В лагере оказалось ещё больше гоблинов чем было в засаде." + "\n" + \
                           "Хорошо, что вы не один! В бой!"
                    if make_fight(atr[2] + atr[0], 80):
                        return make_response(text, state={'location': 40, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location, 'debaf': debaf}, buttons=[
                            button('В бой!', hide=True),
                        ])
            if user_message == 'Разрушить плотину' or old_location == 39:
                if debaf:
                    text = "Вы разрушаете плотину и лагерь гоблинов смывает водой." + "\n" + \
                           " Вы получаете в награду за свою помощь новую броню эльфийской работы." + "\n" + \
                           " Ваше здоровье увеличилось на 20 очков." + "\n" + \
                           "Однако, вам также пришлось уплатить долг " + \
                           "за вред нанесённый окружающей среде, для этого вам пришлось " + \
                           ' продать ваше "кольцо ветра".' + "\n" + \
                           " Все ваши атрибуты понизились на 1 очко." + "\n" + \
                           " Хотите ли вы закончить своё путешествие?"
                    if old_location != 39:
                        atr[0] += 19
                        atr[1] -= 1
                        atr[2] -= 1
                        atr[3] -= 1
                    return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
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
                    if old_location != 39:
                        atr[0] += 20
                    return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
                                                      'old_location': location, 'debaf': debaf}, buttons=[
                        button('Да', hide=True),
                        button('Нет', hide=True),
                    ])
            if user_message == 'Поджечь лес' or old_location == 39:
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
                if old_location != 39:
                    atr[0] += 19
                    atr[1] -= 1
                    atr[2] -= 1
                    atr[3] -= 1
                return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location, 'debaf': debaf}, buttons=[
                    button('Да', hide=True),
                    button('Нет', hide=True),
                ])
        if location == 39:
            text = "К сожалению вы терпете поражение, хотите ли вы начать своё путешествие заново?"
            return end_work(text, event)
        if location == 40:
            text = "Вам удалось выстоять под тяжёлым натиском гоблинов." + "\n" + \
                   "После зачистки лагеря вы находите раненого камандира Далина, к счастью " + \
                   "рана не смертельна. Вы помогаете ему добраться до лекаря и " + \
                   "в награду за свою помощь новую броню эльфийской работы." + "\n" + \
                   " Ваше здоровье увеличилось на 20 очков." + "\n" + \
                   " Хотите ли вы закончить своё путешествие?"
            return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Да', hide=True),
                button('Нет', hide=True),
            ])
        if location == 41:
            text = "Вам удалось выстоять под тяжёлым натиском гоблинов." + "\n" + \
                   "Вы добираетесь до лагеря гоблинов. " + "\n" + \
                   "Что вы решаете сделать?" + "\n" + \
                   "Разрушить плотину, просто пойти в атаку или поджечь лес?"
            return make_response(text, state={'location': 38, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location, 'debaf': True}, buttons=[
                button('Разрушить плотину', hide=True),
                button('Просто пойти в атаку', hide=True),
                button('Поджечь лес', hide=True),
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