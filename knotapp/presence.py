from django.core.cache import cache

PRESENCE_TTL = 90  

def mark_online(user_id):
    cache.set(f'presence:{user_id}', True, timeout=PRESENCE_TTL)

def mark_offline(user_id):
    cache.delete(f'presence:{user_id}')

def is_online(user_id):
    return bool(cache.get(f'presence:{user_id}', False))

def bulk_online_status(user_ids):
    user_ids = list(user_ids)
    keys = {f'presence:{uid}': uid for uid in user_ids}
    found = cache.get_many(keys.keys())
    online_ids = {keys[k] for k in found}
    return online_ids