<template>
  <div 
    class="relative group border border-neutral-700 rounded-lg overflow-hidden hover:border-neutral-600 cursor-pointer"
    :class="`${asset.status === 'error' ? 'border-red-500' : asset.status === 'ready' ? 'border-green-500' : ''}`"
    @click="selectAsset(asset)"
  >
    <!-- Status indicator badge -->
    <div class="absolute top-2 left-2 flex items-center space-x-1 text-xs px-2 py-0.5 rounded">
      <div class="w-2 h-2" :class="`bg-${getStatusColor(asset.status)}`"></div>
      <span class="capitalize">{{ asset.status }}</span>
    </div>
    
    <!-- Thumbnail placeholder -->
    <div class="aspect-w-16 aspect-h-9 bg-neutral-800 flex items-center justify-center">
      <img 
        :src="asset.thumbnail" 
        :alt="asset.name" 
        class="w-full h-full object-cover"
      />
      <div v-if="asset.status === 'error'" class="bg-black bg-opacity-50 text-red-300 text-xs px-2 py-1">
        <span class="font-medium">!</span> Error
      </div>
    </div>
    
    <!-- Asset info -->
    <div class="p-3">
      <div class="flex justify-between items-start mb-2">
        <h3 class="font-medium truncate max-w-[150px]">{{ asset.name }}</h3>
        <span class="text-xs text-neutral-500">{{ asset.duration }}</span>
      </div>
      
      <!-- Progress bars for each stage -->
      <div class="space-y-2 text-xs">
        <div class="flex items-center">
          <span class="w-20">Orig:</span>
          <div class="flex-1 bg-neutral-700 rounded h-1.5">
            <div 
              class="bg-blue-500 h-1.5 rounded" 
              :style="`width: ${asset.original.progress}%`"
            ></div>
          </div>
          <span class="w-16 text-right">{{ asset.original.progress }}%</span>
        </div>
        
        <div class="flex items-center">
          <span class="w-20">Proxy:</span>
          <div class="flex-1 bg-neutral-700 rounded h-1.5">
            <div 
              class="bg-purple-500 h-1.5 rounded" 
              :style="`width: ${asset.proxy.progress}%`"
            ></div>
          </div>
          <span class="w-16 text-right">{{ asset.proxy.progress }}%</span>
        </div>
        
        <div class="flex items-center">
          <span class="w-20">Transcript:</span>
          <div class="flex-1 bg-neutral-700 rounded h-1.5">
            <div 
              class="bg-pink-500 h-1.5 rounded" 
              :style="`width: ${asset.transcript.progress}%`"
            ></div>
          </div>
          <span class="w-16 text-right">{{ asset.transcript.progress }}%</span>
        </div>
        
        <div class="flex items-center">
          <span class="w-20">Analysis:</span>
          <div class="flex-1 bg-neutral-700 rounded h-1.5">
            <div 
              class="bg-yellow-500 h-1.5 rounded" 
              :style="`width: ${asset.analysis.progress}%`"
            ></div>
          </div>
          <span class="w-16 text-right">{{ asset.analysis.progress }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  asset: Object
})

const emit = defineEmits(['select'])

const getStatusColor = (status) => {
  const statusColors = {
    ingesting: 'blue-500',
    checksum_verified: 'purple-500',
    transcoding: 'pink-500',
    proxy_ready: 'indigo-500',
    transcript_ready: 'rose-500',
    analysis_ready: 'yellow-500',
    error: 'red-500',
    ready: 'green-500'
  }
  return statusColors[status] || 'gray-500'
}

// Handle asset selection
const handleSelect = () => {
  emit('select', props.asset)
}
</script>

<style scoped>
/* MediaCard Styles */
</style>