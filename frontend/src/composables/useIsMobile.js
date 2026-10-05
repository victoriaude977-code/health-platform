// Reactive mobile-width check shared by views that switch layouts on phones.
import { onBeforeUnmount, ref } from 'vue'

export function useIsMobile(breakpoint = 768) {
  const isMobile = ref(window.innerWidth < breakpoint)
  const onResize = () => {
    isMobile.value = window.innerWidth < breakpoint
  }
  window.addEventListener('resize', onResize)
  onBeforeUnmount(() => window.removeEventListener('resize', onResize))
  return isMobile
}
