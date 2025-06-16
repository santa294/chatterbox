import random
import datetime
import json

MALE_FIRST_NAMES = ['Александр', 'Роман', 'Евгений', 'Иван', 'Максим', 'Дмитрий', 'Сергей', 'Николай', 'Константин', 'Михаил']
FEMALE_FIRST_NAMES = ['Софья', 'Анастасия', 'Виктория', 'Ксения', 'Арина', 'Елизавета', 'Ирина', 'Елена', 'Полина', 'Дарья']
LAST_NAMES = ['Люков', 'Смирнов', 'Петров', 'Сидоров', 'Кузнецов', 'Попов', 'Васильев', 'Соколов', 'Михайлов', 'Новиков']
CITIES = ['Москва', 'Петербург', 'Воронеж', 'Екатеринбург', 'Казань', 'Нижний Новгород', 'Челябинск', 'Самара', 'Omsk', 'Rostov-on-Don']
POSITIONS = ['Сотрудник поддержки', 'ТЛ', 'Инженер', 'Аналитик', 'Программист', 'Дизайнер', 'Бухгалтер', 'Юрист']
USER_MESSAGES = [
    "Я слишком долго жду ответа.",
    "Ваш сотрудник не выслушал мою проблему.",
    "Меня несколько раз переводили между отделами.",
    "Оператор был груб со мной.",
    "Мне нужно решение моей проблемы.",
    "Я не могу связаться с живым человеком.",
    "Вы порекомендовали неподходящий продукт.",
    "Вы не выполнили свое обещание.",
    "Ваша служба не ориентирована на клиента.",
    "Ваша поддержка не соответствует моим потребностям."
]
OPERATOR_MESSAGES = [
    "Приношу извинения за задержку. Чем могу помочь?",
    "Сожалею, что вы так почувствовали. Давайте разберемся.",
    "Понимаю ваше разочарование. Я решу этот вопрос.",
    "Приношу извинения за неудобства.",
    "Позвольте мне найти решение для вас.",
    "Я переведу вас в нужный отдел.",
    "Я прослежу за выполнением.",
    "Ваше удовлетворение — наш приоритет.",
    "Я учту ваш отзыв."
]

class Person:
    next_id = 1

    def __init__(self, gender, first_name, last_name, patronymic, city, date_of_birth, position, work_experience):
        self.id = Person.next_id
        Person.next_id += 1
        self.gender = gender
        self.first_name = first_name
        self.last_name = last_name
        self.patronymic = patronymic
        self.full_name = f"{last_name} {first_name} {patronymic}"
        self.city = city
        self.date_of_birth = date_of_birth
        self.position = position
        self.work_experience = work_experience

    def to_dict(self):
        return {
            'id': self.id,
            'gender': self.gender,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'patronymic': self.patronymic,
            'full_name': self.full_name,
            'city': self.city,
            'date_of_birth': self.date_of_birth.isoformat(),
            'position': self.position,
            'work_experience': self.work_experience
        }

class Operator(Person):
    def __init__(self, gender, first_name, last_name, patronymic, city, date_of_birth, position, work_experience):
        super().__init__(gender, first_name, last_name, patronymic, city, date_of_birth, position, work_experience)
        self.status = 'available'

class User(Person):
    pass

class Chat:
    next_id = 1

    def __init__(self, user, operator):
        self.id = Chat.next_id
        Chat.next_id += 1
        self.user_id = user.id
        self.operator_id = operator.id
        self.status = 'open'
        self.messages = []
        self.csat = None

    def add_message(self, sender, text, timestamp):
        self.messages.append({'sender': sender, 'text': text, 'timestamp': timestamp.isoformat()})

    def close(self):
        self.status = 'closed'

    def set_in_progress(self):
        if self.status == 'open':
            self.status = 'in_progress'
        else:
            raise ValueError("Нельзя изменить статус закрытого чата")

    def set_csat(self, score):
        if self.status == 'closed':
            self.csat = score
        else:
            raise ValueError("Нельзя установить CSAT для открытого чата")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'operator_id': self.operator_id,
            'status': self.status,
            'messages': self.messages,
            'csat': self.csat
        }

class Platform:
    def __init__(self):
        self.operators = []
        self.users = []
        self.chats = []

    def add_operator(self, operator):
        self.operators.append(operator)

    def add_user(self, user):
        self.users.append(user)

    def create_chat(self, user):
        available_operators = [op for op in self.operators if op.status == 'available']
        if not available_operators:
            raise Exception("Нет свободных операторов")
        operator = random.choice(available_operators)
        chat = Chat(user, operator)
        self.chats.append(chat)
        operator.status = 'busy'
        return chat

    def close_chat(self, chat):
        chat.close()
        operator = next(op for op in self.operators if op.id == chat.operator_id)
        operator.status = 'available'

    def set_csat(self, chat, score):
        chat.set_csat(score)

    def export_all_chats(self):
        return json.dumps([chat.to_dict() for chat in self.chats], indent=4, ensure_ascii=False)

    def export_chats_by_operator(self, operator_id):
        chats = [chat for chat in self.chats if chat.operator_id == operator_id]
        return json.dumps([chat.to_dict() for chat in chats], indent=4, ensure_ascii=False)

    def export_chats_by_user(self, user_id):
        chats = [chat for chat in self.chats if chat.user_id == user_id]
        return json.dumps([chat.to_dict() for chat in chats], indent=4, ensure_ascii=False)

    def export_operators(self):
        return json.dumps([op.to_dict() for op in self.operators], indent=4, ensure_ascii=False)

    def export_users(self):
        return json.dumps([user.to_dict() for user in self.users], indent=4, ensure_ascii=False)

    def generate_operators(self, n):
        for _ in range(n):
            operator = generate_person(Operator)
            self.add_operator(operator)

    def generate_users(self, n):
        for _ in range(n):
            user = generate_person(User)
            self.add_user(user)

def generate_person(cls):
    gender = random.choice(['male', 'female'])
    if gender == 'male':
        first_name = random.choice(MALE_FIRST_NAMES)
        patronymic = random.choice(MALE_FIRST_NAMES) + 'ович'
        last_name = random.choice(LAST_NAMES)
    else:
        first_name = random.choice(FEMALE_FIRST_NAMES)
        patronymic = random.choice(MALE_FIRST_NAMES) + 'овна'
        last_name = random.choice(LAST_NAMES) + 'a'
    city = random.choice(CITIES)
    year = random.randint(1950, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date_of_birth = datetime.date(year, month, day)
    position = random.choice(POSITIONS)
    work_experience = random.randint(0, 20)
    return cls(gender, first_name, last_name, patronymic, city, date_of_birth, position, work_experience)
