<template>
  <header class="bg-neutral-800 border-b border-neutral-700 px-6 py-4 flex items-center justify-between">
    <div class="flex items-center space-x-4">
      <div class="w-8 h-8 bg-neutral-600 rounded flex items-center justify-center">
        <span class="text-xs font-medium">E</span>
      </div>
      <h1 class="text-lg font-semibold">Ellio Video Editor</h1>
    </div>
    
    <div class="flex items-center space-x-3">
      <button class="btn-neutral hover:bg-neutral-700">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <span class="ml-1">Play</span>
      </button>
      <button class="btn-neutral hover:bg-neutral-700">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
        <span class="ml-1">Pause</span>
      </button>
      <button class="btn-accent-blue hover:bg-blue-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
        <span class="ml-1">Render</span>
      </button>
    </div>
  </header>
</template>

<script setup>
// Header component - simple placeholder for now
</script>

<style scoped>
.btn-neutral {
  @apply bg-neutral-700 hover:bg-neutral-600 text-neutral-200 px-3 py-1.5 rounded text-sm flex items-center space-x-1 transition-colors duration-200;
}

.btn-accent-blue {
  @apply bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded text-sm flex items-center space-x-1 transition-colors duration-200;
}
</style>