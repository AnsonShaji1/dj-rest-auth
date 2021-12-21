from allauth.account.adapter import DefaultAccountAdapter
from .models import UserRole

class DefaultAccountAdapterCustom(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from allauth.account.utils import user_field

        user = super().save_user(request, user, form, False)
        user_field(user, 'employee_code', request.data.get('employee_code', ''))
        user_field(user, 'first_name', request.data.get('first_name', ''))
        user_field(user, 'last_name', request.data.get('last_name', ''))
        # user_field(user, 'employee_role', request.data.get('employee_role', ''))
        user_field(user, 'status', request.data.get('status', ''))
        user.employee_role = UserRole.objects.get(id=int(request.data['employee_role']))
        user.save()
        return user