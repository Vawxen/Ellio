// Simple state management store for the Ellio MVP Frontend
// Following the immutable patterns from Ellio's backend

import { ref } from 'vue'

// Create store
const state = ref({
  // Project information
  project: {
    id: null,
    name: '',
    brief: null,
    createdAt: null,
    updatedAt: null
  },
  
  // Media library
  mediaLibrary: {
    assets: [],
    selectedAsset: null,
    filters: {
      status: '',
      type: '',
      search: ''
    }
  },
  
  # Selects reel (the signature surface from PIN-12)
  selectsReel: {
    selections: [],  // Array of { inPoint, outPoint, assetId, metadata }
    playhead: 0,     // Current playhead position in seconds
    isPlaying: false,
    volume: 1.0
  },
  
  # Timeline for rough-cut assembly
  timeline: {
    tracks: [],      // Array of tracks (video, audio, transcripts, etc.)
    playhead: 0,
    isPlaying: false,
    zoomLevel: 1.0,  // Timeline zoom (1.0 = 1sec = 100px)
    markers: []      // In/out points, markers, etc.
  },
  
  # AI interaction state
  aiState: {
    isGenerating: false,
    currentPrompt: '',
    context: null,   // Selected media (clip, range, scene, etc.)
    scope: [],       // AI scope badges: Story, Style, Composition, Motion, Audio
    preservation: 0.5, // 0 = strictly preserve, 1 = creative reinterpretation
    results: [],     // AI generated candidates/versions
    selectedResult: null
  },
  
  # UI state
  uiState: {
    leftRailCollapsed: false,
    rightRailCollapsed: false,
    activeScreen: 'brief',
    notifications: []
  }
})

// Getters (computed properties)
const getters = {
  // Get project brief
  getBrief: () => state.value.project.brief,
  
  // Get selected asset
  getSelectedAsset: () => state.value.mediaLibrary.selectedAsset,
  
  # Get selects reel selections
  getSelectsReelSelections: () => state.value.selectsReel.selections,
  
  # Get current playhead time
  getPlayheadTime: () => state.value.selectsReel.playhead,
  
  # Get AI context
  getAIContext: () => state.value.aiState.context,
  
  # Get AI generation status
  isAIGenerating: () => state.value.aiState.isGenerating
}

// Actions (methods to update state)
const actions = {
  // Project actions
  setProjectBrief: (brief) => {
    state.value.project.brief = brief
    state.value.project.updatedAt = Date.now()
  },
  
  # Media library actions
  setMediaLibraryAssets: (assets) => {
    state.value.mediaLibrary.assets = assets
  },
  
  selectMediaAsset: (assetId) => {
    const asset = state.value.mediaLibrary.assets.find(a => a.id === assetId)
    state.value.mediaLibrary.selectedAsset = asset || null
  },
  
  # Selects reel actions
  addToSelectsReel: (selection) => {
    state.value.selectsReel.selections.push(selection)
  },
  
  removeFromSelectsReel: (index) => {
    state.value.selectsReel.selections.splice(index, 1)
  },
  
  updateSelectsReelPlayhead: (time) => {
    state.value.selectsReel.playhead = time
  },
  
  setSelectsReelPlaying: (isPlaying) => {
    state.value.selectsReel.isPlaying = isPlaying
  },
  
  # Timeline actions
  addTimelineTrack: (track) => {
    state.value.timeline.tracks.push(track)
  },
  
  updateTimelinePlayhead: (time) => {
    state.value.timeline.playhead = time
  },
  
  setTimelinePlaying: (isPlaying) => {
    state.value.timeline.isPlaying = isPlaying
  },
  
  # AI actions
  setAIContext: (context) => {
    state.value.aiState.context = context
  },
  
  setAIGenerating: (isGenerating) => {
    state.value.aiState.isGenerating = isGenerating
  },
  
  setAIPrompt: (prompt) => {
    state.value.aiState.currentPrompt = prompt
  },
  
  setAIScope: (scope) => {
    state.value.aiState.scope = scope
  },
  
  setAIPreservation: (value) => {
    state.value.aiState.preservation = value
  },
  
  addAIResult: (result) => {
    state.value.aiState.results.push(result)
  },
  
  selectAIResult: (result) => {
    state.value.aiState.selectedResult = result
  },
  
  # UI actions
  setLeftRailCollapsed: (collapsed) => {
    state.value.uiState.leftRailCollapsed = collapsed
  },
  
  setRightRailCollapsed: (collapsed) => {
    state.value.uiState.rightRailCollapsed = collapsed
  },
  
  setActiveScreen: (screen) => {
    state.value.uiState.activeScreen = screen
  },
  
  addNotification: (notification) => {
    state.value.uiState.notifications.push({
      id: Date.now() + Math.random(),
      ...notification,
      timestamp: Date.now()
    })
  },
  
  removeNotification: (id) => {
    state.value.uiState.notifications = state.value.uiState.notifications.filter(
      n => n.id !== id
    )
  }
}

// Expose store API
export const store = {
  state,
  getters,
  actions
}

// Export individual parts for convenience
export default store