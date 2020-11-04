<template>
  <div id="app">
    <template v-for="(item, index) in formTypes">
      <div :key="index">
        <Uploader
          :doc-type="item.doc_type"
          :party="item.party_code"
          :filing-type="filingType"
        />
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
      filingType: String,
      proxyRootPath: String,
    },
  };
</script>
