# Génère hooks/scene.ts : pluie de code coloré façon IDE sur les côtés de la fenêtre.
# Génère hooks/scene.js : la scène SVG (desktop/mobile) et les flux de caractères
# colorés (terminal). Usage : python3 -I gen_scene.py > hooks/scene.js
import random, re, sys, json, os
random.seed(42)
W, H = 1600, 1000
MAXC = 28  # largeur max d'une ligne (caractères), pour ne pas déborder vers le centre

SNIPPETS = {
"java": """public class Main {
  // point d'entrée
  public static void main(String[] args) {
    List<String> xs = new ArrayList<>();
    for (int i = 0; i < 10; i++) {
      xs.add("item" + i);
    }
    System.out.println(xs);
  }
}""",
"html": """<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="utf-8">
    <title>Accueil</title>
  </head>
  <body>
    <div id="app"></div>
    <a href="/login">Login</a>
  </body>
</html>""",
"php": """<?php
namespace App\\Controller;
// contrôleur Symfony
class FeedController
{
  public function index(): Response
  {
    $posts = $this->repo->findAll();
    return $this->json($posts, 200);
  }
}""",
"sql": """-- top auteurs
SELECT u.login, COUNT(*) AS nb
FROM publication p
JOIN utilisateur u
  ON u.id = p.auteur_id
WHERE p.date > '2026-01-01'
GROUP BY u.login
ORDER BY nb DESC
LIMIT 10;""",
"js": """import { ref } from 'vue'
// compteur réactif
const count = ref(0)
function inc() {
  count.value++
}
const todos = await fetch('/api')
  .then(r => r.json())
export default { count, inc }""",
"scala": """object Main extends App {
  // case class immuable
  case class Point(x: Int, y: Int)
  val pts = List(1, 2, 3)
    .map(i => Point(i, i * 2))
  pts.foreach(println)
  def sum(xs: List[Int]): Int =
    xs.foldLeft(0)(_ + _)
}""",
"c": """#include <stdio.h>
/* somme d'un tableau */
int sum(int *t, int n) {
  int s = 0;
  for (int i = 0; i < n; i++)
    s += t[i];
  return s;
}
int main(void) {
  printf("%d\\n", 42);
  return 0;
}""",
"bash": """#!/usr/bin/env bash
set -euo pipefail
# build et déploiement
for f in src/*.ts; do
  echo "lint $f"
done
npm run build
cp -r dist/ /var/www/html
docker compose up -d""",
}

KW = {
"java": "public class static void new for int return if else private import package extends",
"php": "namespace class public function return new use if else foreach private",
"sql": "SELECT FROM JOIN ON WHERE GROUP BY ORDER DESC LIMIT AS COUNT AND INSERT INTO",
"js": "import from const let function return await export default new if else",
"scala": "object extends case class val def new if else",
"c": "int void return for if else while char",
"bash": "set for in do done echo if then fi",
"html": "",
}
TYPES = {"String","List","ArrayList","Response","Int","App","Point","System"}

def tokenize(lang, line):
    """Renvoie [(classe, texte)] : c=commentaire, s=chaîne, k=mot-clé, n=nombre,
    t=type, f=fonction, v=variable, g=balise, a=attribut, '' = texte normal."""
    kws = set(KW[lang].split())
    out = []
    if lang == "html":
        for m in re.finditer(r'(<!?/?)([\w!]+)|([\w-]+)(?==)|("[^"]*")|(/?>)|([^<>"=]+|=)', line):
            if m.group(2): out += [("p", m.group(1)), ("g", m.group(2))]
            elif m.group(3): out.append(("a", m.group(3)))
            elif m.group(4): out.append(("s", m.group(4)))
            elif m.group(5): out.append(("p", m.group(5)))
            else: out.append(("", m.group(0)))
        return out
    pat = re.compile(r'(//.*|/\*.*\*/|--.*|#(?!include)(?!!).*)|("[^"]*"|\'[^\']*\')|(\$\w+|\$this)|(#include|#!.*)|(\b\d+\b)|([A-Za-z_]\w*)(?=\s*\()|([A-Za-z_]\w*)|(.)')
    for m in pat.finditer(line):
        c, s, v, pre, n, fn, w, o = m.groups()
        if c: out.append(("c", c))
        elif s: out.append(("s", s))
        elif v: out.append(("v", v))
        elif pre: out.append(("k", pre))
        elif n: out.append(("n", n))
        elif fn: out.append(("k" if fn in kws else "f", fn))
        elif w: out.append(("k" if w in kws else "t" if w in TYPES else "", w))
        else: out.append(("", o))
    return out

esc = lambda s: s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace(" ", " ")

