<template>
  <aside :class="`flex-shrink-0 w-64 bg-neutral-800 border-r border-neutral-700 overflow-hidden transition-all duration-300 ${isCollapsed ? '-translate-x-full' : ''}`">
    <div class="flex items-center justify-between px-4 py-3 border-b border-neutral-700">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 bg-neutral-600 rounded flex items-center justify-center">
          <span class="text-xs font-medium">E</span>
        </div>
        <span class="font-medium text-left">Ellio</span>
      </div>
      <button @toggle-collapse aria-label="Toggle navigation" class="p-2 rounded hover:bg-neutral-700">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
      </button>
    </div>
    
    <nav class="mt-4 space-y-1">
      <nav-link 
        href="#/brief" 
        label="Brief" 
        icon="document-text"
        :active="currentRoute === 'brief'"
      />
      <nav-link 
        href="#/library" 
        label="Library" 
        icon="folder"
        :active="currentRoute === 'library'"
      />
      <nav-link 
        href="#/search" 
        label="Search" 
        icon="search"
        :active="currentRoute === 'search'"
      />
      <nav-link 
        href="#/selects" 
        label="Selects" 
        icon="square-rounded"
        :active="currentRoute === 'selects'"
      />
      <nav-link 
        href="#/assembly" 
        label="Assembly" 
        icon="layers"
        :active="currentRoute === 'assembly'"
      />
      <nav-link 
        href="#/review" 
        label="Review" 
        icon="eye"
        :active="currentRoute === 'review'"
      />
    </nav>
    
    <!-- Bottom section for decisions and other items -->
    <div class="mt-auto border-t border-neutral-700 pt-4">
      <nav-link 
        href="#/decisions" 
        label="Decisions" 
        icon="list-checks"
        :active="currentRoute === 'decisions'"
      />
      <nav-link 
        href="#/deliverables" 
        label="Deliverables" 
        icon="download"
        :active="currentRoute === 'deliverables'"
      />
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import NavLink from '../ui/NavLink.vue'

const props = defineProps({
  isCollapsed: Boolean
})

const emit = defineEmits(['toggle-collapse'])

const currentRoute = ref('brief') // This would come from router in real implementation

// Emit event when collapse button is clicked
const handleToggleCollapse = () => {
  emit('toggle-collapse')
}
</script>

<style scoped>
/* Left Rail Styles */
</style>