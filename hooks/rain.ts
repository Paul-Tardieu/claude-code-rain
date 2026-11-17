// Pluie de code pour le terminal : calcule les cellules d'un `Raster`
// (caractère, couleur du texte, couleur du fond) image par image.
import { STREAMS } from './scene.js'

// Mêmes couleurs que la scène SVG (thème sombre type VS Code Dark+).
const PALETTE: Record<string, number> = {
  k: 0x569cd6, s: 0xce9178, c: 0x6a9955, n: 0xb5cea8, t: 0x4ec9b0,
  f: 0xdcdcaa, v: 0x9cdcfe, g: 0x569cd6, a: 0x9cdcfe, p: 0x808080, d: 0xd4d4d4,
}
const DEFAULT_BG = 0x01000000 // le fond du terminal, quel qu'il soit
const HEAD = 0xffffff

type Drop = {
  y: number // ligne de la tête (peut être négative : pas encore entrée)
  speed: number // lignes par image
  len: number // longueur de la traîne
  stream: number // langage source
  offset: number // position de départ dans le flux
}

export type Rain = { columns: number; rows: number; drops: (Drop | undefined)[] }

const pick = (n: number) => Math.floor(Math.random() * n)

function newDrop(rows: number, isFirst: boolean): Drop {
  const stream = pick(STREAMS.length)
  const length = STREAMS[stream]?.text.length ?? 1
  return {
    y: isFirst ? pick(rows * 2) - rows : -pick(rows),
    speed: 0.25 + Math.random() * 0.6,
    len: 4 + pick(Math.max(4, rows)),
    stream,
    offset: pick(length),
  }
}

/** Une colonne de terminal sur deux porte une goutte : plus lisible. */
export function createRain(columns: number, rows: number): Rain {
  const drops = Array.from({ length: columns }, (_, x) =>
    x % 2 === 0 ? newDrop(rows, true) : undefined,
  )
  return { columns, rows, drops }
}

function scale(rgb: number, k: number): number {
  const r = ((rgb >> 16) & 0xff) * k
  const g = ((rgb >> 8) & 0xff) * k
  const b = (rgb & 0xff) * k
  return (Math.round(r) << 16) | (Math.round(g) << 8) | Math.round(b)
}

/** Avance d'une image et renvoie les cellules encodées pour `Raster`/`$.ui.blit`. */
export function step(rain: Rain): string {
  const { columns, rows, drops } = rain
  const cells = new Uint32Array(columns * rows * 3)
  for (let i = 0; i < columns * rows; i++) {
    cells[i * 3] = 0x20
    cells[i * 3 + 1] = DEFAULT_BG
    cells[i * 3 + 2] = DEFAULT_BG
  }
  for (let x = 0; x < columns; x++) {
    const drop = drops[x]
    if (drop === undefined) continue
    const source = STREAMS[drop.stream]
    if (source === undefined) continue
    const { text, classes } = source
    const head = Math.floor(drop.y)
    for (let d = 0; d < drop.len; d++) {
      const y = head - d
      if (y < 0 || y >= rows) continue
      // Le caractère dépend de la ligne : la colonne « déroule » le code en tombant.
      const at = (drop.offset + y) % text.length
      const ch = text.charCodeAt(at)
      if (ch === 0x20) continue
      const base = PALETTE[classes[at] ?? 'd'] ?? 0xd4d4d4
      const fade = 1 - d / drop.len
      const i = (y * columns + x) * 3
      cells[i] = ch
      cells[i + 1] = d === 0 ? HEAD : scale(base, 0.25 + 0.75 * fade)
    }
    drop.y += drop.speed
    if (head - drop.len >= rows) drops[x] = newDrop(rows, false)
  }
  // toBase64 existe dans l'environnement des mods (ES2025) mais pas encore dans les types TS.
  const bytes = new Uint8Array(cells.buffer) as Uint8Array & { toBase64(): string }
  return bytes.toBase64()
}
