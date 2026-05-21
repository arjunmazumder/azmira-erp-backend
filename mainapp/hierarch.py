from collections import deque
from mainapp.models import ERPUser

def up_line_id(user_id):
 
    try:
        user = ERPUser.objects.get(id=user_id)
        return user.referred_by 
    except ERPUser.DoesNotExist:
        return None


def define_hierarchy(start_id):
   
    up_line = []
    current_id = start_id

    
    while current_id:
        up_line.append(current_id)
      
        current_id = up_line_id(current_id)
        
        if current_id is None:
            break
            
    return list(up_line)  