<template>
  <aside :class="`flex-shrink-0 w-80 bg-neutral-800 border-l border-neutral-700 overflow-hidden transition-all duration-300 ${isCollapsed ? 'translate-x-full' : ''}`">
    <div class="flex items-center justify-between px-4 py-3 border-b border-neutral-700">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 bg-neutral-600 rounded flex items-center justify-center">
          <span class="text-xs font-medium">I</span>
        </div>
        <span class="font-medium text-left">Inspector</span>
      </div>
      <button @toggle-collapse aria-label="Toggle inspector" class="p-2 rounded hover:bg-neutral-700">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </div>
    
    <!-- Inspector content will vary based on selected item -->
    <inspector-content 
      v-if="!isCollapsed"
      :selected-item="selectedItem"
    />
    
    <!-- Collapsed state shows only icons -->
    <div v-else class="flex flex-col items-center pt-4">
      <inspector-icon 
        v-for="item in inspectorItems" 
        :key="item.name"
        :name="item.name"
        :icon="item.icon"
        :active="item.active"
        @click="selectItem(item.name)"
      />
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import InspectorContent from '../ui/InspectorContent.vue'
import InspectorIcon from '../ui/InspectorIcon.vue'

const props = defineProps({
  isCollapsed: Boolean
})

const emit = defineEmits(['toggle-collapse'])

// State for selected item in inspector
const selectedItem = ref(null)

// Inspector items when collapsed (icon-only view)
const inspectorItems = ref([
  { name: 'metadata', icon: 'list-details', active: false },
  { name: 'references', icon: 'link', active: false },
  { name: 'ai-recommendations', icon: 'sparkles', active: false },
  { name: 'decision-receipts', icon: 'receipt', active: false },
  { name: 'continuity-notes', icon: 'clock', active: false },
  { name: 'open-questions', icon: 'help-circle', active: false }
])

// Handle item selection
const selectItem = (name) => {
  selectedItem.value = { name }
}

// Emit event when collapse button is clicked
const handleToggleCollapse = () => {
  emit('toggle-collapse')
}
</script>

<style scoped>
/* Right Rail Styles */
</style>