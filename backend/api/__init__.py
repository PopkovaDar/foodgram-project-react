"""Миграций тут нет так как проект изначально писала на posrgres."""
"""Поэтому миграции оказывались в контейнере(или в volumes =)."""
"""Командой docker compose exec backend python manage.py makemigrations."""
"""Вне контейнера применить миграции postgres не получается."""

"""Кажется, я не указала в проекте домен помимо файла .env."""
"""http://foodproject.servehttp.com ."""
