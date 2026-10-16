# Análisis de las respuestas de la IA (paso 6–7) — `duel --source ai`: 3 de 8

| Pregunta | Veredicto | Clasificación del fallo | Evidencia |
|---|---|---|---|
| q1 publicados | ✔ correcta (1) | — | igual que la del equipo |
| q2 sin categoría | ✔ correcta (1) | — | igual que la del equipo |
| q3 rango 1 mar–31 may | ✘ faltan 2 | **borde**: `__gt`/`__lt` excluyen los bordes | SQL: `WHERE published_at > 2026-03-01 AND published_at < 2026-05-31`; pierde «Introducción…» (3/1) y «Reseña…» (31/5). El equipo usa `__range` (BETWEEN inclusivo) |
| q4 +2 comentarios | ⚠ correcta pero cara (16) | **cara**: filtra en Python (`post.comments.count()` por artículo: 1 + 15) | duelo: «16 consultas; una buena necesita 1». El equipo anota `Count` y filtra en BD (1) |
| q5 top3 + conteos | ✘ (18,18) vs (6,3) | **conteos multiplicados**: `Count` sin `distinct` sobre el producto comentarios×etiquetas (6×3=18 filas) | SQL: un solo `LEFT JOIN` a comments y a tags con `COUNT()` sin DISTINCT; además cambia el orden (QuerySets 12 > Managers 8). El equipo usa `distinct=True` |
| q6 autores de Perú | ✘ error | **campo inventado**: `author__country` no existe | `FieldError: Unsupported lookup 'country'...`. El país vive en `Profile`: `author__profile__country` |
| q7 comentarios Tecnología | ✔ correcta (1) | — | igual que la del equipo |
| q8 nunca publicaron | ✘ falta Diego, sobra Ana | **significado**: `filter(posts__published=False)` = «tiene algún borrador» ≠ «nunca publicó» | Ana tiene 1 borrador y aparece; Diego (0 artículos) falta. El equipo usa `exclude(posts__published=True).distinct()` |

Intentos del equipo: Q1–Q8 verdes al primer intento (1 consulta cada una).
Paso 8 (pedir las 8 a un asistente desde cero): omitido, sin asistente autorizado por el docente.
