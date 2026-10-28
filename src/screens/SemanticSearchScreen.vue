<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold mb-4">Footage Library & Semantic Search</h1>
      <p class="text-neutral-400">Search footage using natural language and browse the library</p>
    </div>
    
    <!-- Search Bar -->
    <div class="mb-6">
      <div class="relative max-w-3xl">
        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg class="w-5 h-5 text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </div>
        <input 
          v-model="searchQuery"
          @keyup.enter="performSearch"
          type="text" 
          placeholder="Search footage... e.g., 'quiet close-ups with tension before the reveal', 'sunset landscape wide shot', 'dialogue scene interior'"
          class="w-full pl-12 pr-4 py-3 bg-neutral-700 border border-neutral-600 rounded-lg text-neutral-100 placeholder-neutral-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base"
        />
        <button 
          @click="performSearch"
          :disabled="isSearching"
          class="absolute right-3 top-1/2 -translate-y-1/2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <span v-if="isSearching" class="flex items-center space-x-2">
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span>Searching...</span>
          </span>
          <span v-else>Search</span>
        </button>
      </div>
      
      <!-- Search Filters -->
      <div class="flex flex-wrap items-center gap-4 mt-4">
        <div class="flex items-center space-x-2">
          <label class="text-sm font-medium text-neutral-300">Filters:</label>
          <select class="bg-neutral-700 border border-neutral-600 rounded px-3 py-1.5 text-sm" v-model="selectedType">
            <option value="">All Types</option>
            <option value="video">Video</option>
            <option value="image">Image</option>
            <option value="audio">Audio</option>
          </select>
          <select class="bg-neutral-700 border border-neutral-600 rounded px-3 py-1.5 text-sm" v-model="selectedStatus">
            <option value="">All Status</option>
            <option value="ready">Ready</option>
            <option value="processing">Processing</option>
            <option value="error">Error</option>
          </select>
        </div>
        
        <div class="flex items-center space-x-2 ml-auto">
          <label class="flex items-center space-x-2 text-sm">
            <input type="checkbox" class="h-4 w-4 text-blue-600 bg-neutral-700 border-neutral-600 rounded focus:ring-blue-500" v-model="showOnlySelects" />
            <span>Show only selects</span>
          </label>
        </div>
      </div>
    </div>
    
    <!-- View Mode Toggle -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-2">
        <span class="text-sm text-neutral-400">{{ filteredAssets.length }} results</span>
        <div class="flex bg-neutral-700 rounded-lg p-1">
          <button 
            @click="viewMode = 'grid'" 
            :class="viewMode === 'grid' ? 'bg-neutral-600' : ''"
            class="p-2 rounded transition-colors"
            title="Grid View"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
          </button>
          <button 
            @click="viewMode = 'list'" 
            :class="viewMode === 'list' ? 'bg-neutral-600' : ''"
            class="p-2 rounded transition-colors"
            title="List View"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
          </button>
          <button 
            @click="viewMode = 'filmstrip'" 
            :class="viewMode === 'filmstrip' ? 'bg-neutral-600' : ''"
            class="p-2 rounded transition-colors"
            title="Filmstrip View"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
          </button>
        </div>
      </div>
      
      <div class="flex items-center space-x-2">
        <button class="btn-neutral hover:bg-neutral-700 px-3 py-1.5 text-sm flex items-center space-x-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path></svg>
          <span>Add to Bin</span>
        </button>
        <button class="btn-neutral hover:bg-neutral-700 px-3 py-1.5 text-sm flex items-center space-x-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path></svg>
          <span>Create Bin</span>
        </button>
      </div>
    </div>
    
    <!-- Results Grid/List/Filmstrip -->
    <div v-if="isSearching" class="flex justify-center py-12">
      <div class="flex items-center space-x-3 text-neutral-400">
        <svg class="animate-spin h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span class="text-lg">Searching footage...</span>
      </div>
    </div>
    
    <div v-else-if="filteredAssets.length === 0" class="empty-state">
      <svg class="w-16 h-16 mx-auto text-neutral-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      <h3 class="text-xl font-medium text-neutral-300 mb-2">No results found</h3>
      <p class="text-neutral-500">Try adjusting your search query or filters</p>
    </div>
    
    <div v-else>
      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <MediaCard 
          v-for="asset in filteredAssets" 
          :key="asset.id"
          :asset="asset"
          @select="selectAsset"
          @add-to-selects="addToSelects"
          @add-to-bin="addToBin"
          @preview="previewAsset"
        />
      </div>
      
      <!-- List View -->
      <div v-else-if="viewMode === 'list'" class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="text-left text-neutral-500 text-sm border-b border-neutral-700">
              <th class="pb-3 pr-4">Preview</th>
              <th class="pb-3 pr-4">Name</th>
              <th class="pb-3 pr-4">Type</th>
              <th class="pb-3 pr-4">Duration</th>
              <th class="pb-3 pr-4">Status</th>
              <th class="pb-3 pr-4">In/Out</th>
              <th class="pb-3 pr-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="asset in filteredAssets" :key="asset.id" class="border-b border-neutral-800 hover:bg-neutral-800/50">
              <td class="py-3 pr-4">
                <img :src="asset.thumbnail" :alt="asset.name" class="w-16 h-9 object-cover rounded" />
              </td>
              <td class="py-3 pr-4">
                <div class="font-medium truncate max-w-xs">{{ asset.name }}</div>
                <div class="text-xs text-neutral-500">{{ asset.fileSize }}</div>
              </td>
              <td class="py-3 pr-4">
                <span class="inline-block px-2 py-0.5 text-xs bg-neutral-700 rounded">{{ asset.type }}</span>
              </td>
              <td class="py-3 pr-4 text-neutral-300 font-mono">{{ asset.duration }}</td>
              <td class="py-3 pr-4">
                <StatusBadge :status="asset.status" />
              </td>
              <td class="py-3 pr-4 text-neutral-400 font-mono text-sm">
                {{ asset.inPoint || '—' }} / {{ asset.outPoint || '—' }}
              </td>
              <td class="py-3 pr-4">
                <div class="flex items-center space-x-2">
                  <button @click="previewAsset(asset)" class="btn-neutral hover:bg-neutral-700 p-1.5 rounded" title="Preview">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                  </button>
                  <button @click="addToSelects(asset)" class="btn-neutral hover:bg-neutral-700 p-1.5 rounded" title="Add to Selects">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                  </button>
                  <button @click="addToBin(asset)" class="btn-neutral hover:bg-neutral-700 p-1.5 rounded" title="Add to Bin">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2z"></path></svg>
                  </button>
                </div>
              </td            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Filmstrip View -->
      <div v-else-if="viewMode === 'filmstrip'" class="overflow-x-auto pb-4">
        <div class="flex space-x-2 min-w-max">
          <MediaCard 
            v-for="asset in filteredAssets" 
            :key="asset.id"
            :asset="asset"
            :compact="true"
            @select="selectAsset"
            @add-to-selects="addToSelects"
            @add-to-bin="addToBin"
            @preview="previewAsset"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import MediaCard from '../components/media/MediaCard.vue'

