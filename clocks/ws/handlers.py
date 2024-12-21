from .base_action import BaseAction


class ActionHandler:
    def __init__(self):
        self._actions = {}

    def register(self, name, action):
        """Регистрация нового действия"""
        if not issubclass(action, BaseAction):
            raise TypeError("Action must be a subclass of BaseAction")
        self._actions[name] = action

    def get_action(self, name):
        """Получить действие по имени"""
        return self._actions.get(name)

    async def execute(self, name, consumer, data):
        """Выполнить действие"""
        action = self.get_action(name)
        if action:
            return await action.execute(consumer, data)
        return {"error": "Invalid action"}
