<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold mb-4">Creative Brief</h1>
      <p class="text-neutral-400">Define the vision, goals, and constraints for your video project</p>
    </div>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">Objective</label>
        <textarea 
          v-model="brief.objective"
          class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded text-neutral-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="What is the main goal of this video?"
          rows="2"
        ></textarea>
      </div>
      
      <div>
        <label class="block text-sm font-medium mb-1">Target Audience</label>
        <input 
          v-model="brief.audience"
          type="text"
          class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded text-neutral-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Who is this video for?"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium mb-1">Emotional Tone</label>
        <select 
          v-model="brief.tone"
          class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded text-neutral-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Select emotional tone...</option>
          <option value="inspiring">Inspiring</option>
          <option value="energetic">Energetic</option>
          <option value="calm">Calm</option>
          <option value="mysterious">Mysterious</option>
          <option value="urgent">Urgent</option>
          <option value="joyful">Joyful</option>
          <option value="somber">Somber</option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium mb-1">Story Beats</label>
        <div class="space-y-2">
          <div v-for="(beat, index) in brief.storyBeats" :key="index" class="flex items-center space-x-2">
            <input 
              v-model="brief.storyBeats[index]"
              type="text"
              class="flex-1 px-3 py-2 bg-neutral-700 border border-neutral-600 rounded text-neutral-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Story beat description"
            />
            <button 
              @click="removeStoryBeat(index)"
              class="btn-neutral hover:bg-neutral-700 p-1 rounded"
              :disabled="brief.storyBeats.length <= 1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>
          <button 
            @click="addStoryBeat"
            class="btn-neutral hover:bg-neutral-700 w-full px-3 py-1.5 rounded text-sm flex items-center justify-center"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v12m8-8H4"></path></svg>
            Add Story Beat
          </button>
        </div>
      </div>
      
      <div>
        <label class="block text-sm font-medium mb-1">Deliverables</label>
        <div class="grid grid-cols-2 gap-2">
          <label class="flex items-center space-x-2">
            <input 
              v-model="brief.deliverables.web"
              type="checkbox"
              class="h-4 w-4 text-blue-600 bg-neutral-700 border-neutral-600 rounded focus:ring-blue-500"
            >
            Web Version
          </label>
          <label class="flex items-center space-x-2">
            <input 
              v-model="brief.deliverables.social"
              type="checkbox"
              class="h-4 w-4 text-blue-600 bg-neutral-700 border-neutral-600 rounded focus:ring-blue-500"
            >
            Social Media Clips
          </label>
          <label class="flex items-center space-x-2">
            <input 
              v-model="brief.deliverables.broadcast"
              type="checkbox"
              class="h-4 w-4 text-blue-600 bg-neutral-700 border-neutral-600 rounded focus:ring-blue-500"
            >
            Broadcast
          </label>
          <label class="flex items-center space-x-2">
            <input 
              v-model="brief.deliverables.archive"
              type="checkbox"
              class="h-4 w-4 text-blue-600 bg-neutral-700 border-neutral-600 rounded focus:ring-blue-500"
            >
            Archive
          </label>
        </div>
      </div>
    </form>
    
    <div class="mt-8 pt-4 border-t border-neutral-700">
      <div class="flex justify-end space-x-3">
        <button 
          @click="resetForm"
          class="btn-neutral hover:bg-neutral-700 px-4 py-2 rounded text-sm"
        >
          Reset
        </button>
        <button 
          @click="handleSubmit"
          class="btn-accent-blue hover:bg-blue-700 px-4 py-2 rounded text-sm"
        >
          Start Ingest / Open Library
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Form state
const brief = ref({
  objective: '',
  audience: '',
  tone: '',
  storyBeats: [''],
  deliverables: {
    web: false,
    social: false,
    broadcast: false,
    archive: false
  }
})

const handleSubmit = () => {
  console.log('Creative brief submitted:', brief.value)
  // In a real app, this would navigate to the next screen or update state
  alert('Creative brief saved! Next: Start ingesting your media.')
}

const resetForm = () => {
  brief.value = {
    objective: '',
    audience: '',
    tone: '',
    storyBeats: [''],
    deliverables: {
      web: false,
      social: false,
      broadcast: false,
      archive: false
    }
  }
}

const addStoryBeat = () => {
  brief.value.storyBeats.push('')
}

const removeStoryBeat = (index) => {
  if (brief.value.storyBeats.length > 1) {
    brief.value.storyBeats.splice(index, 1)
  }
}
</script>

<style scoped>
/* Creative Brief Screen Styles */
</style>