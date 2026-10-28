// Simple router implementation for the Ellio MVP Frontend
// In a real implementation, we would use Vue Router

import { ref } from 'vue'

// Define routes
const routes = {
  '/': 'CreativeBriefScreen',
  '/brief': 'CreativeBriefScreen',
  '/library': 'IngestReadinessScreen',
  '/search': 'SemanticSearchScreen',
  '/selects': 'SelectsReelScreen',
  '/assembly': 'RoughCutAssemblyScreen',
  '/review': 'ReviewApprovalScreen'
}

// Current route state
const currentRoute = ref('CreativeBriefScreen')

// Navigate to a route
function navigate(path) {
  // Remove leading slash if present
  const cleanPath = path.startsWith('/') ? path.substring(1) : path
  currentRoute.value = routes[cleanPath] || 'CreativeBriefScreen'
  console.log(`Navigating to: ${currentRoute.value}`)
}

// Get current route component name
function getCurrentRoute() {
  return currentRoute.value
}

// Check if route is active
function isRouteActive(routeName) {
  return currentRoute.value === routeName
}

export { navigate, getCurrentRoute, isRouteActive }