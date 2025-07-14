from rooms.services.message_senders.base import MessageSender


class CompositeMessageSender(MessageSender):
    def __init__(self):
        self._senders = []

    def add_sender(self, sender: MessageSender) -> None:
        """
        Добавляет отправителя в список отправителей.

        Args:
            sender (MessageSender): Объект, реализующий интерфейс MessageSender.
        """
        self._senders.append(sender)

    def send(self, group_name: str, message: dict) -> None:
        """
        Отправляет сообщение через всех зарегистрированных отправителей.

        Args:
            group_name (str): Имя группы.
            message (dict): Сообщение, которое нужно отправить.
        """
        for sender in self._senders:
            sender.send(group_name, message)
