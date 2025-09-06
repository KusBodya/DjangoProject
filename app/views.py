# app/views.py
import random
from django.conf import settings
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, resolve_url, redirect
from django.views.decorators.http import require_POST
from .models import Quote, Vote
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

def quotes_list(request):
    quotes = Quote.objects.select_related("source").order_by("-created_at")
    return render(request, "quotes_list.html", {"quotes": quotes})


def random_quote(request):
    ids = list(Quote.objects.values_list("id", flat=True))
    quote = get_object_or_404(Quote, pk=random.choice(ids)) if ids else None
    likes = quote.votes.filter(value=Vote.LIKE).count() if quote else 0
    dislikes = quote.votes.filter(value=Vote.DISLIKE).count() if quote else 0
    return render(request, "random.html", {"quote": quote, "likes": likes, "dislikes": dislikes})


def _votes_ctx(q):
    return {
        "quote": q,
        "likes": q.votes.filter(value=Vote.LIKE).count(),
        "dislikes": q.votes.filter(value=Vote.DISLIKE).count(),
    }


def _ensure_auth_or_redirect(request):
    """
    Если пользователь не аутентифицирован:
    - для HTMX-запроса возвращаем HX-Redirect на страницу входа (полная навигация)
    - для обычного запроса отдаём обычный 302 редирект на страницу входа
    """
    if request.user.is_authenticated:
        return None
    login_url = resolve_url(settings.LOGIN_URL)
    if request.headers.get("HX-Request") == "true":
        resp = HttpResponse("", status=200)
        resp["HX-Redirect"] = login_url  # HTMX выполнит полный переход [4]
        return resp
    return HttpResponseRedirect(login_url)


@require_POST
def quote_like(request, pk):
    guard = _ensure_auth_or_redirect(request)
    if guard:
        return guard
    q = get_object_or_404(Quote, pk=pk)
    Vote.objects.update_or_create(user=request.user, quote=q, defaults={"value": Vote.LIKE})
    return render(request, "partials/quote_votes.html", _votes_ctx(q))  # partial обновит DOM [21]


@require_POST
def quote_dislike(request, pk):
    guard = _ensure_auth_or_redirect(request)
    if guard:
        return guard
    q = get_object_or_404(Quote, pk=pk)
    Vote.objects.update_or_create(user=request.user, quote=q, defaults={"value": Vote.DISLIKE})
    return render(request, "partials/quote_votes.html", _votes_ctx(q))  # partial обновит DOM [21]


@require_POST
def quote_view(request, pk):
    Quote.objects.filter(pk=pk).update(views=F("views") + 1)  # атомарный инкремент [22]
    q = get_object_or_404(Quote, pk=pk)
    return render(request, "partials/quote_views.html", {"quote": q})

def signup(request):
    if request.user.is_authenticated:
        return redirect("quotes_list")  # или "random_quote"
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("quotes_list")
    else:
        form = UserCreationForm()  # <— ВАЖНО: инициализируем для GET
    return render(request, "registration/signup.html", {"form": form})


from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef

@login_required
def liked_quotes(request):
    qs = Quote.objects.filter(votes__user=request.user, votes__value=Vote.LIKE).select_related("source").order_by("-created_at")
    return render(request, "quotes_list.html", {"quotes": qs})

@login_required
def unvoted_quotes(request):
    has_any_vote = Vote.objects.filter(user=request.user, quote=OuterRef("pk"))
    qs = Quote.objects.annotate(voted=Exists(has_any_vote)).filter(voted=False).select_related("source").order_by("-created_at")
    return render(request, "quotes_list.html", {"quotes": qs})