from django import forms
from django.forms import ModelForm
from web.models import SiteUser, Post


class SigninForm(forms.Form):
    username = forms.CharField(
        label=u"아이디",
        widget=forms.TextInput(
            attrs={
                "placeholder": u"아이디",
                "autocapitalize": "none",
                "autocorrect": "off",
            }
        ),
    )
    password = forms.CharField(
        label=u"비밀번호", widget=forms.PasswordInput(attrs={"placeholder": u"비밀번호"})
    )


class PostForm(ModelForm):
    class Meta:
        model = Post
        # Post 모델의 정보 항목들(필드) 중에서 글을 작성할 때 사용자가 입력하는 값이 아닌 항목들을 제외
        exclude = ["is_notice", "date_created", "date_modified", "views"]
        # widgets = {"board": forms.HiddenInput(), "author": forms.HiddenInput()}
