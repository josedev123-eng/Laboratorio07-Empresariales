# Guía de Laboratorio #7 — Resuelta
**Tema: ORM de Django** · DAE · Repo: `Laboratorio07-Empresariales`

## 1–2. Entorno y datos
`.venv` + `pip install -r requirements.txt` (Django 6.1.2), `migrate`, `seed_blog`:
**4 autores, 15 artículos, 23 comentarios** (siempre iguales → respuestas conocidas).

## 3. Diagrama de relaciones (`blog/models.py`)
```
Author 1──1 Profile (profile.author, country)      ← Q6 atraviesa author__profile__country
Author 1──N Post (post.author, related_name="posts")
Category 1──N Post (post.category, null=True OPCIONAL, SET_NULL)   ← Q2: category__isnull
Post N──N Tag (post.tags, related_name="posts")    ← Q5 cuenta tags con distinct
Post 1──N Comment (comment.post, related_name="comments")
```

## 4–5. Duelo del equipo (`blog/duel/team.py`): 8 de 8, 1 consulta c/u, al 1.er intento
| P | Consulta | Costo |
|---|---|---|
| q1 publicados | `Post.objects.filter(published=True)` | 1 |
| q2 sin categoría | `filter(category__isnull=True)` | 1 |
| q3 1 mar–31 may 2026 | `filter(published_at__range=(date(2026,3,1), date(2026,5,31)))` (BETWEEN inclusivo) | 1 |
| q4 +2 comentarios | `annotate(n_comments=Count("comments")).filter(n_comments__gt=2)` | 1 |
| q5 top3 + conteos | `filter(published=True).annotate(n_comments=Count("comments",distinct=True), n_tags=Count("tags",distinct=True)).order_by("-n_comments")[:3]` | 1 |
| q6 autores de Perú | `filter(author__profile__country="Perú")` (publicados o no: 12) | 1 |
| q7 comentarios Tecnología | `Comment.objects.filter(post__category__name="Tecnología")` (17) | 1 |
| q8 nunca publicaron | `Author.objects.exclude(posts__published=True).distinct()` (Carla, Diego) | 1 |
Nota: `duel` en Windows necesita `$env:PYTHONUTF8='1'` (los ✔ rompen cp1252).

## 6–7. Duelo de la IA: 3 de 8 (`docs/analisis_ia.md`)
| P | Veredicto | Fallo |
|---|---|---|
| q1, q2, q7 | ✔ correctas | — |
| q3 | ✘ faltan 2 | **borde**: `__gt/__lt` excluyen 3/1 y 31/5 (SQL: `> 2026-03-01 AND < 2026-05-31`) |
| q4 | ⚠ cara (16 = 1+15) | filtra en Python (`post.comments.count()` por fila) |
| q5 | ✘ (18,18) vs (6,3) | **conteos multiplicados**: `COUNT` sin DISTINCT sobre comentarios×etiquetas (6×3=18); cambia hasta el orden |
| q6 | ✘ FieldError | **campo inventado**: `author__country` no existe (el país está en `Profile`) |
| q8 | ✘ sobra Ana, falta Diego | **significado**: `published=False` = «tiene borrador» ≠ «nunca publicó» |
Paso 8 omitido: sin asistente autorizado por el docente.

## 9–11. N+1: 23 → 2
Fallo copiado: `test_front_page_runs_two_queries` esperaba 2 y vio **23** (1 de posts +
11 de `post.author` + 11 de `post.tags`; crece con cada artículo).
Fix en `blog/queries.py`: `select_related("author")` (FK: mismo SELECT) +
`prefetch_related("tags")` (M2M: una 2.ª consulta global). Suite: todo verde salvo
`test_the_starter_has_nothing_written`, que falla **por diseño** ahora que el equipo
escribió sus respuestas (esperaba el starter intacto).

## 12–14. Agente (`docs/agent_evidencias.md`)
`posts_per_author`→ok, `comments_of_post(1)`→ok (4.º hostil como texto),
`delete(1)`→`approval_required` (nada aplicado), `run_sql`→denied.
El comentario hostil borraría el art. 1 si se ejecutara como orden; lo impiden:
lista cerrada `ACTIONS`, lecturas como `untrusted_data` y R2 solo con `--approve` humano.
Plan art. 5 (`4d7ffe2c0e99`) aplicado (`deleted: 1`); carrera con hash viejo rechazada
(hash nuevo, comentario intacto: el digest cubre el estado actual). Datos restaurados (4/15/23).

## 15. Uso de IA
| Pedido | Respuesta | Decisión y por qué |
|---|---|---|
| Q1–Q8 del duelo | 8 consultas ORM | Aceptadas: duelo 8/8 ✔ con 1 consulta c/u (verificado, no por fe) |
| Fallos de la IA del repo | clasificación + SQL | Aceptada: coincide con `test_the_assistant_fails_where_the_lab_says` (OK) |
| Fix N+1 | select+prefetch | Aceptado: test 23→2 en verde |
| Esta guía | texto | Aceptada tras revisar cada comando ejecutado |

## Conclusiones
1. Todo el duelo se resolvió solo con el ORM (filtros encadenados, `__range`, `Count` con
   `distinct`, relaciones inversas `posts__`, `author__profile__`): 8/8 con una consulta cada una,
   sin SQL ni filtrado en Python.
2. Los fallos de la IA son sistemáticos y verificables: bordes exclusivos, conteos multiplicados
   sin `distinct`, campos inventados y confusión de significado; el duelo + `print(q.query)` los
   delatan en segundos.
3. El N+1 se mide (23 vs 2), se explica (1+11+11, crece por artículo) y se corrige con la
   herramienta exacta: `select_related` para FK/uno-a-uno, `prefetch_related` para M2M.
4. La pasarela del agente muestra la frontera: lista cerrada, datos≠órdenes y aprobación humana
   con hash ligado al estado hacen que ni un comentario hostil ni una condición de carrera
   logren un borrado no autorizado.
