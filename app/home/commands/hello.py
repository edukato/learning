from ..command_system import Command


def hello(domain):
   message = 'Привет, друг!\nЯ новый чат-бот.'
   return message, ''

hello_command = Command()

hello_command.keys = ['привет', 'hello', 'дратути', 'здравствуй', 'здравствуйте']
hello_command.description = 'Поприветствую тебя'
hello_command.process = hello