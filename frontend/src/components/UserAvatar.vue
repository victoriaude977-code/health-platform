<template>
  <!-- Preset emoji icon -->
  <div v-if="meta.type === 'preset'" class="preset-avatar" :style="style">
    {{ meta.emoji }}
  </div>
  <!-- Uploaded picture -->
  <el-avatar v-else-if="meta.type === 'image'" :size="size" :src="meta.src" class="avatar-img" />
  <!-- Fallback: initial letter -->
  <el-avatar v-else :size="size" class="avatar-initial">{{ initial }}</el-avatar>
</template>

<script>
import { computed } from 'vue'
import { describeAvatar } from '@/constants/avatars'

export default {
  name: 'UserAvatar',
  props: {
    avatar: { type: String, default: null },
    username: { type: String, default: '' },
    size: { type: Number, default: 36 },
  },
  setup(props) {
    const meta = computed(() => describeAvatar(props.avatar))
    const initial = computed(() =>
      props.username ? props.username[0].toUpperCase() : '?')
    const style = computed(() => ({
      width: `${props.size}px`,
      height: `${props.size}px`,
      fontSize: `${Math.round(props.size * 0.52)}px`,
      background: meta.value.bg,
    }))
    return { meta, initial, style }
  },
}
</script>

<style scoped>
.preset-avatar {
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  line-height: 1;
  user-select: none;
}

.avatar-initial {
  background: var(--brand);
  color: #fff;
  font-weight: 600;
  flex-shrink: 0;
}

.avatar-img {
  flex-shrink: 0;
  background: var(--surface-soft);
}
</style>
