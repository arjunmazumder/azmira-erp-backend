def generate_access_control(user):
   
    user_roles = []
    
    # ১. রোলস ফিল্ড প্রসেস করার নিরাপদ উপায় (লিস্ট বা স্ট্রিং চেক করা)
    if user.roles:
        if isinstance(user.roles, list):
            # যদি অলরেডি লিস্ট হয় (যেমন: ['admin', 'manager'])
            user_roles = [str(r).strip() for r in user.roles if r]
        else:
            # যদি স্ট্রিং হয় (যেমন: 'admin, manager')
            user_roles = [r.strip() for r in str(user.roles).split(',') if r.strip()]
            
    access_control = {}

    # 👑 ২. অ্যাডমিন বা সুপার অ্যাডমিন হলে সরাসরি ফুল পারমিশন বাইপাস করা
    if 'admin' in user_roles or 'super_admin' in user_roles:
        all_modules = [
            'project', 'plot', 'booking', 'installment', 'receipt', 
            'commission', 'wallet', 'lead', 'attendance', 'payroll', 
            'investment', 'dividend', 'officer_request', 'document', 'offer'
        ]
        for module in all_modules:
            access_control[module] = {
                "view": True,
                "create": True,
                "edit": True,
                "delete": True,
                "scope": "all"  # অ্যাডমিন সব ডেটা দেখবে
            }
            
    # 👥 ৩. সাধারণ ইউজার হলে api_permissions থেকে পারমিশন প্রসেস করা
    else:
        try:
            # একই ফোল্ডারে থাকায় রিলেটিভ ইমপোর্ট ব্যবহার করা হয়েছে
            from .api_permissions import get_role_permissions 
            
            for role in user_roles:
                role_perms = get_role_permissions(role)  # ক্যাশ বা ডিবি হেল্পার থেকে আসে
                
                if not role_perms:
                    continue
                    
                for codename, scope in role_perms.items():
                    # 'booking.view' -> module='booking', action='view'
                    if '.' in codename:
                        module, action = codename.split('.', 1)
                    else:
                        continue
                    
                    # মডিউল অবজেক্ট ডিকশনারিতে না থাকলে ইনিশিয়াল করা
                    if module not in access_control:
                        access_control[module] = {
                            "view": False, 
                            "create": False, 
                            "edit": False, 
                            "delete": False, 
                            "scope": "own"
                        }
                    
                    # অ্যাকশন ট্রু করা
                    if action in access_control[module]:
                        access_control[module][action] = True
                    
                    # স্কোপ মার্জ করা ('all' প্রায়োরিটি পাবে)
                    if scope == 'all':
                        access_control[module]["scope"] = 'all'
                    elif scope == 'own' and access_control[module]["scope"] != 'all':
                        access_control[module]["scope"] = 'own'
                        
        except (ImportError, NameError):
            # কোনো কারণে ফাইল বা ফাংশন না পাওয়া গেলে ক্র্যাশ এড়াতে খালি ডিকশনারি পাস করবে
            pass

    return access_control