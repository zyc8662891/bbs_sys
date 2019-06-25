from django import forms
from appo.models import User


def check_name(username):
    print(username)
    user = User.objects.filter(username=username)
    print(user)
    if user:
        return '•用户已存在'
    return 'OK'

class CheckForm(forms.Form):
    username = forms.CharField(max_length=10,min_length=3)
    telephone = forms.CharField(max_length=11,min_length=11)
    password = forms.CharField(max_length=100)
    re_password = forms.CharField(max_length=100)
    email = forms.CharField(max_length=23)


    def clean_username(self):
        cleaned_username = self.cleaned_data.get('username')
        return cleaned_username

    # def clean_password(self):
    #     cleaned_password = self.cleaned_data.get('password')
    #     return cleaned_password
    #
    # def clean_re_password(self):
    #     cleaned_re_password = self.cleaned_data.get('re_password')
    #     return cleaned_re_password