def block(lang, size, lh):
    lines = SNIPPETS[lang].split("\n")
    parts = []
    for i, line in enumerate(lines):
        line = line[:MAXC]
        toks = "".join(f'<tspan class="{c}">{esc(t)}</tspan>' if c else esc(t) for c, t in tokenize(lang, line))
        parts.append(f'<text y="{(i+1)*lh}">{toks}</text>')
    return "".join(parts), len(lines) * lh

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">']
# Couleurs façon thème sombre d'IDE (VS Code Dark+)
out.append("""<style>
text{font-family:ui-monospace,'JetBrains Mono','DejaVu Sans Mono',Menlo,Consolas,monospace;fill:#d4d4d4}
.k{fill:#569cd6}.s{fill:#ce9178}.c{fill:#6a9955;font-style:italic}.n{fill:#b5cea8}
.t{fill:#4ec9b0}.f{fill:#dcdcaa}.v{fill:#9cdcfe}.g{fill:#569cd6}.a{fill:#9cdcfe}.p{fill:#808080}
KEYFRAMES
</style>""")
# Masque : visible sur les bords, s'efface vers le centre
out.append("""<defs>
<linearGradient id="fade" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="#fff"/><stop offset=".2" stop-color="#fff" stop-opacity=".85"/>
<stop offset=".31" stop-color="#fff" stop-opacity="0"/><stop offset=".69" stop-color="#fff" stop-opacity="0"/>
<stop offset=".8" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff"/></linearGradient>
<linearGradient id="vfade" x1="0" x2="0" y1="0" y2="1">
<stop offset="0" stop-color="#000" stop-opacity="1"/><stop offset=".12" stop-color="#000" stop-opacity="0"/>
<stop offset=".88" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="1"/></linearGradient>
<mask id="m"><rect width="1600" height="1000" fill="url(#fade)"/></mask>
</defs>""")
out.append(f'<rect width="{W}" height="{H}" fill="#07080b"/>')
out.append('<g mask="url(#m)">')

langs = list(SNIPPETS)
# couloirs (x, taille de police, opacité) : arrière-plan petit et pâle, premier plan plus net
lanes = [
    (24, 11, .22), (250, 11, .22), (1180, 11, .22), (1400, 11, .22),   # fond
    (110, 13, .55), (1290, 13, .55),                                   # premier plan
]
keyframes = {}
rules = []  # une classe par bloc : l'app retire les attributs style="…" du SVG
for x, size, op in lanes:
    lh = int(size * 1.45)
    # Même départ (hauteur du plus grand bloc) pour tous => même vitesse dans le couloir,
    # et décalage régulier => les blocs ne se chevauchent jamais.
    maxh = max(len(t.split("\n")) for t in SNIPPETS.values()) * lh + 30
    travel = H + 20 + maxh
    n = int(travel // maxh)
    dur = random.uniform(30, 46) * (13 / size)
    phase = random.uniform(0, dur)
    # Animation CSS (celle que l'app dessine) : une @keyframes par hauteur de départ.
    name = f"fall{maxh}"
    keyframes[name] = (f"@keyframes {name}{{from{{transform:translateY(-{maxh}px)}}"
                       f"to{{transform:translateY({H + 20}px)}}}}")
    random.shuffle(langs)
    for j in range(n):
        g, h = block(langs[j % len(langs)], size, lh)
        elapsed = (phase + dur * j / n) % dur
        # Position à t=0 en attribut : si l'animation ne tourne pas, la scène reste répartie.
        y0 = -maxh + travel * elapsed / dur
        cls = f"b{len(rules)}"
        rules.append(f".{cls}{{animation:{name} {dur:.1f}s linear -{elapsed:.1f}s infinite}}")
        out.append(
            f'<g transform="translate({x} 0)" opacity="{op}" font-size="{size}">'
            f'<g class="{cls}" transform="translate(0 {y0:.0f})">'
            f'{g}</g></g>')
out.append('</g>')
# assombrit haut et bas (zone titre / zone de saisie)
out.append(f'<rect width="{W}" height="{H}" fill="url(#vfade)" opacity=".6"/>')
out.append('</svg>')
svg = "".join(out).replace("KEYFRAMES", "".join(keyframes.values()) + "".join(rules))
sys.stderr.write(f"{len(svg)} caractères\n")
# Aperçu pour le README (GitHub anime le CSS d'un SVG affiché en <img>) :
# la même scène, avec le nom du mod dans la zone dégagée du centre.
PREVIEW_TITLE = (
    f'<g text-anchor="middle" font-family="ui-monospace,\'JetBrains Mono\',Menlo,Consolas,monospace">'
    f'<text x="{W // 2}" y="{H // 2 - 10}" font-size="64" font-weight="700" style="fill:#e6e6e6">code-rain</text>'
    f'<text x="{W // 2}" y="{H // 2 + 40}" font-size="22" class="p">'
    f'animated dark theme for Claude Code · desktop app &amp; terminal</text></g>')
preview = svg.replace("</svg>", PREVIEW_TITLE + "</svg>")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "preview.svg"), "w") as f:
    f.write(preview + "\n")
# Flux pour le terminal : chaque langage devient une suite de caractères (espaces
# multiples réduits) et, en parallèle, la classe de couleur de chaque caractère.
streams = []
for lang, code in SNIPPETS.items():
    text, cls = [], []
    for line in code.split("\n"):
        for c, t in tokenize(lang, line.strip()):
            for ch in t:
                if ch.isprintable() and ord(ch) < 0x3000:
                    text.append(ch); cls.append(c or "d")
        text.append(" "); cls.append("d")
    streams.append({"text": "".join(text), "classes": "".join(cls)})
print("// Généré par gen_scene.py — ne pas éditer à la main.")
print("export const SCENE = " + json.dumps(svg, ensure_ascii=False))
print("export const STREAMS = " + json.dumps(streams, ensure_ascii=False))
