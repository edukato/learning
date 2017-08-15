import datetime

from ..command_system import Command
from ...models import Client, Schedule, Teacher, Subject
from ...utils import awesome_date

def next_lesson(domain):
   client = Client.query.filter(Client.social_network == 'https://vk.com/'+ domain['domain']).first()
   schedule = Schedule.query.filter((Schedule.client_id == client.id) & (Schedule.time > datetime.datetime.now())).all()

   if client:
      if schedule:
         teacher = Client.query.get_or_404(Teacher.query.get_or_404(schedule[-1].teacher_id).login_id)
         subject = Subject.query.get_or_404(schedule[-1].subject_id)
         message = 'Немного информации о следующем заняии:\n'+'Оно пройдет '+awesome_date(schedule[-1].time)+'\nПреподаватель - '+teacher.first_name+' '+teacher.last_name
      else:
         message = 'Кхм... А следующего занятия нет. Если ты считаешь, что это ошибка, то напиши, пожалуйста, в поддержку.'
   else:
      message = 'Прости, но это доступно только для клиентов. Если ты уже клиент, то пожалуйста зайди на http://edukato.ru/chat-bot и укажи адрес страницы'
   return message, ''

next_lesson_command = Command()

next_lesson_command.keys = ['следующее занятие', 'когда следующее занятие', 'когда следующий урок', 'урок следующий', 'занятие следующее']
next_lesson_command.description = 'Расскажу о следующем занятии *'
next_lesson_command.process = next_lesson