FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]

RUN python manage.py migrate
RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('логин', 'почта', 'пароль')" | python manage.py shell
