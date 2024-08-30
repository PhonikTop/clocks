import json

from channels.generic.websocket import AsyncWebsocketConsumer


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get("action")

        if action == "refresh_participants":
            participants = await self.get_participants()
            votes = await self.get_votes()
            await self.send(text_data=json.dumps({
                "participants": participants,
                "votes": votes
            }))
        elif action == "submit_vote":
            user_id = text_data_json.get("user_id")
            vote = text_data_json.get("vote")
            # Здесь нужно реализовать логику сохранения голоса в базу данных или другой источник
            print(f"Received vote: user_id={user_id}, vote={vote}")
            # Отправьте обновлённые данные голосов
            votes = await self.get_votes()
            await self.send(text_data=json.dumps({
                "votes": votes
            }))
        else:
            await self.send(text_data=json.dumps({
                "message": "unknown action"
            }))

    async def get_participants(self):
        # Пример получения участников
        return [
            {"username": "user1", "role": "Observer", "status": "Waiting"},
            {"username": "user2", "role": "Voter", "status": "Voted"}
        ]

    async def get_votes(self):
        # Пример получения голосов
        return {
            "meeting1": [
                {"user__username": "user1", "vote": "5"},
                {"user__username": "user2", "vote": "3"}
            ]
        }
