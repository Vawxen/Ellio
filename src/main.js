// Main entry point for the Ellio MVP Frontend
import { createApp } from 'vue'
import ApplicationShell from './components/layout/ApplicationShell.vue'
import { getCurrentRoute } from './router.js'

// Simple component resolver based on route
const componentResolver = {
  CreativeBriefScreen: () => import('./screens/CreativeBriefScreen.vue'),
  IngestReadinessScreen: () => import('./screens/IngestReadinessScreen.vue'),
  SemanticSearchScreen: () => import('./screens/SemanticSearchScreen.vue'),
  SelectsReelScreen: () => import('./screens/SelectsReelScreen.vue'),
  RoughCutAssemblyScreen: () => import('./screens/RoughCutAssemblyScreen.vue'),
  ReviewApprovalScreen: () => import('./screens/ReviewApprovalScreen.vue')
}

// Dynamic component that resolves based on current route
const RouterView = {
  template: `<component :is="component" />`,
  setup() {
    const component = ref(null)
    
    // Watch for route changes and load component
    const loadComponent = async () => {
      const routeName = getCurrentRoute()
      if (routeName && componentResolver[routeName]) {
        try {
          component.value = (await componentResolver[routeName]()).default
        } catch (error) {
          console.error(`Failed to load component ${routeName}:`, error)
          // Fallback to a simple error component
          component.value = {
            template: `<div class="p-6"><h2 class="text-red-500">Error loading component: ${routeName}</h2></div>`
          }
        }
      }
    }
    
    // Initial load
    loadComponent()
    
    // In a real app, we'd watch for route changes
    // For now, we'll just load once
    
    return { component }
  }
}

const app = createApp(ApplicationShell)
app.component('RouterView', RouterView)
app.mount('#app')

console.log('Ellio MVP Frontend initialized')