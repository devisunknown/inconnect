from django.core.cache import cache


def unread_key(user_id, chat_id):
    return f'unread:{user_id}:{chat_id}'


def get_unread_count(user_id, chat_id):
    count = cache.get(unread_key(user_id, chat_id))
    if count is None:
        from .models import Message
        count = Message.objects.filter(chat_id=chat_id, is_read=False).exclude(sender_id=user_id).count()
        cache.set(unread_key(user_id, chat_id), count, timeout=None)
    return count


def bulk_unread_counts(user_id, chat_ids):
    chat_ids = list(chat_ids)
    keys = {unread_key(user_id, cid): cid for cid in chat_ids}
    found = cache.get_many(keys.keys())
    result = {keys[k]: v for k, v in found.items()}
    missing = [cid for cid in chat_ids if cid not in result]
    if missing:
        from .models import Message
        rows = (
            Message.objects.filter(chat_id__in=missing, is_read=False)
            .exclude(sender_id=user_id)
            .values('chat_id')
            .annotate(cnt=__import__('django.db.models', fromlist=['Count']).Count('id'))
        )
        counts_by_chat = {r['chat_id']: r['cnt'] for r in rows}
        for cid in missing:
            cnt = counts_by_chat.get(cid, 0)
            result[cid] = cnt
            cache.set(unread_key(user_id, cid), cnt, timeout=None)
    return result


def increment_unread(user_id, chat_id):
    key = unread_key(user_id, chat_id)
    try:
        cache.incr(key)
    except ValueError:
        get_unread_count(user_id, chat_id)  


def clear_unread(user_id, chat_id):
    cache.set(unread_key(user_id, chat_id), 0, timeout=None)


def invalidate_unread(user_id, chat_id):
    cache.delete(unread_key(user_id, chat_id))