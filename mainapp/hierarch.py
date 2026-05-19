from collections import deque
from mainapp.models import ERPUser

def up_line_id(user_id):
    """
    Specific user_id er jonno database theke referred_by id niye asbe.
    All users loop na kore direct lookup kora hoyeche ($O(1)$ DB hit).
    """
    try:
        user = ERPUser.objects.get(id=user_id)
        return user.referd_by  # Apnar model-e 'referd_by' nam diyechilen
    except ERPUser.DoesNotExist:
        return None


def define_hierarchy(start_id):
    """
    Upline hierarchy generator.
    """
    up_line = deque()
    current_id = start_id
    
    while current_id:
        up_line.append(current_id)
        # Poroborti upline user id niye asa hobe
        current_id = up_line_id(current_id)
        
        # Infinite loop theke bachar jonno (jodi keu nijekeo refer kore thake)
        if current_id in up_line:
            break
            
    return list(up_line)  # Enqueue/Deque sesh hole list akare return kora bhalo