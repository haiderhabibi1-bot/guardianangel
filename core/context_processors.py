def user_roles(request):
    """
    Makes it easy to know in every template whether the logged-in user
    is a lawyer or a customer.
    """
    user = request.user
    is_customer = False
    is_lawyer = False

    if user.is_authenticated:
        if hasattr(user, 'customer_profile'):
            is_customer = True
        if hasattr(user, 'lawyer_profile') and user.lawyer_profile.is_approved:
            is_lawyer = True

    return {
        'is_customer': is_customer,
        'is_lawyer': is_lawyer,
    }
