const { createApp, ref } = Vue
      
        createApp({
          setup() {
            const message = ref('Hello vue 3!')
            return {
              message
            }
          }
        }).mount('#myapp')