<template>
  <TheHeader/>
  <img alt="Vue logo" src="./assets/logo.png">
  <!-- <HelloWorld msg="Welcome to Your Vue.js App"/> -->
  <vue/>
</template>

<script>
// import HelloWorld from './components/HelloWorld.vue'
// import TheHeader from './components/TheHeader';
import vue from './components/vue.vue';

export default {
  name: 'App',
  components: {
    // HelloWorld,
    // TheHeader,
    vue
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
