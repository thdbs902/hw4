// Swatch colours for the colour names used in the catalogue.
const SWATCHES: Record<string, string> = {
  black: '#111111',
  blue: '#1f5fbf',
  'charcoal gray': '#3d4248',
  cream: '#f4ecd8',
  'dark heather charcoal': '#3a3d42',
  'dark heather gray': '#5c6168',
  'dusty coral': '#d98b78',
  gold: '#d4af37',
  gray: '#9a9ea5',
  green: '#2f7d4a',
  'heather charcoal gray': '#4a4e55',
  'heather gray': '#b5b8bd',
  ivory: '#fbf6e9',
  'light blue': '#a9cbea',
  'light gray': '#d6d8db',
  multicolor: 'conic-gradient(#c8102e, #d4af37, #2f7d4a, #1f5fbf, #c8102e)',
  navy: '#0f2a52',
  'navy blue': '#0f2a52',
  red: '#c8102e',
  'royal blue': '#2251b5',
  white: '#ffffff',
  yellow: '#f2c94c',
}

export const swatchFor = (name: string) => SWATCHES[name.toLowerCase()] ?? '#c9c9c9'
