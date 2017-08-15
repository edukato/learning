import vk

from ..command_system import Command
from ...models import Client, Service

def plan(domain):
   client = Client.query.filter(Client.social_network == 'https://vk.com/'+ domain['domain']).first()
   if client:
      if client.plan:
         plan = Service.query.filter(Service.id == client.plan).first()
         message = 'Твой тарифный план - '+(plan.name)
      else:
         message = 'Пока тарифного плана нет, его можно приобрести на сайте'
   else:
      message = 'Прости, но это доступно только для клиентов. Если ты уже клиент, то пожалуйста зайди на http://edukato.ru/chat-bot и укажи адрес страницы'
   return message, ''

plan_command = Command()

plan_command.keys = ['план', 'тариф', 'тарифный план', 'план тарифный']
plan_command.description = 'Покажу твой тарифный план *'
plan_command.process = plan