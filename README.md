# code-rain

Un mod pour Claude Code : une **pluie de code coloré façon IDE** (Java, HTML, PHP,
SQL, JS, Scala, C, Bash) avec la coloration d'un thème sombre classique.

| Où | Ce que fait le mod |
| --- | --- |
| **App desktop / mobile** | Thème très sombre + fond de pluie de code sur les côtés de la fenêtre, le centre reste dégagé pour la lecture. Le SVG est animé en CSS, mais l'app desktop actuelle fige les fonds : la pluie y apparaît donc immobile (chaque bloc a une position de départ répartie). |
| **Terminal (CLI)** | Le terminal ne dessine ni thème ni fond : tapez `/code-rain` pour afficher (ou masquer) la pluie dans un panneau animé. |

Chacun prend ce qu'il veut : rien ne s'affiche dans le terminal tant que vous ne
lancez pas `/code-rain`.

## Installation

Dans une session Claude Code en terminal :

```
/plugin install code-rain --marketplace Paul-Tardieu/claude-code-rain
```

Répondez `y` pour ajouter le marketplace, puis choisissez la portée (utilisateur par
défaut). Le mod est actif tout de suite.

Depuis un shell :

```bash
claude plugin install code-rain --marketplace Paul-Tardieu/claude-code-rain
```

Dans l'app desktop (où `/plugin` ne fonctionne pas) : cliquez sur **+** à côté de la
zone de saisie, puis **Plugins**, **Add marketplace** avec
`Paul-Tardieu/claude-code-rain`, puis **Add plugin**.

## Personnaliser

La scène SVG et les extraits de code sont générés par `gen_scene.py` :

```bash
python3 gen_scene.py > hooks/scene.js
```

Modifiez `SNIPPETS` (le code qui tombe), `lanes` (position, taille, opacité des
colonnes) ou le dégradé `fade` (largeur de la zone dégagée au centre). La vitesse de
la pluie du terminal se règle dans `hooks/rain.ts` (`speed`) et `hooks/register.tsx`
(`FRAME_MS`).

## Fichiers

- `hooks/register.tsx` : le mod (thème, fond, commande `/code-rain`, panneau terminal)
- `hooks/rain.ts` : l'animation du terminal (cellules d'un `Raster`)
- `hooks/scene.js` : scène SVG + flux de caractères, générés
- `hooks/make-colors.js` : générateur de palette fourni par Claude Code
