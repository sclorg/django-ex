import Vue from 'vue';
import App from './InitialFiling.vue';

Vue.config.productionTip = false;
Vue.component("initial-filing-uploader", App);

new Vue({ 
  el: '#vue-app' 
});
