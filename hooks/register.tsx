import type { Register, ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'
import { createRain, step, type Rain } from './rain.ts'
import { SCENE } from './scene.js'

// ─── Desktop / mobile : thème très sombre + fond animé ───────────────────────

// Rôles proches d'un IDE sombre classique (VS Code Dark+).
const { theme, problems } = makeColors({
  label: 'Code rain',
  only: 'dark',
  roles: { accent: '#569cd6', danger: '#f14c4c', success: '#6a9955', warning: '#ce9178', pro: '#c586c0' },
  dark: {
    gray: {
      anchors: {
        'surface-0': '#07080b',
        'surface-1': '#0d0f13',
        'surface-2': '#121419',
        'surface-3': '#171a20',
        'text-primary': '#e6e6e6',
        'text-secondary': '#c2c2c2',
        'text-muted': '#9a9a9a',
      },
    },
  },
})

const LOOK: ThemeSetArgs = {
  colors: theme,
  backdrop: { scene: 'code-rain', glass: { blur: 6, tint: '#07080b', opacity: 0.55 } },
}

// ─── Terminal : la pluie dans un panneau, ouvert par /code-rain ──────────────

const PANE = 'code-rain'
const FRAME_MS = 80
const INLINE_ROWS = 12

// État d'animation local au module (perdu à un rechargement : il se recrée).
let rain: Rain | undefined
let isMounted = false

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const unpainted = problems.find(line => line.startsWith("Desktop won't paint"))

    if (unpainted !== undefined) {
      $.ui.toast(unpainted)
    }
    // Le terminal ne dessine pas de thème : isDrawn y vaut false, sans conséquence.
    await $.theme.set(LOOK)

    await $.command.register({
      name: 'code-rain',
      description: 'Affiche ou masque la pluie de code dans un panneau',
    })

    // Une image toutes les FRAME_MS, seulement quand la pluie est affichée.
    $.clock.every(FRAME_MS, () => {
      if (!isMounted || rain === undefined) {
        return
      }
      void $.ui.blit({ requestId: PANE, key: 'rain', cells: step(rain) }).then(result => {
        // Refusé = panneau fermé (ou redimensionné) : on attend le prochain rendu.
        if ('deny' in result) {
          isMounted = false
        }
      })
    })

    return next(e)
  })

  on('command.run', { command: 'code-rain' }, async $ => {
    const isOpen = (await $.ui.panes()).some(pane => pane.id === PANE)

    if (isOpen) {
      await $.ui.close({ id: PANE })
      return { text: 'Pluie de code masquée.' }
    }
    await $.ui.open({ id: PANE, title: 'Code rain' })
    return { text: 'Pluie de code affichée (/code-rain pour la masquer).' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, ($, e) => {
    if (e.surface === 'terminal') {
      const { Raster } = $.ui.resolve(e)
      const columns = Math.max(1, Math.min(512, e.props.bodyColumns))
      const room = e.props.scroll.bodyRows
      const rows = Math.max(1, Math.min(256, e.props.placement === 'inline' ? Math.min(INLINE_ROWS, room) : room))

      if (rain === undefined || rain.columns !== columns || rain.rows !== rows) {
        rain = createRain(columns, rows)
      }
      isMounted = true

      return <Raster key="rain" columns={columns} rows={rows} cells={step(rain)} />
    }

    // Desktop / mobile : le panneau montre la même scène que le fond.
    const { Svg } = $.ui.resolve(e)
    return <Svg source={SCENE} alt="Pluie de code coloré" isInteractive />
  })

  on('ui.render', { component: 'Backdrop' }, ($, e, next) => {
    if (e.surface !== 'desktop' && e.surface !== 'mobile') {
      return next(e)
    }
    const { Svg } = $.ui.resolve(e)

    // isInteractive : dessiné dans un cadre (sans script) au lieu d'une image fixe,
    // ce qui laisse tourner l'animation.
    return <Svg source={SCENE} alt="Pluie de code coloré sur les côtés de la fenêtre" isInteractive />
  })
}
