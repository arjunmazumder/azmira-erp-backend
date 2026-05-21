from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import ERPPermission

@api_view(['GET'])
@permission_classes([AllowAny])
def force_seed_permissions(request):
    # ১. প্রথমে যদি টেবিলে পুরনো কোনো আবর্জনা ডাটা থাকে তা পরিষ্কার করা
    ERPPermission.objects.all().delete()
    
    # ২. আপনার মডেল থেকে মডিউল এবং অ্যাকশন চয়েসগুলো নেওয়া
    modules = [choice[0] for choice in ERPPermission.MODULE_CHOICES]
    actions = [choice[0] for choice in ERPPermission.ACTION_CHOICES]
    
    created_list = []
    
    # ৩. সরাসরি ডাটাবেজে নতুন অবজেক্ট ক্রিয়েট করা
    for module in modules:
        for action in actions:
            # bulk_create বা সরাসরি create ব্যবহার করা হচ্ছে
            obj = ERPPermission.objects.create(
                module=module,
                action=action,
                codename=f"{module}.{action}", # আপনার কোডনেম ফরম্যাট
                description=f"Can {action} {module}"
            )
            created_list.append(f"{module}.{action}")

    return Response({
        "status": "Success",
        "message": f"সরাসরি রানিং ডাটাবেজে {len(created_list)}টি পারমিশন ফোর্স-রাইট করা হয়েছে।",
        "inserted_permissions": created_list
    })