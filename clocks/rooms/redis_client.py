from django.core.cache import cache


class RoomCacheManager:
    def __init__(self, room_uuid, ttl=60 * 60 * 5):
        self.room_key = f"room:{room_uuid}"
        self.users_key = f"{self.room_key}:users"
        self.votes_key = f"{self.room_key}:votes"
        self.ttl = ttl

    def add_user(self, uuid, role, nickname, vote=None):
        user_key = f"user:{uuid}:data"

        cache.set(user_key, {"role": role, "nickname": nickname, "vote": vote}, timeout=self.ttl)

        uuids = cache.get(self.users_key, [])
        uuids.append(uuid)
        cache.set(self.users_key, uuids, timeout=self.ttl)

        if vote is not None:
            votes = cache.get(self.votes_key, {})
            votes[uuid] = {"nickname": nickname, "vote": vote}
            cache.set(self.votes_key, votes, timeout=self.ttl)

    def get_user(self, user_uuid):
        user_key = f"user:{user_uuid}:data"
        return cache.get(user_key)

    def remove_user(self, user_uuid):
        user_key = f"user:{user_uuid}:data"

        cache.delete(user_key)

        uuids = cache.get(self.users_key, [])
        if uuids and user_uuid in uuids:
            uuids.remove(user_uuid)
            cache.set(self.users_key, uuids, timeout=self.ttl)

    def get_room_users(self):
        uuids = cache.get(self.users_key, [])
        users_dict = {}
        for uuid in uuids:
            user_data = cache.get(f"user:{uuid}:data")
            users_dict[uuid] = user_data["role"]
        return users_dict

    def get_users_by_role(self, role):
        all_users = self.get_room_users()
        return [uuid for uuid, user_role in all_users.items() if user_role == role]

    def set_vote(self, user_uuid, vote):
        user_key = f"user:{user_uuid}:data"
        user_data = cache.get(user_key)
        if not user_data:
            raise ValueError("User not found")

        if user_data["role"] != "voter":
            raise ValueError("User is not allowed to vote")

        user_data["vote"] = vote
        cache.set(user_key, user_data, timeout=self.ttl)

        votes = cache.get(self.votes_key, {})
        votes[user_uuid] = {"nickname": user_data["nickname"], "vote": vote}
        cache.set(self.votes_key, votes, timeout=self.ttl)

    def get_votes(self):
        return cache.get(self.votes_key, {})

    def get_votes_dict(self):
        votes = cache.get(self.votes_key, {})
        return {uuid: data["vote"] for uuid, data in votes.items()}

    def clear_votes(self):
        cache.delete(self.votes_key)

    def clear_room(self):
        uuids = cache.get(self.users_key, [])
        for user_uuid in uuids:
            cache.delete(f"user:{user_uuid}:data")
        cache.delete(self.users_key)
        cache.delete(self.votes_key)
