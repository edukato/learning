from ..command_system import Command, command_list


def help(domain):
   message = 'Все очень просто: вот что я могу:\n'
   for c in command_list:
      message += c.keys[0] + ' - ' + c.description + '\n'
   message += '* - доступно только для клиентов'
   return message, ''

help_command = Command()

help_command.keys = ['помоги', 'сложна', 'помощь', 'help']
help_command.description = 'Покажу список команд'
help_command.process = help