const props = defineProps({
  initialAssets: Array
})

const emit = defineEmits(['assetSelected', 'assetAddedToSelects', 'assetAddedToBin', 'assetPreviewed'])

const searchQuery = ref('')
const isSearching = ref(false)
const viewMode = ref('grid')
const selectedType = ref('')
const selectedStatus = ref('')
const showOnlySelects = ref(false)

// Mock assets data - in real app this would come from store
const allAssets = ref([
  {
    id: 'asset-001',
    name: 'DSC_0024.MOV',
    type: 'video',
    thumbnail: 'https://via.placeholder.com/320x180?opening_shot',
    duration: '00:08:15',
    fileSize: '2.4 GB',
    status: 'ready',
    inPoint: '00:00:12:15',
    outPoint: '00:00:18:03',
    isSelect: true,
    metadata: { resolution: '4K', fps: 24, codec: 'ProRes 422' }
  },
  {
    id: 'asset-002',
    name: 'interview_segment.mp4',
    type: 'video',
    thumbnail: 'https://via.placeholder.com/320x180?interview',
    duration: '00:04:22',
    fileSize: '1.8 GB',
    status: 'ready',
    inPoint: '00:00:05:12',
    outPoint: '00:00:09:08',
    isSelect: false,
    metadata: { resolution: '1080p', fps: 30, codec: 'H.264' }
  },
  {
    id: 'asset-003',
    name: 'b-roll_nature.mp4',
    type: 'video',
    thumbnail: 'https://via.placeholder.com/320x180?b-roll',
    duration: '00:12:40',
    fileSize: '3.2 GB',
    status: 'processing',
    inPoint: null,
    outPoint: null,
    isSelect: false,
    metadata: { resolution: '4K', fps: 60, codec: 'ProRes RAW' }
  },
  {
    id: 'asset-004',
    name: 'establishing_shot.mp4',
    type: 'video',
    thumbnail: 'https://via.placeholder.com/320x180?establishing',
    duration: '00:05:12',
    fileSize: '1.2 GB',
    status: 'ready',
    inPoint: '00:00:02:00',
    outPoint: '00:00:04:30',
    isSelect: true,
    metadata: { resolution: '4K', fps: 24, codec: 'ProRes 422' }
  },
  {
    id: 'asset-005',
    name: 'dialogue_scene.mp4',
    type: 'video',
    thumbnail: 'https://via.placeholder.com/320x180?dialogue',
    duration: '00:03:18',
    fileSize: '950 MB',
    status: 'ready',
    inPoint: '00:00:15:22',
    outPoint: '00:00:22:10',
    isSelect: false,
    metadata: { resolution: '1080p', fps: 24, codec: 'H.265' }
  },
  {
    id: 'asset-006',
    name: 'landscape_shot.mp4',
    type: 'video',
    thumbnail: 'https://via.placeholder.com/320x180?landscape',
    duration: '00:01:55',
    fileSize: '650 MB',
    status: 'error',
    inPoint: null,
    outPoint: null,
    isSelect: false,
    metadata: { resolution: '4K', fps: 24, codec: 'ProRes 422' }
  },
  {
    id: 'asset-007',
    name: 'product_closeup.mp4',
    type: 'video',
    thumbnail: 'https://via.placeholder.com/320x180?product',
    duration: '00:00:45',
    fileSize: '320 MB',
    status: 'ready',
    inPoint: '00:00:00:00',
    outPoint: '00:00:00:45',
    isSelect: false,
    metadata: { resolution: '4K', fps: 120, codec: 'ProRes 4444' }
  },
  {
    id: 'asset-008',
    name: 'drone_aerial.mp4',
    type: 'video',
    thumbnail: 'https://via.placeholder.com/320x180?drone',
    duration: '00:02:30',
    fileSize: '890 MB',
    status: 'ready',
    inPoint: '00:00:01:00',
    outPoint: '00:00:02:15',
    isSelect: true,
    metadata: { resolution: '5.2K', fps: 30, codec: 'H.265' }
  }
])

