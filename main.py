from chat_messages.models import Message, MessageStatus
from django.db.models import Q

def get_messages_until_condition(friendship_id, user_id):
    filtered_messages = []

    while True:
        messages = Message.objects.filter(
            Q(sender_id=user_id) | Q(receiver_id=user_id),  
            friendship_id=friendship_id  
        ).order_by('-created_at').iterator()

        for message in messages:
            if message.sender_id == user_id or message.statuses.is_received:
                return filtered_messages
            message.statuses.is_received = True
            message.statuses.save()
            filtered_messages.append(message.content)

    return filtered_messages

print(get_messages_until_condition("40b62aca-e7c2-5661-a729-3c171c4c0b59", "210b7748-62b2-53c5-96cf-b332cb3bcc60"))
print("h666666666666666666666666i")
