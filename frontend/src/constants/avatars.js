// Preset avatar icons offered in the Profile picker. The backend stores the
// choice as "preset:<key>"; uploaded pictures are stored as "/uploads/...".
export const PRESET_AVATARS = [
  { key: 'fox', emoji: '🦊', bg: '#ffe4d6' },
  { key: 'panda', emoji: '🐼', bg: '#e8eef7' },
  { key: 'cat', emoji: '🐱', bg: '#fde9f1' },
  { key: 'frog', emoji: '🐸', bg: '#e2f7e4' },
  { key: 'tiger', emoji: '🐯', bg: '#fff0d9' },
  { key: 'rabbit', emoji: '🐰', bg: '#fdf0fa' },
  { key: 'koala', emoji: '🐨', bg: '#e9eef4' },
  { key: 'unicorn', emoji: '🦄', bg: '#efe6fd' },
  { key: 'dog', emoji: '🐶', bg: '#fdf1e1' },
  { key: 'monkey', emoji: '🐵', bg: '#fdf3dc' },
  { key: 'bear', emoji: '🐻', bg: '#f6e8dd' },
  { key: 'penguin', emoji: '🐧', bg: '#e3eefb' },
  { key: 'owl', emoji: '🦉', bg: '#f0ecdf' },
  { key: 'lion', emoji: '🦁', bg: '#fff3d6' },
  { key: 'star', emoji: '⭐', bg: '#fdf8dc' },
  { key: 'leaf', emoji: '🍀', bg: '#e4f7e9' },
]

const PRESET_MAP = Object.fromEntries(PRESET_AVATARS.map((p) => [p.key, p]))

// Describe any stored avatar value for rendering.
//   "preset:fox"            -> { type: 'preset', emoji, bg }
//   "/uploads/avatars/x.png" -> { type: 'image', src }
//   null / ""               -> { type: 'none' }
export function describeAvatar(avatar) {
  if (!avatar) return { type: 'none' }
  if (avatar.startsWith('preset:')) {
    const p = PRESET_MAP[avatar.slice(7)]
    return { type: 'preset', emoji: (p && p.emoji) || '🙂', bg: (p && p.bg) || '#e2f7e4' }
  }
  if (avatar.startsWith('/')) return { type: 'image', src: avatar }
  return { type: 'none' }
}