// Merge with initial assets if provided
if (props.initialAssets && props.initialAssets.length > 0) {
  allAssets.value = [...allAssets.value, ...props.initialAssets]
}

const filteredAssets = computed(() => {
  return allAssets.value.filter(asset => {
    // Search query filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const matchesName = asset.name.toLowerCase().includes(query)
      const matchesMetadata = Object.values(asset.metadata || {}).some(v => 
        String(v).toLowerCase().includes(query)
      )
      if (!matchesName && !matchesMetadata) return false
    }
    
    // Type filter
    if (selectedType.value && asset.type !== selectedType.value) return false
    
    // Status filter
    if (selectedStatus.value && asset.status !== selectedStatus.value) return false
    
    // Show only selects filter
    if (showOnlySelects.value && !asset.isSelect) return false
    
    return true
  })
})

const performSearch = () => {
  isSearching.value = true
  // Simulate search delay
  setTimeout(() => {
    isSearching.value = false
  }, 800)
}

const selectAsset = (asset) => {
  emit('assetSelected', asset)
}

const addToSelects = (asset) => {
  asset.isSelect = !asset.isSelect
  emit('assetAddedToSelects', asset)
}

const addToBin = (asset) => {
  emit('assetAddedToBin', asset)
}

const previewAsset = (asset) => {
  emit('assetPreviewed', asset)
}

// Watch for search query changes for live search
// watch(searchQuery, (newVal) => {
//   if (newVal.length > 2) performSearch()
// }, { debounce: 300 })
</script>

<style scoped>
.empty-state {
  @apply flex flex-col items-center justify-center py-16 px-4 text-center;
}

.status-badge {
  @apply inline-flex items-center px-2 py-0.5 rounded text-xs font-medium;
}

.status-ready {
  @apply bg-green-500/20 text-green-400;
}

.status-processing {
  @apply bg-yellow-500/20 text-yellow-400;
}

.status-error {
  @apply bg-red-500/20 text-red-400;
}
</style>