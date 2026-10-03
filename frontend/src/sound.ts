// Halftime "click" sound for buttons, links and cards, synthesised with the Web Audio API
// (no audio files). Shoppers can mute it from the nav; the choice is saved in localStorage.
const KEY = 'cc-sound'
let ctx: AudioContext | null = null

export const soundOn = () => localStorage.getItem(KEY) !== 'off'
export const setSoundOn = (on: boolean) => localStorage.setItem(KEY, on ? 'on' : 'off')

export function playClick() {
  if (!soundOn()) return
  ctx ??= new AudioContext()
  const t = ctx.currentTime
  // Short tick (filtered noise) + a soft high "pop", like a stadium clicker.
  const osc = ctx.createOscillator()
  const gain = ctx.createGain()
  osc.type = 'triangle'
  osc.frequency.setValueAtTime(1800, t)
  osc.frequency.exponentialRampToValueAtTime(600, t + 0.05)
  gain.gain.setValueAtTime(0.12, t)
  gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.07)
  osc.connect(gain).connect(ctx.destination)
  osc.start(t)
  osc.stop(t + 0.08)
}

export function installClickSound() {
  const handler = (e: Event) => {
    const el = (e.target as Element | null)?.closest('a, button, [role="radio"]')
    if (el && !(el as HTMLButtonElement).disabled) playClick()
    startCrowd() // first interaction unlocks audio; no-op if muted or already playing
  }
  document.addEventListener('pointerdown', handler)
  return () => document.removeEventListener('pointerdown', handler)
}

// ---------- Stadium crowd ambience (background), synthesised: no audio files ----------
// Layers, like a real stadium: a ROARING crowd (noise shaped by vowel formants, so it sounds
// like thousands of voices), APPLAUSE (thousands of tiny hand-clap grains), a "LET'S GO YA-LE!"
// CHANT (4 shouted vowel syllables + stomps), and CHEERS ("woo!" whistles + big swells).
// Starts on the shopper's first click (browsers block autoplay); follows the 🔊 toggle.
let crowd: { stop: () => void } | null = null

function noiseBuffer(ac: AudioContext, seconds: number, brown = true) {
  const buf = ac.createBuffer(2, Math.floor(ac.sampleRate * seconds), ac.sampleRate)
  for (let ch = 0; ch < 2; ch++) {
    const data = buf.getChannelData(ch)
    let last = 0
    for (let i = 0; i < data.length; i++) {
      const white = Math.random() * 2 - 1
      last = brown ? 0.985 * last + 0.15 * white : white
      data[i] = brown ? last * 2.2 : white
    }
  }
  return buf
}

// Applause: many short, randomly timed, high-passed clap grains (stereo spread).
function applauseBuffer(ac: AudioContext, seconds: number, clapsPerSecond: number) {
  const len = Math.floor(ac.sampleRate * seconds)
  const buf = ac.createBuffer(2, len, ac.sampleRate)
  const grain = Math.floor(ac.sampleRate * 0.012)
  for (let ch = 0; ch < 2; ch++) {
    const data = buf.getChannelData(ch)
    for (let n = 0; n < clapsPerSecond * seconds; n++) {
      const start = Math.floor(Math.random() * (len - grain))
      const amp = 0.2 + Math.random() * 0.5
      for (let i = 0; i < grain; i++) data[start + i] += (Math.random() * 2 - 1) * amp * Math.exp(-i / (grain / 5))
    }
  }
  return buf
}

