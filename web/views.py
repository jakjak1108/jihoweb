import logging
import urllib
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotAllowed,
    Http404,
    HttpResponseForbidden,
    HttpResponseBadRequest,
)

from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from web.models import SiteUser, Board, Post
from web.forms import SigninForm, PostForm

logger = logging.getLogger(__name__)

# 모든 페이지는 django generic view를 활용하여 작성
# Django Class-based views: https://docs.djangoproject.com/en/3.0/topics/class-based-views/


class HomeView(TemplateView):
    # 메인 페이지
    template_name = "index.html"
    model = Board


class SigninFormView(FormView):
    form_class = SigninForm
    template_name = "registration/signin.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("home"))
        self.next = request.GET.get("next", None)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.next:
            context["next"] = urllib.parse.quote(self.next.encode("utf8"))
        return context

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        try:
            user = SiteUser.objects.get(username=username)
        except ObjectDoesNotExist as e:
            msg = u"이메일을 다시 확인하거나 회원가입 해주세요"
            form._errors["username"] = form.error_class([msg])
            return self.form_invalid(form)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                # Redirect to a success page.
                if self.next:
                    return HttpResponseRedirect(self.next)
                return HttpResponseRedirect(reverse("home"))
            else:
                # Return a 'disabled account' error message
                messages.error(self.request, u"사용 제한된 회원입니다")
                return self.render_to_response(self.get_context_data(form=form))
        else:
            # Return an 'invalid login' error message.
            msg = u"비밀번호가 일치하지 않습니다"
            form._errors["password"] = form.error_class([msg])
            return self.render_to_response(self.get_context_data(form=form))


class BoardListView(ListView):
    # 게시판 목록 페이지
    model = Board


class BoardDetailView(DetailView):
    # 게시판 상세 페이지
    model = Board


class PostDetailView(DetailView):
    # 게시글 상세 페이지
    model = Post
    # context_object_name = "post" # model의 이름이 object의 기본 이름이 되어 template에서 사용 됨
    # template_name = "codiz2/post_detail.html" # 기본 이름 규칙 <app name>/<model name>_detail.html

    def get_context_data(self, **kwargs):
        """웹 페이지에 보낼 데이터 세팅"""
        context = {}
        # context에 메뉴바에 표시될 게시판 리스트 정보 추가
        context["board_list"] = Board.objects.all()
        # kwargs로 넘어온 context 정보가 있으면 context object에 추가
        context.update(kwargs)
        return super().get_context_data(**context)


class PostCreateView(CreateView):
    # 게시글 작성 페이지
    model = Post
    form_class = PostForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
