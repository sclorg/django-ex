<template>
  <div class="item-tile" v-if="file.progress === '100.00' || file.error">
    <uploaded-image :file="file" :image-style="imageStyle" @imageclick="showPreview" @removeclick="$emit('remove')" />
    <div class="bottom-wrapper">
      <div class="item-text">
        {{file.name}} ({{ Math.round(file.size/1024 * 100) / 100 }}KB)
      </div>
      <div class="button-wrapper">
        <div v-if="!file.active && file.success && !isPdf">
          <button type="button" @click.prevent="$emit('moveup')" :disabled="index === 0" aria-label="Move down one position">
            <i class="fa fa-chevron-circle-left"></i>
          </button>
          <button type="button" @click.prevent="$emit('movedown')" :disabled="index >= (fileCount - 1)" aria-label="Move up one position">
            <i class="fa fa-chevron-circle-right"></i>
          </button>
          <button type="button" aria-label="Rotate counter-clockwise" @click.prevent="$emit('rotateleft')">
            <i class="fa fa-undo"></i>
          </button>
          <button type="button" aria-label="Rotate clockwise" @click.prevent="$emit('rotateright')">
            <i class="fa fa-undo fa-flip-horizontal"></i>
          </button>
        </div>
        <div class="alert alert-danger" style="padding: 4px; margin-bottom: 0" v-if="file.error">Upload Error</div>
      </div>
    </div>
  </div>
  <div v-else>
    <progress-bar :file="file"/>
  </div>
</template>

<script>
import UploadedImage from './UploadedImage'
import ProgressBar from './ProgressBar'

export default {
  props: {
    file: Object,
    index: Number,
    fileCount: Number
  },
  data: function () {
    return {
      showModal: false,
    }
  },
  components: {
    ProgressBar,
    UploadedImage
  },
  methods: {
    showPreview() {
       this.showModal = true;
    },
    closePreview() {
      this.showModal = false;
    }
  },
  computed: {
    isPdf() {
      return this.file.type === 'application/pdf';
    }
  }
}
</script>

<style lang="scss">
  .item-tile {
    margin-bottom: 5px;
    position: relative;

    .item-text {
      text-align: center;
      min-height: 75px;
      max-height: 75px;
      overflow: hidden;
      padding: 5px;
      line-height: 1.05;
      font-size: 0.95em;
    }

    .button-wrapper {
      text-align: center;
    }

    .bottom-wrapper {
      border-bottom-left-radius: 6px;
      border-bottom-right-radius: 6px;
      border: 1px solid silver;
      background-color: #F2F2F2;
      margin-bottom: 10px;
    }
  }
</style>

<style lang="scss">
  .item-tile {
    button {
      position: relative; 
      z-index: 2;
      background-color: transparent;
      border: none;
      outline: none;
      font-size: 22px;
      padding: 0;
      margin-right: 16px;

      &:disabled {
        i.fa {
          opacity: 0.15;
        }
      }

      &:hover {
        cursor: pointer !important;
      }

      i.fa {
        color: #003366;
      }

      &:last-of-type {
        margin-right: 0;
      }

      &:nth-of-type(2) {
        margin-right: 32px;
      }
    }
  }
</style>