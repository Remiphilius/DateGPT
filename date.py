import os
from dotenv import load_dotenv
import openai
import tiktoken


def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}.
        See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages
        are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


class DateGPT:
    def __init__(self, accroche: str, model: str = "gpt-3.5-turbo-0301"):
        print(f"0 : {accroche}\n")
        load_dotenv('.env')
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.messages_users = {
            'system': {
                # 'user0': '''
                # Tu joues les rôle d'un homme en rendez-vous galant. Tu n'as encore jamais vu ton interlocutrice.
                # Tu devras séduire ton interlocutrice qui est une femme, notamment en lui parlant des carrières de Paris.
                # Tu dois seulement donner une phrase brève et courte.
                # N'oublie pas que tu dois accorder les mots pour toi au masculin et les mots pour ton interlocutrice au
                # féminin.
                # ''',
                # 'user1': '''
                # Tu joues les rôle d'une femme en rendez-vous galant. Tu n'as encore jamais vu ton interlocuteur.
                # Tu devras séduire ton interlocuteur qui est un homme, notamment en lui parlant d'ornithologie.
                # Tu dois seulement donner une phrase brève et courte.
                # N'oublie pas que tu dois accorder les mots pour toi au féminin et les mots pour ton interlocuteur au
                # masculin.
                # '''
                'user0': '''
                You act as an international cat.
                You meow using all the onomatopoeias that exist in the world.
                You will use as little as possible the same onomatopoeia that designates the sound of the cat.
                ''',
                'user1': '''
                You act as an international cat.
                You meow using all the onomatopoeias that exist in the world.
                You will use as little as possible the same onomatopoeia that designates the sound of the cat.
                '''
                       },
            'user0': [accroche],
            'user1': list()
        }

    def speak(self, messages: list) -> str:
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )
        message = completion.choices[0].message
        return message.get('content', '')

    def get_i_user(self) -> int:
        n_0 = len(self.messages_users.get('user0', list()))
        n_1 = len(self.messages_users.get('user1', list()))
        if n_0 > n_1:
            return 1
        else:
            return 0

    def rm_first_messages(self):
        user0 = self.messages_users['user0'][1:]
        user1 = self.messages_users['user1'][1:]
        self.messages_users['user0'] = user0
        self.messages_users['user1'] = user1

    def get_messages_user(self, i_user: int) -> list:
        user = f'user{i_user}'
        messages = [{'role': 'system', 'content': self.messages_users['system'][user]}]
        for u0, u1 in zip(self.messages_users['user0'], self.messages_users['user1']):
            message_turn = [
                {
                    'role': 'user' if i_user == 1 else 'assistant',
                    'content': u0
                },
                {
                    'role': 'assistant' if i_user == 1 else 'user',
                    'content': u1
                }
            ]
            messages.extend(message_turn)
        if i_user == 1:
            last_message_content = self.messages_users['user0'][-1]
            last_message = {
                'role': 'user',
                'content': last_message_content
            }
            messages.append(last_message)
        return messages

    def user_speak(self):
        i_user = self.get_i_user()
        messages = self.get_messages_user(i_user)
        while num_tokens_from_messages(messages, self.model) > 4096:
            self.rm_first_messages()
            messages = self.get_messages_user(i_user)
        reply = self.speak(messages)
        print(f"{i_user} : {reply}\n")
        user = f'user{i_user}'
        self.messages_users[user].append(reply)
