<template>
  <transition-group name="fade" class="pointer-events-none">
    <div 
      v-for="notification in notifications" 
      :key="notification.id"
      class="fixed z-50 top-4 right-4 max-w-xs w-full"
    >
      <notification-card 
        :notification="notification"
        @close="removeNotification(notification.id)"
      />
    </div>
  </transition-group>
</template>

<script setup>
import { ref } from 'vue'
import NotificationCard from './NotificationCard.vue'

const props = defineProps({
  notifications: Array
})

const emit = defineEmits(['removeNotification'])

const removeNotification = (id) => {
  emit('removeNotification', id)
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>