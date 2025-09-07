from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import F, Count, Q, Exists, OuterRef
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, resolve_url, redirect
from django.views.decorators.http import require_POST
from random import choices

from .models import Quote, Vote


def _with_vote_counts(qs):
    return qs.annotate(
        likes_count=Count("votes", filter=Q(votes__value=Vote.LIKE)),
        dislikes_count=Count("votes", filter=Q(votes__value=Vote.DISLIKE)),
    )


def _apply_filters(request, qs):
    q = request.GET.get("q", "").strip()
    kind = request.GET.get("kind", "").strip()
    order = request.GET.get("order", "date")
    direction = request.GET.get("dir", "desc")

    if q:
        qs = qs.filter(source__name__icontains=q)
    if kind:
        qs = qs.filter(source__kind=kind)

    field_map = {"likes": "likes_count", "views": "views", "date": "created_at"}
    field = field_map.get(order, "created_at")
    return qs.order_by(field if direction == "asc" else f"-{field}", "-id")


def quotes_list(request):
    base = _with_vote_counts(Quote.objects.select_related("source"))
    top10 = base.order_by("-likes_count", "-created_at", "-id")[:10]
    qs = _apply_filters(request, base)
    return render(request, "quotes_list.html", {"quotes": qs, "top10": top10, "filters": request.GET})

def random_quote(request):
    rows = list(Quote.objects.values_list("id", "weight"))
    if not rows:
        return render(request, "random.html", {"quote": None})

    ids = [r[0] for r in rows]
    weights = [r[1] for r in rows]

    chosen_id = int(choices(ids, weights=weights, k=1)[0])
    quote = Quote.objects.select_related("source").get(pk=chosen_id)

    # quote = _with_vote_counts(Quote.objects.select_related("source").filter(pk=chosen_id)).first()
    return render(request, "random.html", {"quote": quote})

def _votes_ctx(q):
    return {
        "quote": q,
        "likes": q.votes.filter(value=Vote.LIKE).count(),
        "dislikes": q.votes.filter(value=Vote.DISLIKE).count(),
    }

def _ensure_auth_or_redirect(request):
    if request.user.is_authenticated:
        return None
    login_url = resolve_url(settings.LOGIN_URL)
    if request.headers.get("HX-Request") == "true":
        resp = HttpResponse("", status=200)
        resp["HX-Redirect"] = login_url
        return resp
    return HttpResponseRedirect(login_url)

@require_POST
def quote_like(request, pk):
    guard = _ensure_auth_or_redirect(request)
    if guard:
        return guard
    q = get_object_or_404(Quote, pk=pk)
    Vote.objects.update_or_create(user=request.user, quote=q, defaults={"value": Vote.LIKE})
    return render(request, "partials/quote_votes.html", _votes_ctx(q))

@require_POST
def quote_dislike(request, pk):
    guard = _ensure_auth_or_redirect(request)
    if guard:
        return guard
    q = get_object_or_404(Quote, pk=pk)
    Vote.objects.update_or_create(user=request.user, quote=q, defaults={"value": Vote.DISLIKE})
    return render(request, "partials/quote_votes.html", _votes_ctx(q))

@require_POST
def quote_view(request, pk):
    Quote.objects.filter(pk=pk).update(views=F("views") + 1)
    q = get_object_or_404(Quote, pk=pk)
    return render(request, "partials/quote_views.html", {"quote": q})

def signup(request):
    if request.user.is_authenticated:
        return redirect("quotes_list")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("quotes_list")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def liked_quotes(request):
    base = _with_vote_counts(Quote.objects.filter(votes__user=request.user, votes__value=Vote.LIKE).select_related("source"))
    qs = _apply_filters(request, base)
    return render(request, "quotes_list.html", {"quotes": qs, "filters": request.GET})


@login_required
def disliked_quotes(request):
    base = _with_vote_counts(Quote.objects.filter(votes__user=request.user, votes__value=Vote.DISLIKE).select_related("source"))
    qs = _apply_filters(request, base)
    return render(request, "quotes_list.html", {"quotes": qs, "filters": request.GET})

@login_required
def unvoted_quotes(request):
    has_any_vote = Vote.objects.filter(user=request.user, quote=OuterRef("pk"))
    base = _with_vote_counts(Quote.objects.annotate(voted=Exists(has_any_vote)).filter(voted=False).select_related("source"))
    qs = _apply_filters(request, base)
    return render(request, "quotes_list.html", {"quotes": qs, "filters": request.GET})
