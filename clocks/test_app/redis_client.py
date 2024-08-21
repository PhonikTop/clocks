import redis
import os

# Подключение к Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True  # Позволяет работать со строками вместо байтов
)


def save_url_to_redis(url, short_url):  # ttl=432000
    """Сохранение оригинальной и укороченной ссылки в Redis."""
    redis_client.hset('url_mapping', short_url, url)
    redis_client.hset('url_stats', short_url, 0)
    # redis_client.setex(f"url_mapping:{short_url}", ttl, url)
    # redis_client.setex(f"url_stats:{short_url}", ttl, 0)


def get_url_from_redis(short_url):
    """Получение оригинальной ссылки по укороченной."""
    return redis_client.hget('url_mapping', short_url)


def increment_url_stat(short_url):
    """Увеличение счетчика переходов по укороченной ссылке."""
    redis_client.hincrby('url_stats', short_url, 1)


def get_url_stats(short_url):
    """Получение количества переходов по укороченной ссылке."""
    return redis_client.hget('url_stats', short_url)


def get_all_urls():
    """Получение всех укороченных ссылок и их оригинальных версий."""
    return redis_client.hgetall('url_mapping')
