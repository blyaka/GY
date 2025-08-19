from allauth.account.forms import SignupForm
from django import forms

class SignupForm(SignupForm):
    full_name = forms.CharField(label='ФИО', max_length=150, required=False)

    def save(self, request):
        user = super().save(request)
        fio = self.cleaned_data.get('full_name', '')
        if hasattr(user, 'profile'):
            user.profile.full_name = fio
            user.profile.save()
        return user
