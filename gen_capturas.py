"""Genera docs/capturas/*.png con salidas REALES de terminal del Lab07.
Uso: .venv\\Scripts\\python gen_capturas.py (requiere datos seed y queries.py con fix).
El caso 'rojo' revierte temporalmente blog/queries.py vía git stash.
"""
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
CAP = ROOT / 'docs' / 'capturas'
CAP.mkdir(parents=True, exist_ok=True)
PY = str(ROOT / '.venv' / 'Scripts' / 'python.exe')
ENV = {**os.environ, 'PYTHONUTF8': '1'}


def raw(args):
    p = subprocess.run([PY, 'manage.py', *args], capture_output=True, text=False,
                       env=ENV, cwd=ROOT, timeout=300)
    return (p.stdout + p.stderr).decode('utf-8', errors='replace').replace('\r\n', '\n').strip()


def run(args, tail=None):
    lines = raw(args).split('\n')
    if tail:
        lines = ['[...]'] + lines[-tail:]
    return '\n'.join(lines)


def shot(name, title, text):
    text = text.replace('✔', '[OK]').replace('✘', '[X]').replace('⚠', '[!]')
    try:
        font = ImageFont.truetype('consola.ttf', 15)
    except OSError:
        try:
            font = ImageFont.truetype('DejaVuSansMono.ttf', 14)
        except OSError:
            font = ImageFont.load_default()
    pad, lh = 14, 20
    raw = [f'$ {title}'] + text.split('\n')
    wrapped = []
    for line in raw:
        while len(line) > 100:
            wrapped.append(line[:100])
            line = line[100:]
        wrapped.append(line)
    tmp = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    w = max(int(tmp.textlength(l, font=font)) for l in wrapped) + pad * 2
    img = Image.new('RGB', (w, lh * len(wrapped) + pad * 2), (12, 12, 12))
    d = ImageDraw.Draw(img)
    y = pad
    for i, line in enumerate(wrapped):
        color = (86, 156, 214) if i == 0 else (220, 220, 220)
        d.text((pad, y), line, font=font, fill=color)
        y += lh
    img.save(CAP / name)
    print(f'{name}: {len(wrapped)} líneas')


def git(*args):
    subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True)


# 1. Datos semilla + conteos
shot('01_seed.png', 'python manage.py seed_blog && shell (conteos)',
     run(['seed_blog']) + '\n' + run(['shell', '-c',
         'from blog.models import Author, Post, Comment; '
         'print(f"autores={Author.objects.count()} articulos={Post.objects.count()} comentarios={Comment.objects.count()}")'],
         tail=3))

# 2. Duelo equipo 8/8
shot('02_duelo_team.png', 'python manage.py duel', raw(['duel']).split('Destroying')[0].strip())

# 3. Duelo IA 3/8
out_ai = raw(['duel', '--source', 'ai'])
shot('03_duelo_ai.png', 'python manage.py duel --source ai', out_ai.split('Destroying')[0].strip())

# 4. SQL evidencia
shot('04_sql.png', 'shell: print(ai_answers.q3().query / q5().query)',
     run(['shell', '-c', 'from blog.duel import ai_answers; '
          'print("AI-Q3:"); print(ai_answers.q3().query); print(); print("AI-Q5:"); print(ai_answers.q5().query)'],
         tail=8))

# 5. Test en ROJO (queries.py original del profesor, temporalmente)
fixed = (ROOT / 'blog' / 'queries.py').read_text(encoding='utf-8')
orig = subprocess.run(['git', 'show', '8e7b744:blog/queries.py'], capture_output=True,
                      text=True, cwd=ROOT, timeout=60).stdout.replace('\n', '\n')
(ROOT / 'blog' / 'queries.py').write_text(orig, encoding='utf-8')
try:
    red = run(['test', 'blog.tests.test_front_page'], tail=14)
finally:
    (ROOT / 'blog' / 'queries.py').write_text(fixed, encoding='utf-8')
shot('05_test_rojo.png', 'python manage.py test blog.tests.test_front_page  (ANTES del fix)', red)

# 6. Test en VERDE + suite
shot('06_test_verde.png',
     'python manage.py test blog.tests.test_front_page  (DESPUÉS) && python manage.py test',
     run(['test', 'blog.tests.test_front_page'], tail=5) + '\n\n' + run(['test'], tail=4))

# 7. Agent: 4 intenciones
a1 = run(['agent', '--intent', '{"action": "posts_per_author", "args": {}}'], tail=14)
a2 = run(['agent', '--intent', '{"action": "run_sql", "args": {}}'], tail=4)
shot('07_agent_lecturas.png', 'agent posts_per_author / run_sql', a1 + '\n\n' + a2)

# 8. Comentario hostil + plan sin aprobar
a3 = run(['agent', '--intent', '{"action": "comments_of_post", "args": {"post_id": 1}}'], tail=12)
a4 = run(['agent', '--intent', '{"action": "delete_comments_of_post", "args": {"post_id": 1}}'], tail=12)
shot('08_agent_hostil.png', 'agent comments_of_post(1) / delete_comments_of_post(1)', a3 + '\n\n' + a4)

# 9. Plan aprobado + carrera + restauración
p1 = run(['agent', '--intent', '{"action": "delete_comments_of_post", "args": {"post_id": 5}}'], tail=16)
import re
h = re.search(r'"plan_hash": "([0-9a-f]+)"', p1).group(1)
p2 = run(['agent', '--intent', '{"action": "delete_comments_of_post", "args": {"post_id": 5}}',
          '--approve', h], tail=6)
run(['shell', '-c', 'from blog.models import Post, Comment; p=Post.objects.get(pk=5); '
     'Comment.objects.create(post=p, author_name="Lector X", text="race")'])
p3 = run(['agent', '--intent', '{"action": "delete_comments_of_post", "args": {"post_id": 5}}'], tail=16)
h2 = re.search(r'"plan_hash": "([0-9a-f]+)"', p3).group(1)
p4 = run(['agent', '--intent', '{"action": "delete_comments_of_post", "args": {"post_id": 5}}',
          '--approve', h], tail=4)  # hash VIEJO
rest = run(['seed_blog'], tail=1)
shot('09_agent_race.png', 'plan post5 -> approve -> race con hash viejo -> seed_blog',
     f'[plan1 hash={h}]\n' + p2 + f'\n[plan2 hash={h2}, apruebo con el VIEJO {h}]\n' + p4 + '\n' + rest)

print('Listo:', sorted(p.name for p in CAP.glob('*.png')))
