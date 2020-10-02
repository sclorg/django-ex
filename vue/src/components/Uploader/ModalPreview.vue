<template>
  <modal
    v-model="showModal"
    class="image-preview-modal"
    ref="modal"
    :footer="false"
    @hide="$emit('close')"
  >
    <img
      v-if="file.objectURL && !file.error && file.type !== 'application/pdf'"
      :src="file.objectURL"
      :style="modalImageStyle"
    />
  </modal>
</template>

<script>
  import { Modal } from "uiv";

  export default {
    props: {
      file: Object,
      imageStyle: String,
      rotateVal: Number,
      showModal: Boolean,
      scale: Number,
    },
    components: {
      Modal,
    },
    computed: {
      modalImageStyle() {
        let extraCss = "";
        if (this.rotateVal === 90 || this.rotateVal === 270) {
          if (this.scale < 1) {
            extraCss = " width: 100%; height: inherit !important;";
          } else {
            extraCss = ` width: calc(${85 /
              this.scale}vh); height: inherit !important;`;
          }
        } else {
          extraCss = " max-height: 85vh;";
        }
        return this.imageStyle + extraCss;
      },
    },
  };
</script>

<style lang="scss">
  .image-preview-modal {
    .modal-dialog {
      width: fit-content;
      text-align: center;
    }

    .modal-content {
      background-color: transparent;
      box-shadow: none;
      -webket-box-shadow: none;
      border: none;

      .modal-body,
      .modal-header {
        padding: 0 !important;
      }

      .modal-body {
        img {
          max-width: 780px;
        }
      }

      button.close {
        font-size: 40px;
        color: white;
        opacity: 1;
      }
    }
  }
</style>
