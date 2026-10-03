// Yale residential colleges and professional schools CC sells (crest ids match
// data/brand/crests/<id>.png from backend/crop_crests.py).
export interface Crest {
  id: string
  name: string
  query: string
  mono: string
}

export const COLLEGES: Crest[] = [
  { id: 'benjamin-franklin', name: 'Benjamin Franklin', query: 'Benjamin Franklin', mono: 'BF' },
  { id: 'berkeley', name: 'Berkeley', query: 'Berkeley', mono: 'BK' },
  { id: 'branford', name: 'Branford', query: 'Branford', mono: 'BR' },
  { id: 'davenport', name: 'Davenport', query: 'Davenport', mono: 'DC' },
  { id: 'grace-hopper', name: 'Grace Hopper', query: 'Grace Hopper', mono: 'GH' },
  { id: 'jonathan-edwards', name: 'Jonathan Edwards', query: 'Jonathan Edwards', mono: 'JE' },
  { id: 'morse', name: 'Morse', query: 'Morse', mono: 'MC' },
  { id: 'pierson', name: 'Pierson', query: 'Pierson', mono: 'PC' },
  { id: 'saybrook', name: 'Saybrook', query: 'Saybrook', mono: 'SY' },
  { id: 'timothy-dwight', name: 'Timothy Dwight', query: 'Timothy Dwight', mono: 'TD' },
  { id: 'trumbull', name: 'Trumbull', query: 'Trumbull', mono: 'TC' },
]

export const SCHOOLS: Crest[] = [
  { id: 'law', name: 'Law', query: 'Law School', mono: 'LAW' },
  { id: 'management', name: 'Management', query: 'School Of Management', mono: 'SOM' },
  { id: 'medicine', name: 'Medicine', query: 'Medicine', mono: 'MED' },
  { id: 'nursing', name: 'Nursing', query: 'Nursing', mono: 'YSN' },
  { id: 'public-health', name: 'Public Health', query: 'Public Health', mono: 'YSPH' },
  { id: 'divinity', name: 'Divinity', query: 'Divinity', mono: 'YDS' },
  { id: 'art', name: 'Art', query: 'School Of Art', mono: 'ART' },
  { id: 'music', name: 'Music', query: 'School Of Music', mono: 'YSM' },
  { id: 'architecture', name: 'Architecture', query: 'Architecture', mono: 'ARCH' },
  { id: 'engineering', name: 'Engineering', query: 'Engineering', mono: 'SEAS' },
]
