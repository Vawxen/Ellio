<template>
  <div 
    class="bg-neutral-800 border border-neutral-700 rounded-lg shadow-lg p-4 flex items-start space-x-3"
    :class="`border-${getBorderColor(type)}`"
  >
    <div class="flex-shrink-0">
      <svg 
        class="w-5 h-5" 
        :class="`text-${getTextColor(type)}`"
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <!-- Icon based on type -->
        <circle cx="12" cy="12" r="10" stroke-width="2" v-if="type === 'info'"></circle>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" v-if="type === 'success'"></path>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.13 0 2.136-.5 2.757-1.224l.225-.26A5.001 5.001 0 0021.75 12c0-2.761-1.51-5.098-3.698-6.064L15.75 3.25a2.625 2.625 0 00-2.378-.49A2.621 2.621 0 009.375 6.75a2.625 2.625 0 00-2.378.49l-.798 1.34A5.001 5.001 0 003.85 17.65c-.621.724-.09 1.56.642 1.886l.225.26A5.006 5.006 0 006 21a8.996 8.996 0 006.282-4.249z" v-if="type === 'error'"></path>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6-2a9 9 0 10-18 0v.01" v-if="type === 'warning'"></path>
      </svg>
    </div>
    
    <div class="flex-1">
      <div class="flex justify-between items-start mb-1">
        <h3 class="font-medium text-neutral-100">{{ title }}</h3>
        <button 
          @click="close"
          class="p-1 rounded hover:bg-neutral-700 text-neutral-400"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>
      <p class="text-neutral-300">{{ message }}</p>
      
      <!-- Progress bar for loading notifications -->
      <div v-if="progress !== null" class="mt-2 h-1.5 bg-neutral-700 rounded">
        <div 
          class="bg-blue-500 h-1.5 rounded" 
          :style="`width: ${progress}%`"
        ></div>
      </div>
      
      <!-- Action buttons -->
      <div v-if="actions && actions.length > 0" class="mt-3 flex space-x-2">
        <button 
          v-for="action in actions" 
          :key="action.label"
          @click="action.handler"
          class="px-3 py-1.5 text-sm rounded transition-colors duration-200"
          :class="`${action.variant === 'primary' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-neutral-700 hover:bg-neutral-600'}` text-white"
        >
          {{ action.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  notification: Object
})

const emit = defineEmits(['close'])

const { id, type = 'info', title = '', message = '', progress = null, actions = [] } = props.notification

const getBorderColor = (type) => {
  const colors = {
    info: 'blue-500',
    success: 'green-500',
    error: 'red-500',
    warning: 'yellow-500'
  }
  return colors[type] || 'neutral-500'
}

const getTextColor = (type) => {
  const colors = {
    info: 'blue-400',
    success: 'green-400',
    error: 'red-400',
    warning: 'yellow-400'
  }
  return colors[type] || 'neutral-400'
}

const close = () => {
  emit('close')
}
</script>

<style scoped>
/* NotificationCard Styles */
</style>