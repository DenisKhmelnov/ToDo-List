import logging

from django.core.management import BaseCommand

from todolist.bot.models import TgUser
from todolist.bot.tg.client import TgClient
from todolist.bot.tg.schemas import Message

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()

    def handle(self, *args, **options):
        offset = 0
        logger.info('Bot start handling')
        tg_client = TgClient()
        while True:
            res = tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message):
        tg_user, created = TgUser.objects.get_or_create(chat_id=msg.chat.id)
        logger.info(f'Created {created}')

        if tg_user.user:
            self.handle_authorized(tg_user, msg)
        else:
            self.handle_unauthorized(tg_user, msg)

    def handle_unauthorized(self, tg_user: TgUser, msg: Message):
        self.tg_client.send_message(msg.chat.id, 'Hello!')
        code = tg_user.set_verefication_code()
        self.tg_client.send_message(tg_user.chat_id, f'Your verification code: {code}')

    def handle_authorized(self, tg_user: TgUser, msg: Message):
        if msg.text == '/goals':
            # Get goals from the database
            goals = tg_user.user.goals.all()
            if goals:
                # Construct message with list of goals
                goals_list = '\n'.join([f'{i + 1}. {goal.title}' for i, goal in enumerate(goals)])
                message = f'Your goals:\n{goals_list}'
            else:
                message = 'You have no goals yet!'
        else:
            message = 'Unknown command!'

        # Send the response to the user
        self.tg_client.send_message(tg_user.chat_id, message)
        logger.info('Authorized')
