<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold mb-4">Ingest and Asset Readiness</h1>
      <p class="text-neutral-400">Monitor the status of your media assets as they are processed</p>
    </div>
    
    <!-- Controls and filters -->
    <div class="flex flex-wrap items-center mb-4 space-x-3">
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium">View:</label>
        <select class="bg-neutral-700 border border-neutral-600 rounded px-3 py-1 text-sm">
          <option value="grid">Grid</option>
          <option value="list">List</option>
          <option value="filmstrip">Filmstrip</option>
        </select>
      </div>
      
      <div class="flex-1">
        <input 
          type="text" 
          placeholder="Search assets..."
          class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded text-neutral-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      
      <button class="btn-neutral hover:bg-neutral-700 px-4 py-2 rounded">
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
        Select All
      </button>
      
      <button class="btn-neutral hover:bg-neutral-700 px-4 py-2 rounded">
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
        Delete Selected
      </button>
    </div>
    
    <!-- Assets grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Asset Card Example 1: Ingesting -->
      <media-card 
        :asset="assets[0]"
        @select="selectAsset"
      />
      
      <!-- Asset Card Example 2: Checksum Verified -->
      <media-card 
        :asset="assets[1]"
        @select="selectAsset"
      />
      
      <!-- Asset Card Example 3: Transcoding -->
      <media-card 
        :asset="assets[2]"
        @select="selectAsset"
      />
      
      <!-- Asset Card Example 4: Proxy Ready -->
      <media-card 
        :asset="assets[3]"
        @select="selectAsset"
      />
      
      <!-- Asset Card Example 5: Transcript Ready -->
      <media-card 
        :asset="assets[4]"
        @select="selectAsset"
      />
      
      <!-- Asset Card Example 6: Analysis Ready -->
      <media-card 
        :asset="assets[5]"
        @select="selectAsset"
      />
      
      <!-- Asset Card Example 7: Error State -->
      <media-card 
        :asset="assets[6]"
        @select="selectAsset"
      />
      
      <!-- Asset Card Example 8: Fully Ready -->
      <media-card 
        :asset="assets[7]"
        @select="selectAsset"
      />
    </div>
    
    <div class="mt-6 pt-4 border-t border-neutral-700 text-center">
      <p class="text-neutral-500">Showing 8 assets</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MediaCard from '../components/media/MediaCard.vue'

// Mock assets data representing different readiness states
const assets = ref([
  {
    id: 'asset-001',
    name: 'DSC_0024.MOV',
    type: 'video',
    original: { ready: false, progress: 65 },
    proxy: { ready: false, progress: 0 },
    transcript: { ready: false, progress: 0 },
    analysis: { ready: false, progress: 0 },
    status: 'ingesting', // uploading, checksum, transcoding, proxy, transcript, analysis, error, ready
    thumbnail: 'https://via.placeholder.com/320x180?original',
    duration: '02:34'
  },
  {
    id: 'asset-002',
    name: 'interview_take_2.mp4',
    type: 'video',
    original: { ready: true, progress: 100 },
    proxy: { ready: false, progress: 0 },
    transcript: { ready: false, progress: 0 },
    analysis: { ready: false, progress: 0 },
    status: 'checksum_verified',
    thumbnail: 'https://via.placeholder.com/320x180?checksum',
    duration: '01:22'
  },
  {
    id: 'asset-003',
    name: 'B-roll_01.mp4',
    type: 'video',
    original: { ready: true, progress: 100 },
    proxy: { ready: false, progress: 45 },
    transcript: { ready: false, progress: 0 },
    analysis: { ready: false, progress: 0 },
    status: 'transcoding',
    thumbnail: 'https://via.placeholder.com/320x180?transcode',
    duration: '00:45'
  },
  {
    id: 'asset-004',
    name: 'establishing_shot.mp4',
    type: 'video',
    original: { ready: true, progress: 100 },
    proxy: { ready: true, progress: 100 },
    transcript: { ready: false, progress: 0 },
    analysis: { ready: false, progress: 0 },
    status: 'proxy_ready',
    thumbnail: 'https://via.placeholder.com/320x180?proxy',
    duration: '05:12'
  },
  {
    id: 'asset-005',
    name: 'dialogue_scene.mp4',
    type: 'video',
    original: { ready: true, progress: 100 },
    proxy: { ready: true, progress: 100 },
    transcript: { ready: true, progress: 100 },
    analysis: { ready: false, progress: 0 },
    status: 'transcript_ready',
    thumbnail: 'https://via.placeholder.com/320x180?transcript',
    duration: '03:18'
  },
  {
    id: 'asset-006',
    name: 'landscape_shot.mp4',
    type: 'video',
    original: { ready: true, progress: 100 },
    proxy: { ready: true, progress: 100 },
    transcript: { ready: true, progress: 100 },
    analysis: { ready: true, progress: 75 },
    status: 'analysis_ready',
    thumbnail: 'https://via.placeholder.com/320x180?analysis',
    duration: '01:55'
  },
  {
    id: 'asset-007',
    name: 'corrupted_file.mov',
    type: 'video',
    original: { ready: false, progress: 0 },
    proxy: { ready: false, progress: 0 },
    transcript: { ready: false, progress: 0 },
    analysis: { ready: false, progress: 0 },
    status: 'error',
    error: 'File format not supported or corrupted',
    thumbnail: 'https://via.placeholder.com/320x180?error',
    duration: '--:--'
  },
  {
    id: 'asset-008',
    name: 'final_shot.mp4',
    type: 'video',
    original: { ready: true, progress: 100 },
    proxy: { ready: true, progress: 100 },
    transcript: { ready: true, progress: 100 },
    analysis: { ready: true, progress: 100 },
    status: 'ready',
    thumbnail: 'https://via.placeholder.com/320x180?ready',
    duration: '02:07'
  }
])

// Handle asset selection
const selectAsset = (asset) => {
  console.log('Asset selected:', asset)
  // In a real app, this would update the selected asset state
  alert(`Selected: ${asset.name}\nStatus: ${asset.status}`)
}
</script>

<style scoped>
/* Ingest Readiness Screen Styles */
</style>