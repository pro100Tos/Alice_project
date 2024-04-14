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
        if user_message == "Покажи мои атрибуты":
            text = show_atributs(atr)
            debaf = False
            if old_location == 38:
                debaf = state.get('debaf')
            return make_response(text, state={'location': old_location, 'type_hero': 'archer', 'atr': atr,
                                              'old_location': location, 'debaf': debaf},
                                 buttons=[
                                     button('Продолжить путешествие', hide=True),
                                 ])
        if location == 1:
            if user_message == "Маг":
                atr = [50, 10, 10, 20]
                text = "Отлично! Вот ваши атрибуты:" + "\n" + show_atributs(atr)
                return make_response(text,
                                     state={'location': 70, 'type_hero': 'wizard', 'atr': atr,
                                            'old_location': location},
                                     buttons=[
                                         button('Отправиться в путь', hide=True),
                                     ])
            if user_message == "Лучник":
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
                   "Вы хотите поздороваться с ним, сделать вид, что вы его не заметили или покинуть таверну?"
            return make_response(text,
                                 state={'location': 32, 'type_hero': type_hero, 'atr': atr, 'old_location': location},
                                 buttons=[
                                     button('Поздороваться с ним', hide=True),
                                     button('Сделать вид, что вы его не заметили', hide=True),
                                     button('Покинуть таверну', hide=True),
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
                return make_response(text, state={'location': 34, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('В лагерь гоблинов', hide=True),
                    button('В гильдию искателей приключений', hide=True),
                    button('К форпосту городской стражи', hide=True),
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
        if location == 36:
            if user_message == 'В лагерь гоблинов' or old_location == 37:
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
                        return make_response(text, state={'location': 50, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('Помочь Далину', hide=True),
                            button('Пробраться в лагерь гоблинов', hide=True),
                        ])
        if location == 37:
            debaf = False
            if old_location == 38:
                debaf = state.get('debaf')
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
            debaf = state.get('debaf')
            if user_message == 'Просто пойти в атаку':
                if debaf:
                    text = "В лагере оказалось ещё больше гоблинов чем было в засаде." + "\n" + \
                           "В бой!"
                    if make_fight(atr[2] + atr[0], 90):
                        return make_response(text, state={'location': 40, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
                else:
                    text = "В лагере оказалось ещё больше гоблинов чем было в засаде." + "\n" + \
                           "Хорошо, что вы не один! В бой!"
                    if make_fight(atr[2] + atr[0], 80):
                        return make_response(text, state={'location': 40, 'type_hero': type_hero, 'atr': atr,
                                                          'old_location': location}, buttons=[
                            button('В бой!', hide=True),
                        ])
            if user_message == 'Разрушить плотину':
                text = "Вы разрушаете плотину и лагерь гоблинов смывает водой." + "\n" + \
                       "Ответственность за разрушение плотины капитан Далин берёт на себя." + \
                       " Вы получаете в награду за свою помощь новую броню эльфийской работы." + "\n" + \
                       " Ваше здоровье увеличилось на 20 очков." + "\n" + \
                       " Хотите ли вы закончить своё путешествие?"
                if old_location != 39:
                    atr[0] += 20
                return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Да', hide=True),
                    button('Нет', hide=True),
                ])

        if location == 39:
            text = "Пока что - это конец!"
            return end_work(text, event)
        if location == 40:
            text = "Вам удалось выстоять под тяжёлым натисков гоблинов." + "\n" + \
                   "После зачистки лагеря вы находите раненого камандира Далина, к счастью " + \
                   "рана не смертельна"
            return make_response(text, state={'location': 39, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Да', hide=True),
                button('Нет', hide=True),
            ])

        if location == 70:
            text = '''- Эй ты, не спишь?
Вокруг раздавались звуки копыт и тихое завывание холодного северного ветра. Бродячий цирк никогда не прекращал своего движения,
и сейчас его дорога лежала в небольшой тихий городок Прехивиль, окружённый высокими горными хребтами.
Вы ехали уже долгое время, однако заговорил хоть кто-то лишь сейчас.
- Мы уже почти на месте, - окликнул вас попутчик - выпусник коллегии бардов, присоединившийся к труппе недавно. Повозка остановилась
и вы ступили на улицы Прехевиля. Сам город не был особо примечательным, но гроты в скалах, когда-то использовавшиеся в
качестве гробниц и святилищ, могли представлять интерес. Но больше вас интересовало, можно ли здесь разузнать
какую-либо информацию о пропавшем вашем брате. Несмотря на долгие годы поисков, ваша надежда найти его не угасает.
- Нечего прохлаждаться! Ещё успеешь осмотреться, лучше подготовь свои фокусы. Думаю, в твоём запасе найдётся, чем удивить
местный люд.
Гоблин Пакваджи, трюкач труппы, усмехнувшись, пошёл в сторону повозки. Он прав, нужно подготовиться к выступлению.
'''
            return make_response(text, state={'location': 71, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Пойти за Пакваджи', hide=True),
                button('Зайти в таверну', hide=True),
            ])
        if location == 71:
            if user_message == 'Зайти в таверну':
                text = '''Не обращая внимания на бурчание Пакваджи, вы решаете пойти в таверну. Времени до выступления
ещё полно. В таверне вас встречает шум разговоров, чей-то смех, запах еды и выпивки. Вечером в таких местах всегда много
народу. Вы решаете поговорить с трактирщиком.
- Добро пожаловать, путник. Не желаете чего нибудь? Еда, выпивка?'''
                return make_response(text, state={'location': 72, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Спросить о последних новостях', hide=True),
                    button('Уйти', hide=True),
                ])
        if location == 72:
            if user_message == 'Спросить о последних новостях':
                text = '''- Да какие тут новости? Пару пьных драк, да мелкие кражи. Город у нас тихий, событий почти нет.
Хотя недавно один фермер утверждал, что видел какие-то огни в пещерах, мол призраки ходят. Да только не верит ему никто,
преукрасить да приврать он горазд, так ещё и пьяница.'''
                return make_response(text, state={'location': 73, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Спросить о гротах', hide=True),
                    button('Уйти', hide=True),
                ])
            if user_message == 'Уйти':
                text = '''Попрощавшись с трактирщиком вы решаете  вернуться к повозке.
Вам нужно подготовиться к завтрашнему представлению.'''
                return make_response(text, state={'location': 74, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location})
        if location == 73:
            if user_message == 'Спросить о гротах':
                text = '''- Вокруг этих пещер много всяких историй и легенд ходит. Самая популярная легенда - о 
запечатанном в одном из подземелий цветке зла. Давным-давно жил один полководец, известный своей жестокостью. Во время
очередного своего похода он сжёг оду деревню до тла, никого в живых не осталось. Но неожиданно на пепелище полководец
заметил старика. Тот посмотрел на него сердито, и сказал, мол поплатишься ты за  свои злодеяния, твоя же злость тебя
и погубит. Полководец не воспринял в серьёз заявления старика и велел убить его, что и осуществилось. В эту же ночь
разошлась гроза бурная такой силы, коей раньше не видывали, и решил полководец со своими солдатами в гроту её переждать.
Тут то и вскрылось, что тот старик колдуном оказался: внезапно полководец упал замертво, а сквозь его сердце цветок
пророс, угольно чёрный, а серцевина - чистый рубин, кроваво алый. Все содаты, будто с ума сошли, стали биться друг 
сдругом насмерть, пытаясь достать этот рубин, так и перебили друг друга. Так полководец от собственной злобы погиб,
отравив ею своих солдат. Но, говорят, что в рубине цветка зла содержиться огромная сила, способная сделать его
обладателя невероятно могущественным, но не каждый сможет справиться со злобой внутри камня. Много кто пытался его найти,
но никому ещё не удавалось. Правда красивая легенда, а?'''
                return make_response(text, state={'location': 73, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location}, buttons=[
                    button('Уйти', hide=True),
                ])
            if user_message == 'Уйти':
                text = '''Попрощавшись с трактирщиком вы решаете  вернуться к повозке.
Вам нужно подготовиться к завтрашнему представлению.'''
                return make_response(text, state={'location': 74, 'type_hero': type_hero, 'atr': atr,
                                                  'old_location': location})
        if location == 74:
            text = '''Ночью случился настоящий переполох. На город напала восставшая нежить.
Стража города отбивалась изо всех сил и под утро им удалось очистить город. Жители города в ужасе. Предположительно,
мертвецы полезли из древних захоронений в гротах, но, несмотря на щедрую оплату, никто не решался спуститься в подземелья,
чтобы успокоить мёртвых и найти причину их восстания. Вы вызыватесть добровольцем. Перед спуском в подземелья, вы решаете 
сходить на рынок и запастись на последок'''
            return make_response(text, state={'location': 75, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('Едой', hide=True),
                button('Лекарствами', hide=True),
                button('Магическими артефактами', hide=True),
            ])
        if location == 75:
            if user_message == 'Лекарствами':
                text = '''Вы приобрели зелье лечения. Теперь вы чувствуете, что готовы к тому, что ждёт вас в
подземельях.'''
                main_baff.append('зелье лечения')
            if user_message == 'Магическими артефактами':
                text = '''Вы приобрели кулон Скрытого глаза. Ваша ловкость повышена на 5 очков. Теперь вы 
чувствуете, что готовы к тому, что ждёт вас в подземельях.'''
                atr[2] += 5
            if user_message == 'Едой':
                text = '''На голодный желудок ничего путного не выйдет. Вы приобрели вяленое мясо. Теперь вы
чувствуете, что готовы к тому, что ждёт вас в подземельях.'''
                main_baff.append('мясо')
            return make_response(text, state={'location': 76, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location})
        if location == 76:
            '''Вы входите в подземелья. Кромешная тьма расступается перед светом вашего факела. Вдруг в углу вы
замечаете чьё-то движение. Рыча, в свете факела появился иссохшое мумифицированное тело мертвеца. В его пустых глазницах
горел потусторонний огонь. Вам придётся вступить с ним в бой.'''
            return make_response(text, state={'location': 77, 'type_hero': type_hero, 'atr': atr,
                                              'old_location': location}, buttons=[
                button('В бой!', hide=True),
            ])
        text = "Пока что - это конец!"
        return end_work(text, event)
    return make_response(text, state={'location': 0, 'type_hero': type_hero, 'atr': atr, 'old_location': 0},
                         buttons=[
                             button('Да', hide=True),
                             button('Нет', hide=True)
                         ])


if __name__ == '__main__':
    app.run()
