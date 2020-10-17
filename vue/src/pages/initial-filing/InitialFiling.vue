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
      formTypes: JSON,
      proxyRootPath: String,
    },
  };
</script>

<style scoped lang="scss">
  .upload-area {
    padding: 32px 20px 32px 20px;
    margin-bottom: 50px;
    background-color: #f2f2f2;
    border: 1px solid #ddd;
    border-radius: 8px;
  }
</style>
