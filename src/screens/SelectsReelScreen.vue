<template>
  <div class="h-full flex flex-col">
    <!-- Toolbar -->
    <div class="bg-neutral-800 border-b border-neutral-700 px-4 py-3 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <h1 class="text-lg font-semibold">Selects Reel</h1>
        <div class="flex items-center space-x-1 bg-neutral-700 rounded-lg p-1">
          <button 
            @click="zoomOut"
            :disabled="zoomLevel <= 0.25"
            class="btn-tool"
            title="Zoom Out"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12H9m12 0a9 9 0 10-18 0 9 9 0 0018 0z"></path></svg>
          </button>
          <span class="px-2 text-sm font-mono text-neutral-300">{{ Math.round(zoomLevel * 100) }}%</span>
          <button 
            @click="zoomIn"
            :disabled="zoomLevel >= 4"
            class="btn-tool"
            title="Zoom In"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
          </button>
        </div>
      </div>
      
      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-2 bg-neutral-700 rounded-lg px-3 py-1">
          <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0018 0z"></path></svg>
          <span class="text-sm font-mono text-neutral-300">{{ formatTime(playhead) }}</span>
        </div>
        
        <div class="flex items-center space-x-1">
          <button @click="jumpToStart" class="btn-tool" title="Jump to Start">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"></path></svg>
          </button>
          <button @click="stepBack" class="btn-tool" title="Step Back Frame">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 18l-6-6 6-6"></path></svg>
          </button>
          <button 
            @click="togglePlay"
            :class="isPlaying ? 'bg-blue-600 hover:bg-blue-700' : ''"
            class="btn-tool"
            title="Play/Pause"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path v-if="isPlaying" d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
              <path v-else d="M8 5v14l11-7z" />
            </svg>
          </button>
          <button @click="stepForward" class="btn-tool" title="Step Forward Frame">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 6l6 6-6 6"></path></svg>
          </button>
          <button @click="jumpToEnd" class="btn-tool" title="Jump to End">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
          </button>
        </div>
        
        <div class="flex items-center space-x-2 ml-4">
          <label class="flex items-center space-x-2 text-sm">
            <input type="checkbox" class="h-4 w-4 text-blue-600 bg-neutral-700 border-neutral-600 rounded focus:ring-blue-500" v-model="showTranscript" />
            <span>Transcript</span>
          </label>
          <label class="flex items-center space-x-2 text-sm">
            <input type="checkbox" class="h-4 w-4 text-blue-600 bg-neutral-700 border-neutral-600 rounded focus:ring-blue-500" v-model="showAltTakes" />
            <span>Alt Takes</span>
          </label>
          <label class="flex items-center space-x-2 text-sm">
            <input type="checkbox" class="h-4 w-4 text-blue-600 bg-neutral-700 border-neutral-600 rounded focus:ring-blue-500" v-model="showStoryBeats" />
            <span>Story Beats</span>
          </label>
        </div>
        
        <div class="flex items-center space-x-2 ml-4 border-l border-neutral-700 pl-4">
          <button class="btn-accent-blue hover:bg-blue-700 px-4 py-1.5 text-sm flex items-center space-x-1" @click="createAssembly">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            <span>Create Assembly</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Main Reel Area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Transcript Strip (optional) -->
      <div v-if="showTranscript" class="bg-neutral-800/50 border-b border-neutral-700 px-4 py-2 max-h-32 overflow-y-auto">
        <div class="flex items-start space-x-2 overflow-x-auto pb-2">
          <TranscriptSegment 
            v-for="segment in visibleTranscriptSegments" 
            :key="segment.id"
            :segment="segment"
            :is-active="segment.startTime <= playhead && segment.endTime > playhead"
            @click="seekToTime(segment.startTime)"
          />
        </div>
      </div>
      
      <!-- Main Reel - The Signature Surface -->
      <div class="flex-1 relative overflow-hidden bg-neutral-900" ref="reelContainer">
        <!-- Time Ruler -->
        <div class="absolute top-0 left-0 right-0 h-8 bg-neutral-800/80 border-b border-neutral-700 z-10 flex items-end px-4" ref="timeRuler">
          <TimeMarker 
            v-for="marker in timeMarkers" 
            :key="marker.time"
            :marker="marker"
            :zoom="zoomLevel"
            :container-width="reelWidth"
          />
        </div>
        
        <!-- Story Beat Markers -->
        <div v-if="showStoryBeats" class="absolute top-8 left-0 right-0 h-6 z-10 px-4 pointer-events-none">
          <StoryBeatMarker 
            v-for="beat in storyBeats" 
            :key="beat.id"
            :beat="beat"
            :zoom="zoomLevel"
            :container-width="reelWidth"
            :total-duration="totalDuration"
          />
        </div>
        
        <!-- Main Reel Content -->
        <div 
          class="absolute top-14 left-0 right-0 bottom-0 overflow-x-auto"
          ref="reelContent"
          @scroll="onReelScroll"
        >
          <div 
            class="flex items-start min-h-full"
            :style="{ width: `${reelWidth}px` }"
            ref="reelTrack"
          >
            <SelectsItem 
              v-for="(selection, index) in selections" 
              :key="selection.id"
              :selection="selection"
              :index="index"
              :zoom="zoomLevel"
              :is-selected="selectedIndex === index"
              :show-alt-takes="showAltTakes"
              :alt-takes="getAltTakes(selection.assetId)"
              @click="selectItem(index)"
              @insert="insertAtPlayhead(selection)"
              @replace="replaceAtPlayhead(selection)"
              @append="appendToReel(selection)"
              @seek="seekToTime"
              @remove="removeFromReel(index)"
            />
          </div>
        </div>
        
        <!-- Playhead -->
        <div 
          class="absolute top-8 bottom-0 w-px bg-blue-500 pointer-events-none z-20"
          :style="{ left: `${(playhead / totalDuration) * reelWidth}px` }"
        >
          <div class="absolute -top-2 left-1/2 -translate-x-1/2 w-3 h-3 bg-blue-500 rounded-full border-2 border-neutral-900" />
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-3 h-3 bg-blue-500 rounded-full border-2 border-neutral-900" />
        </div>
        
        <!-- Drop Zone Indicator -->
        <div 
          v-if="dragOverIndex !== null" 
          class="absolute top-14 bottom-0 w-2 bg-blue-500/50 pointer-events-none z-15"
          :style="{ left: `${dragOverIndex * (itemBaseWidth * zoomLevel) + (dragOverIndex * itemGap)}px` }"
        />
      </div>
      
      <!-- Alternate Takes Strip (optional) -->
      <div v-if="showAltTakes && selectedAltTakes.length > 0" class="bg-neutral-800/50 border-t border-neutral-700 px-4 py-2 max-h-32 overflow-x-auto">
        <div class="flex items-start space-x-2 overflow-x-auto pb-2">
          <AltTakeItem 
            v-for="take in selectedAltTakes" 
            :key="take.id"
            :take="take"
            @click="swapWithAltTake(take)"
          />
        </div>
      </div>
    </div>
    
    <!-- Bottom Status Bar -->
    <div class="bg-neutral-800 border-t border-neutral-700 px-4 py-2 flex items-center justify-between text-sm text-neutral-400">
      <div class="flex items-center space-x-4">
        <span>{{ selections.length }} selections</span>
        <span>•</span>
        <span>{{ formatDuration(totalDuration) }} total</span>
        <span v-if="selectedIndex !== null">• Selection {{ selectedIndex + 1 }}</span>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-neutral-500">Zoom:</span>
        <input 
          type="range" 
          min="0.25" 
          max="4" 
          step="0.25" 
          v-model="zoomLevel"
          class="w-32"
        >
        <span class="w-10 text-right">{{ Math.round(zoomLevel * 100) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, ref as vueRef, onUnmounted } from 'vue'

const props = defineProps({
  initialSelections: Array
})

const emit = defineEmits(['assemblyCreated', 'selectionChanged', 'playheadChanged'])

// State
const playhead = ref(0)
const isPlaying = ref(false)
const zoomLevel = ref(1)
const selectedIndex = ref(null)
const showTranscript = ref(true)
const showAltTakes = ref(false)
const showStoryBeats = ref(true)
const dragOverIndex = ref(null)
const reelContainer = vueRef(null)
const reelContent = vueRef(null)
const reelTrack = vueRef(null)
const timeRuler = vueRef(null)

// Mock data
const selections = ref(props.initialSelections || [
  {
    id: 'sel-001',
    assetId: 'asset-001',
    inPoint: 12.5,
    outPoint: 18.3,
    startTime: 0,
    endTime: 5.8,
    metadata: {
      shotType: 'Medium Close-up',
      emotion: 'Hopeful',
      storyBeat: 'Product Introduction',
      aiRationale: 'Strong eye contact and natural lighting'
    }
  },
  {
    id: 'sel-002',
    assetId: 'asset-002',
    inPoint: 5.2,
    outPoint: 9.8,
    startTime: 5.8,
    endTime: 10.4,
    metadata: {
      shotType: 'Two-shot',
      emotion: 'Engaged',
      storyBeat: 'Feature Explanation',
      aiRationale: 'Good chemistry between subjects'
    }
  },
  {
    id: 'sel-003',
    assetId: 'asset-003',
    inPoint: 22.1,
    outPoint: 27.6,
    startTime: 10.4,
    endTime: 15.9,
    metadata: {
      shotType: 'Wide Establishing',
      emotion: 'Peaceful',
      storyBeat: 'Product in Environment',
      aiRationale: 'Beautiful natural lighting and composition'
    }
  },
  {
    id: 'sel-004',
    assetId: 'asset-004',
    inPoint: 2.0,
    outPoint: 4.5,
    startTime: 15.9,
    endTime: 18.4,
    metadata: {
      shotType: 'Close-up',
      emotion: 'Curious',
      storyBeat: 'Detail Reveal',
      aiRationale: 'Sharp focus on product details'
    }
  },
  {
    id: 'sel-005',
    assetId: 'asset-005',
    inPoint: 15.2,
    outPoint: 22.6,
    startTime: 18.4,
    endTime: 25.8,
    metadata: {
      shotType: 'Two-shot',
      emotion: 'Excited',
      storyBeat: 'Feature Demo',
      aiRationale: 'Dynamic interaction between users'
    }
  }
])

// Mock alt takes
const altTakesData = ref({
  'asset-001': [
    { id: 'alt-001a', assetId: 'asset-001', inPoint: 13.2, outPoint: 19.0, label: 'Take 2 - Slightly wider' },
    { id: 'alt-001b', assetId: 'asset-001', inPoint: 11.8, outPoint: 17.5, label: 'Take 3 - Different angle' }
  ],
  'asset-002': [
    { id: 'alt-002a', assetId: 'asset-002', inPoint: 4.8, outPoint: 9.2, label: 'Take 2 - Better delivery' }
  ],
  'asset-003': [
    { id: 'alt-003a', assetId: 'asset-003', inPoint: 21.5, outPoint: 26.8, label: 'Take 2 - Longer hold' },
    { id: 'alt-003b', assetId: 'asset-003', inPoint: 23.0, outPoint: 28.5, label: 'Take 3 - Pan right' }
  ],
  'asset-004': [
    { id: 'alt-004a', assetId: 'asset-004', inPoint: 1.5, outPoint: 4.0, label: 'Take 2 - Closer' }
  ],
  'asset-005': [
    { id: 'alt-005a', assetId: 'asset-005', inPoint: 14.5, outPoint: 21.8, label: 'Take 2 - More energy' },
    { id: 'alt-005b', assetId: 'asset-005', inPoint: 16.0, outPoint: 23.2, label: 'Take 3 - Different framing' }
  ]
})

// Story beats
const storyBeats = ref([
  { id: 'beat-1', time: 0, label: 'Intro', color: '#3b82f6' },
  { id: 'beat-2', time: 5.8, label: 'Features', color: '#8b5cf6' },
  { id: 'beat-3', time: 10.4, label: 'Environment', color: '#ec4899' },
  { id: 'beat-4', time: 15.9, label: 'Details', color: '#f59e0b' },
  { id: 'beat-5', time: 18.4, label: 'Demo', color: '#10b981' }
])

// Mock transcript segments
const transcriptSegments = ref([
  { id: 'ts-1', startTime: 0, endTime: 5.8, text: 'Welcome to our new product line...' },
  { id: 'ts-2', startTime: 5.8, endTime: 10.4, text: 'Let me show you the key features...' },
  { id: 'ts-3', startTime: 10.4, endTime: 15.9, text: 'This is how it looks in the real world...' },
  { id: 'ts-4', startTime: 15.9, endTime: 18.4, text: 'Notice the attention to detail...' },
  { id: 'ts-4', startTime: 18.4, endTime: 25.8, text: 'And here is it in action...' }
])

// Computed
const totalDuration = computed(() => {
  return selections.value.length > 0 
    ? Math.max(...selections.value.map(s => s.endTime))
    : 60
})

const reelWidth = computed(() => {
  return Math.max(totalDuration.value * 200 * zoomLevel.value, 800)
})

const itemBaseWidth = 200
const itemGap = 8

const timeMarkers = computed(() => {
  const markers = []
  const interval = getTimeInterval()
  for (let t = 0; t <= totalDuration.value; t += interval) {
    markers.push({ time: t, label: formatTime(t) })
  }
  return markers
})

const visibleTranscriptSegments = computed(() => {
  return transcriptSegments.value.filter(s => 
    s.endTime >= playhead.value - 10 && s.startTime <= playhead.value + 30
  )
})

const selectedAltTakes = computed(() => {
  if (selectedIndex.value === null) return []
  const sel = selections.value[selectedIndex.value]
  if (!sel) return []
  return altTakesData.value[sel.assetId] || []
})

const getAltTakes = (assetId) => {
  return altTakesData.value[assetId] || []
}

const getTimeInterval = () => {
  const pixelsPerSecond = 200 * zoomLevel.value
  if (pixelsPerSecond > 400) return 1
  if (pixelsPerSecond > 200) return 2
  if (pixelsPerSecond > 100) return 5
  if (pixelsPerSecond > 50) return 10
  return 30
}

// Methods
const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600).toString().padStart(2, '0')
  const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0')
  const s = Math.floor(seconds % 60).toString().padStart(2, '0')
  const f = Math.floor((seconds % 1) * 24).toString().padStart(2, '0')
  return `${h}:${m}:${s}:${f}`
}

