<template>
  <div id="app">
    <template v-for="item in formTypes">
        <div>
          <Uploader v-bind:doc-type="item.doc_type" :party="item.party_code"/>
        </div>
    </template>
  </div>
</template>

<script>
  import Uploader from "../../components/Uploader/Uploader.vue";

  export default {
    name: "App",
    components: {
      Uploader,
    },
    props: {
      formTypes: Array,
      proxyRootPath: String,
    },
  };
</script>
