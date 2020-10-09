<template>
  <div>
    <div
      :class="['image-wrap', isValidImage ? 'valid' : '']"
      @click.prevent="showPreview($event)"
    >
      <img v-if="isValidImage" class="image" :src="file.objectURL" :style="imageStyle" />
      <img 
        class="pdf"
        :src="pdfIconUrl"
        v-if="!this.file.error && file.type === 'application/pdf'"
        width="65" 
        height="65"
      >
      <i class="fa fa-frown-o" v-if="this.file.error"></i>
      <button
        type="button"
        class="btn-remove"
        @click.prevent="$emit('removeclick')"
        aria-label="Delete"
      >
        <i class="fa fa-times-circle"></i>
      </button>
    </div>
    <modal-preview
      :file="file"
      :imageStyle="imageStyle"
      :scale="scale"
      :rotate-val="rotateVal"
      :show-modal="showModal"
      @close="closePreview()"
    />
  </div>
</template>

<script>
  import ModalPreview from "./ModalPreview";
  import rotateFix from "../../utils/rotation";

  export default {
    props: {
      file: Object,
    },
    components: {
      ModalPreview,
    },
    data: function() {
      return {
        showModal: false,
      };
    },
    methods: {
      showPreview($event) {
        if (this.isValidImage) {
          if (
            $event.target.tagName !== "I" &&
            $event.target.tagName !== "BUTTON"
          ) {
            this.showModal = true;
          }
        }
      },
      closePreview() {
        this.showModal = false;
      },
    },
    computed: {
      isValidImage() {
        return (
          this.file.objectURL &&
          !this.file.error &&
          this.file.type !== "application/pdf"
        );
      },
      rotateVal() {
        return rotateFix(this.file.rotation);
      },
      scale() {
        if (!this.file.height || this.file.height <= 0) {
          return 1;
        }
        return this.file.width / this.file.height;
      },
      imageStyle() {
        const shift = -100 * this.scale;
        if (this.rotateVal === 90) {
          return `transform:rotate(90deg) translateY(${shift}%) scale(${this.scale}); transform-origin: top left;`;
        }
        if (this.rotateVal === 270) {
          return `transform:rotate(270deg) translateX(${shift}%) scale(${this.scale}); transform-origin: top left;`;
        }
        if (this.rotateVal === 180) {
          return "transform:rotate(180deg);";
        }
        return "";
      },
      pdfIconUrl() {
        return `${this.$parent.$parent.$parent.$parent.proxyRootPath}static/svg/pdf-icon.svg`;
      }
    },
  };
</script>

<style scoped lang="scss">
  .image-wrap {
    height: 160px;
    border: 1px solid black;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    background-color: white;
    overflow: hidden;
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;

    img.image {
      position: absolute;
      top: 0;
      left: 0;
    }

    img.pdf {
      margin-left: 45px;
    }

    i.fa-frown-o {
      display: block;
      font-size: 48px;
      margin-left: 60px;
      color: #eee;
    }

    &::after {
      font-family: FontAwesome;
      content: "\f06e";
      margin: auto;
      font-size: 43px;
      color: transparent;
    }

    &.valid:hover {
      background-color: #365ebe;
      cursor: pointer;

      button.btn-remove {
        background-color: transparent;

        i.fa {
          color: white;
        }
      }
    }

    &:hover::after {
      color: white;
    }

    &:hover img.image {
      opacity: 0.12;
    }
  }

  button {
    &.btn-remove {
      position: absolute;
      top: 130px;
      left: 130px;
      background-color: white;
      border-radius: 10px;
      height: 18px;
      line-height: 1;
      z-index: 4;

      i.fa {
        color: #365ebe;
        font-size: 23px;

        &::before {
          display: block;
          margin-top: -2px;
          margin-left: -1px;
        }
      }
    }
  }
</style>
