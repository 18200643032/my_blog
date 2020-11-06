# @Time : 2020/11/5 18:52 
# @modele : forms
# @Author : zhengzhong
# @Software: PyCharm
from django import forms

from django.contrib.auth.models import User
from .models import Profile

#登录表单

class UserLoginForm(forms.Form):
    username  = forms.CharField()
    password = forms.CharField()


#注册表单
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ("username","email")

    def clean_password2(self):
        data = self.cleaned_data
        if data.get("password") == data.get("password2"):
            return data.get("password")
        else:
            raise forms.ValidationError("密码输入不一致")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone','avatar','bio')