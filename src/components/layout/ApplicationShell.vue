<template>
  <div class="flex h-screen bg-neutral-900 text-neutral-100">
    <!-- Left Rail: Collapsible Navigation -->
    <LeftRail 
      :is-collapsed="isLeftRailCollapsed"
      @toggle-collapse="toggleLeftRailCollapse"
    />
    
    <!-- Center Canvas: Main Creative Workspace -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <Header />
      <router-view />
    </div>
    
    <!-- Right Rail: Collapsible Inspector -->
    <RightRail 
      :is-collapsed="isRightRailCollapsed"
      @toggle-collapse="toggleRightRailCollapse"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LeftRail from './LeftRail.vue'
import RightRail from './RightRail.vue'
import Header from './Header.vue'

// State for rail collapse states
const isLeftRailCollapsed = ref(false)
const isRightRailCollapsed = ref(false)

const toggleLeftRailCollapse = () => {
  isLeftRailCollapsed.value = !isLeftRailCollapsed.value
}

const toggleRightRailCollapse = () => {
  isRightRailCollapsed.value = !isRightRailCollapsed.value
}
</script>

<style>
/* Application Shell Styles */
</style>