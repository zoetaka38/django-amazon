from django.views import generic
from django.contrib.auth.views import LoginView
from ..forms import *
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest #[6-4]追加
from django.core.signing import BadSignature, SignatureExpired, dumps, loads #[6-4]追加
from django.urls import reverse #[6-4]追加
from django.contrib.sites.shortcuts import get_current_site #[6-4]追加
from django.template.loader import get_template #[6-4]追加
from django.contrib import messages #[6-4]追加
from django.conf import settings
from ..models import ShoppingCart


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'amazon/login.html'


class SignUp(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'amazon/sign_up.html'
    form_class = SignUpForm
   
    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject_template = get_template('amazon/mail_template/sign_up/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('amazon/mail_template/sign_up/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        messages.success(self.request, '本登録用リンクを送付しました')
        return  HttpResponseRedirect(reverse('amazon:sign_up'))


class SignUpDone(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'amazon/sign_up_done.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()

                    his_cart = ShoppingCart()
                    his_cart.user = user
                    his_cart.save()

                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()