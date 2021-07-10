from django.forms import ModelForm, TextInput, Textarea, Form, CharField, PasswordInput, ValidationError, EmailField, EmailInput
from django.contrib.auth.models import User
from .models import Post, Comment, Reply
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse



class SignUpForm(Form):
    username = CharField(widget=TextInput)
    enter_password = CharField(widget=PasswordInput)
    retype_password = CharField(widget=PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('The username has been already taken.')
        return username

    def clean_enter_password(self):
        password = self.cleaned_data.get('enter_password')
        if len(password) < 5:
            raise ValidationError('Password must contain 5 or more characters.')
        return password

    def clean(self):
        super(SignUpForm, self).clean()
        password = self.cleaned_data.get('enter_password')
        retyped = self.cleaned_data.get('retype_password')
        if password and retyped and (password != retyped):
            self.add_error('retype_password', 'This does not match with the above.')

    def save(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('enter_password')
        new_user = User.objects.create_user(username = username)
        new_user.set_password(password)
        new_user.save()



class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'text')
        widgets = {
            'author': TextInput(attrs={
                'class': 'form-control',
                'placeholder': '名前',
            }),
            'text': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'コメント内容',
            }),
        }
        labels = {
            'author': '',
            'text': '',
        }



class ReplyForm(ModelForm):
    class Meta:
        model = Reply
        fields = ('author', 'text')
        widgets = {
            'author': TextInput(attrs={
                'class': 'form-control',
                'placeholder': '名前',
            }),
            'text': Textarea(attrs={
                'class': 'form-control',
                'placeholder': '返信内容',
            }),
        }
        labels = {
            'author': '',
            'text': '',
        }


class ContactForm(Form):
    name = CharField(
        label='',
        max_length=100,
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': "お名前",
        }),
    )
    email = EmailField(
        label='',
        widget=EmailInput(attrs={
            'class': 'form-control',
            'placeholder': "メールアドレス",
        }),
    )
    message = CharField(
        label='',
        widget=Textarea(attrs={
            'class': 'form-control',
            'placeholder': "お問い合わせ内容",
        }),
    )

    def send_email(self):
        subject = "お問い合わせ"
        message = self.cleaned_data['message']
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        from_email = '{name} <{email}>'.format(name=name, email=email)
        recipient_list = [settings.EMAIL_HOST_USER]  # 受信者リスト
        try:
            send_mail(subject, message, from_email, recipient_list)
        except BadHeaderError:
            return HttpResponse("無効なヘッダが検出されました。")