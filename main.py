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
    if 'request' in event and \
            'original_utterance' in event['request'] \
            and len(event['request']['original_utterance']) > 0:
        state = event.get('state').get(STATE_RQUEST_KEY, {})
        intents = event['request'].get('nlu', {}).get('intents')
        location = state.get('location')
        user_message = "".join(str(event['request']['original_utterance']).split("."))
        if location == 0:
            if user_message == 'Да' or 'Yes' in intents:
                text = create_hero()
                return make_response(text, state={'location': 1},
                                     buttons=[
                                         button('Воин', hide=True),
                                         button('Лучник', hide=True),
                                         button('Маг', hide=True)
                                     ])
            else:
                text = say_goodbye()
                return end_work(text, event)
        text = "Пока что - это конец!"
        return end_work(text, event)
    return make_response(text, state={'location': 0},
                         buttons=[
                             button('Да', hide=True),
                             button('Нет', hide=True)
                         ])


if __name__ == '__main__':
    app.run()