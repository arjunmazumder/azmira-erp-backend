from mainapp.models import ERPUser

def up_line_id(user_id):
    try:
        user = ERPUser.objects.get(id=user_id)
        if user.referred_by is None:
            return None
        return user.referred_by_id  
    except ERPUser.DoesNotExist:
        return None


def define_hierarchy(start_id):
    up_line = []
    current_id = start_id

    while current_id:
        try:
            user = ERPUser.objects.get(id=current_id)
            up_line.append({
                "user_id": user.id,
                "is_active": user.is_active
            })
        except ERPUser.DoesNotExist:
            break
        
        current_id = up_line_id(current_id)
        
        if current_id is None:
            break
            
    return up_line