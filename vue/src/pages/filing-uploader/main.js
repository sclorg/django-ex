import Vue from "vue";
import App from "./FilingUploader.vue";
import "core-js/es/array"; // Needed for IE11

Vue.config.productionTip = false;
Vue.component("filing-uploader", App);

new Vue({
  el: "#vue-app",
});
