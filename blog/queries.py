"""Queries behind the views. Part 2 of the lab happens in this file."""
from blog.models import Post


def posts_for_front_page():
    # select_related: author es FK (una fila por post, va en el mismo SELECT).
    # prefetch_related: tags es M2M (segunda consulta global, no una por post).
    # Antes: 1 + 11 + 11 = 23 consultas. Ahora: 2.
    return (
        Post.objects.filter(published=True)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-published_at")
    )
