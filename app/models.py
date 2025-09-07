from django.db import models, transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class Source(models.Model):
    """
    Источник цитаты: фильм, книга и т.д.
    """
    KIND_CHOICES = [
        ("film", "Film"),
        ("book", "Book"),
        ("other", "Other"),
    ]
    name = models.CharField(max_length=255, unique=True)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default="other")

    def __str__(self):
        return f"{self.name} ({self.kind})"


class Quote(models.Model):
    """
    Цитата с весом, источником и счётчиком просмотров.
    """
    text = models.TextField(unique=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="quotes")
    weight = models.PositiveIntegerField(default=1)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["source"])]

    def clean(self):
        exists = Quote.objects.filter(source=self.source).exclude(pk=self.pk).count()
        if exists >= 3:
            raise ValidationError("У источника уже есть 3 цитаты.")
        if self.weight < 1:
            raise ValidationError("Вес должен быть >= 1.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.full_clean()
            return super().save(*args, **kwargs)

    @classmethod
    def increment_views(cls, pk: int):
        # безопасный инкремент просмотров
        return cls.objects.filter(pk=pk).update(views=F("views") + 1)


class Vote(models.Model):
    """
    Голос пользователя за цитату: +1 (like) или -1 (dislike).
    Гарантируем один голос на пару (user, quote).
    """
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = ((LIKE, "Like"), (DISLIKE, "Dislike"))

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quote_votes")
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="votes")
    value = models.SmallIntegerField(choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "quote"], name="uniq_vote_per_user_quote")
        ]
        indexes = [
            models.Index(fields=["quote"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"Vote(user={self.user_id}, quote={self.quote_id}, value={self.value})"
