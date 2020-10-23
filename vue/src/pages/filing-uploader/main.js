import Vue from "vue";
import App from "./FilingUploader.vue";

Vue.config.productionTip = false;
Vue.component("filing-uploader", App);

new Vue({
  el: "#vue-app",
});
