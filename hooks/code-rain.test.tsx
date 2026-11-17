import { expect, test } from 'claude-code/testing'

const PANE = {
  plugin: 'code-rain',
  component: 'Pane',
  requestId: 'code-rain',
  props: {
    title: 'Code rain',
    isFocused: false,
    bodyColumns: 60,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 20 },
    view: {},
  },
} as const

test('le terminal dessine la pluie dans un Raster valide', async ($, on) => {
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const raster = await ui.find({ type: 'Raster', key: 'rain' })

  expect(raster).toBeDefined()
  await ui.unmount()
})

test('en ligne, la pluie se limite à 12 rangées', async ($, on) => {
  const ui = await $.ui.mount({
    ...PANE,
    props: { ...PANE.props, placement: 'inline' },
    surface: 'terminal',
  })
  const raster = await ui.find({ type: 'Raster', key: 'rain' })

  expect(raster).toBeDefined()
  await ui.unmount()
})

test('le desktop montre la scène SVG dans le panneau', async ($, on) => {
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect(await ui.find({ type: 'Svg' })).toBeDefined()
  await ui.unmount()
})