export function startCrowd() {
  if (crowd || !soundOn()) return
  ctx ??= new AudioContext()
  const ac = ctx
  const master = ac.createGain()
  master.gain.value = 0.0001
  master.gain.exponentialRampToValueAtTime(0.32, ac.currentTime + 2.5)
  const comp = ac.createDynamicsCompressor()
  master.connect(comp).connect(ac.destination)
  const sources: AudioScheduledSourceNode[] = []
  const timers: number[] = []

  // 1) ROAR: brown noise through vowel formants ("aaah" ~ 700/1200/2600 Hz) with slow drift.
  const roarSrc = ac.createBufferSource()
  roarSrc.buffer = noiseBuffer(ac, 6)
  roarSrc.loop = true
  const roarGain = ac.createGain()
  roarGain.gain.value = 0.55
  const formants = [700, 1200, 2600].map((f, i) => {
    const bp = ac.createBiquadFilter()
    bp.type = 'bandpass'
    bp.frequency.value = f
    bp.Q.value = 2.2
    const g = ac.createGain()
    g.gain.value = [1, 0.7, 0.35][i]
    roarSrc.connect(bp).connect(g).connect(roarGain)
    return bp
  })
  roarGain.connect(master)
  roarSrc.start()
  sources.push(roarSrc)

  // 2) APPLAUSE: looping clap texture that rises with every cheer.
  const clapSrc = ac.createBufferSource()
  clapSrc.buffer = applauseBuffer(ac, 4, 900)
  clapSrc.loop = true
  const clapHp = ac.createBiquadFilter()
  clapHp.type = 'highpass'
  clapHp.frequency.value = 900
  const clapGain = ac.createGain()
  clapGain.gain.value = 0.25
  clapSrc.connect(clapHp).connect(clapGain).connect(master)
  clapSrc.start()
  sources.push(clapSrc)

  // 3) CHEER: crowd swell + applause burst + "woo!" whistles.
  const woo = (when: number) => {
    const o = ac.createOscillator()
    const g = ac.createGain()
    o.type = 'sine'
    const f = 900 + Math.random() * 700
    o.frequency.setValueAtTime(f, when)
    o.frequency.exponentialRampToValueAtTime(f * 1.6, when + 0.25)
    o.frequency.exponentialRampToValueAtTime(f * 1.1, when + 0.6)
    g.gain.setValueAtTime(0.0001, when)
    g.gain.exponentialRampToValueAtTime(0.06, when + 0.08)
    g.gain.exponentialRampToValueAtTime(0.0001, when + 0.65)
    o.connect(g).connect(master)
    o.start(when)
    o.stop(when + 0.7)
  }
  const cheer = () => {
    const t = ac.currentTime
    roarGain.gain.cancelScheduledValues(t)
    roarGain.gain.setTargetAtTime(1.5, t, 0.3)
    roarGain.gain.setTargetAtTime(0.55, t + 2.2, 1)
    clapGain.gain.cancelScheduledValues(t)
    clapGain.gain.setTargetAtTime(0.9, t + 0.2, 0.3)
    clapGain.gain.setTargetAtTime(0.25, t + 2.8, 1.2)
    formants[0].frequency.setTargetAtTime(850, t, 0.4) // "aaah" opens up when they roar
    formants[0].frequency.setTargetAtTime(700, t + 2.2, 1)
    for (let i = 0; i < 4; i++) woo(t + 0.2 + Math.random() * 1.6)
    timers.push(window.setTimeout(cheer, 7000 + Math.random() * 6000))
  }
  timers.push(window.setTimeout(cheer, 1500))

  // 4) CHANT: "LET'S - GO - YA - LE!" shouted by thousands (formant-shaped vowel bursts) + stomps.
  const syllable = (when: number, vowel: [number, number], dur: number, loud: number) => {
    const src = ac.createBufferSource()
    src.buffer = noiseBuffer(ac, dur + 0.1, false)
    const out = ac.createGain()
    out.gain.setValueAtTime(0.0001, when)
    out.gain.exponentialRampToValueAtTime(loud, when + 0.03)
    out.gain.exponentialRampToValueAtTime(0.0001, when + dur)
    vowel.forEach((f, i) => {
      const bp = ac.createBiquadFilter()
      bp.type = 'bandpass'
      bp.frequency.value = f
      bp.Q.value = 5
      const g = ac.createGain()
      g.gain.value = i ? 0.6 : 1
      src.connect(bp).connect(g).connect(out)
    })
    out.connect(master)
    src.start(when)
  }
  const stomp = (when: number) => {
    const o = ac.createOscillator()
    const g = ac.createGain()
    o.frequency.setValueAtTime(120, when)
    o.frequency.exponentialRampToValueAtTime(45, when + 0.15)
    g.gain.setValueAtTime(0.5, when)
    g.gain.exponentialRampToValueAtTime(0.0001, when + 0.2)
    o.connect(g).connect(master)
    o.start(when)
    o.stop(when + 0.25)
  }
  const chant = () => {
    const t = ac.currentTime + 0.1
    // let's(e) go(o) ya(a) le(i), repeated 3 times, then a cheer
    const words: [[number, number], number][] = [
      [[530, 1840], 0.22],
      [[500, 900], 0.28],
      [[750, 1250], 0.26],
      [[300, 2300], 0.4],
    ]
    for (let rep = 0; rep < 3; rep++) {
      const base = t + rep * 2
      words.forEach(([vowel, dur], i) => syllable(base + i * 0.36, vowel, dur, 1.8))
      stomp(base)
      stomp(base + 0.72)
    }
    timers.push(window.setTimeout(cheer, 6200))
    timers.push(window.setTimeout(chant, 20000 + Math.random() * 10000))
  }
  timers.push(window.setTimeout(chant, 5000))

  crowd = {
    stop: () => {
      timers.forEach((id) => clearTimeout(id))
      master.gain.setTargetAtTime(0.0001, ac.currentTime, 0.3)
      setTimeout(() => sources.forEach((s) => s.stop()), 1500)
      crowd = null
    },
  }
}

export function stopCrowd() {
  crowd?.stop()
}
