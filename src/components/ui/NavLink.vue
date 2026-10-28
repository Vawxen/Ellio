<template>
  <router-link 
    :to="to" 
    class="flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
    :class="`${active ? 'bg-neutral-700' : 'hover:bg-neutral-700'}`"
  >
    <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <!-- This would be replaced with actual icon based on icon prop -->
      <circle cx="12" cy="12" r="10" stroke-width="2"></circle>
    </svg>
    <span class="ml-3">{{ label }}</span>
  </router-link>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  label: String,
  icon: String,
  active: Boolean,
  to: String
})
</script>

<style scoped>
/* NavLink Styles */
</style>