const formatDuration = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}h ${m}m ${s}s`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value * 1.5, 4)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value / 1.5, 0.25)
}

const togglePlay = () => {
  isPlaying.value = !isPlaying.value
  if (isPlaying.value) startPlayback()
  else stopPlayback()
}

const startPlayback = () => {
  // In real implementation, this would use requestAnimationFrame
  // For demo, just update playhead
  const animate = () => {
    if (!isPlaying.value) return
    playhead.value += 0.1
    if (playhead.value >= totalDuration.value) {
      playhead.value = 0
    }
    requestAnimationFrame(animate)
  }
  requestAnimationFrame(animate)
}

const stopPlayback = () => {
  isPlaying.value = false
}

const jumpToStart = () => { playhead.value = 0 }
const jumpToEnd = () => { playhead.value = totalDuration.value }
const stepBack = () => { playhead.value = Math.max(0, playhead.value - 1/24) }
const stepForward = () => { playhead.value = Math.min(totalDuration.value, playhead.value + 1/24) }

const seekToTime = (time) => {
  playhead.value = Math.max(0, Math.min(time, totalDuration.value))
  emit('playheadChanged', playhead.value)
}

const onReelScroll = (e) => {
  // Sync time ruler scroll
  if (timeRuler.value) {
    timeRuler.value.scrollLeft = e.target.scrollLeft
  }
}

const selectItem = (index) => {
  selectedIndex.value = index
  emit('selectionChanged', index)
}

const insertAtPlayhead = (selection) => {
  // Find position based on playhead
  let insertIndex = selections.value.findIndex(s => s.startTime > playhead.value)
  if (insertIndex === -1) insertIndex = selections.value.length
  
  const newSelection = {
    ...selection,
    id: `sel-${Date.now()}`,
    startTime: playhead.value,
    endTime: playhead.value + (selection.outPoint - selection.inPoint)
  }
  
  selections.value.splice(insertIndex, 0, newSelection)
  // Update subsequent start/end times
  updateSelectionTimes(insertIndex)
  emit('selectionChanged', insertIndex)
}

const replaceAtPlayhead = (selection) => {
  if (selectedIndex.value !== null) {
    const current = selections.value[selectedIndex.value]
    const duration = selection.outPoint - selection.inPoint
    selections.value[selectedIndex.value] = {
      ...selection,
      id: current.id,
      startTime: current.startTime,
      endTime: current.startTime + duration
    }
    updateSelectionTimes(selectedIndex.value)
  }
}

const appendToReel = (selection) => {
  const lastSelection = selections.value[selections.value.length - 1]
  const newStartTime = lastSelection ? lastSelection.endTime : 0
  const duration = selection.outPoint - selection.inPoint
  
  selections.value.push({
    ...selection,
    id: `sel-${Date.now()}`,
    startTime: newStartTime,
    endTime: newStartTime + duration
  })
  emit('selectionChanged', selections.value.length - 1)
}

const removeFromReel = (index) => {
  selections.value.splice(index, 1)
  updateSelectionTimes(index)
  if (selectedIndex.value >= index) {
    selectedIndex.value = Math.max(0, selectedIndex.value - 1)
  }
  emit('selectionChanged', selectedIndex.value)
}

const updateSelectionTimes = (fromIndex = 0) => {
  let currentTime = 0
  for (let i = fromIndex; i < selections.value.length; i++) {
    const duration = selections.value[i].outPoint - selections.value[i].inPoint
    selections.value[i].startTime = currentTime
    selections.value[i].endTime = currentTime + duration
    currentTime += duration
  }
}

const swapWithAltTake = (altTake) => {
  if (selectedIndex.value !== null) {
    const current = selections.value[selectedIndex.value]
    const duration = altTake.outPoint - altTake.inPoint
    selections.value[selectedIndex.value] = {
      ...current,
      inPoint: altTake.inPoint,
      outPoint: altTake.outPoint,
      endTime: current.startTime + duration
    }
  }
}

const createAssembly = () => {
  emit('assemblyCreated', {
    selections: selections.value,
    totalDuration: totalDuration.value
  })
}

// Keyboard shortcuts
const handleKeydown = (e) => {
  if (e.target.tagName === 'INPUT') return
  
  switch (e.key) {
    case ' ':
      e.preventDefault()
      togglePlay()
      break
    case 'ArrowLeft':
      e.preventDefault()
      stepBack()
      break
    case 'ArrowRight':
      e.preventDefault()
      stepForward()
      break
    case 'Home':
      e.preventDefault()
      jumpToStart()
      break
    case 'End':
      e.preventDefault()
      jumpToEnd()
      break
    case 'Delete':
    case 'Backspace':
      if (selectedIndex.value !== null) {
        e.preventDefault()
        removeFromReel(selectedIndex.value)
      }
      break
    case '=':
    case '+':
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault()
        zoomIn()
      }
      break
    case '-':
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault()
        zoomOut()
      }
      break
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  // Initialize reel width
  if (reelTrack.value) {
    reelTrack.value.style.width = `${reelWidth.value}px`
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.btn-tool {
  @apply p-2 rounded hover:bg-neutral-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.selects-item {
  @apply bg-neutral-800 border border-neutral-700 rounded-lg overflow-hidden transition-all duration-200;
}

.selects-item.selected {
  @apply border-blue-500 ring-2 ring-blue-500/50;
}

.selects-item:hover {
  @apply border-neutral-600;
}

.reel-track {
  @apply flex items-start gap-2 p-4;
}

.time-marker {
  @apply absolute top-0 bottom-0 w-px bg-neutral-600/50;
}

.time-marker-label {
  @apply absolute bottom-full left-1/2 -translate-x-1/2 mb-1 text-xs text-neutral-500 whitespace-nowrap;
}

.story-beat-marker {
  @apply absolute top-0 bottom-0 w-1.5 rounded opacity-80;
}

.alt-take-item {
  @apply bg-neutral-700 border border-neutral-600 rounded-lg p-2 text-sm hover:border-blue-500 cursor-pointer transition-colors;
}

.transcript-segment {
  @apply bg-neutral-700 rounded px-3 py-1.5 text-sm cursor-pointer hover:bg-neutral-600 transition-colors whitespace-nowrap;
}

.transcript-segment.active {
  @apply bg-blue-600 text-white;
}
</style>