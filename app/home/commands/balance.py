import vk

from ..command_system import Command
from ...models import Client

def balance(domain):
   client = Client.query.filter(Client.social_network == 'https://vk.com/'+ domain['domain']).first()
   if client:
      message = 'Твой баланс - '+str(client.balance)+'₽'
   else:
      message = 'Прости, но это доступно только для клиентов. Если ты уже клиент, то пожалуйста зайди на http://edukato.ru/chat-bot и укажи адрес страницы'
   return message, ''

balance_command = Command()

balance_command.keys = ['баланс', 'balance', 'сколько денег', 'сколько денег осталось', 'счёт']
balance_command.description = 'Покажу остаток средств на счете *'
balance_command.process = balance