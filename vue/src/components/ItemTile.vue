<template>
  <div class="item-tile" v-if="file.progress === '100.00' || file.error">
    <div class="image-wrap">
      <img v-if="file.objectURL && !file.error" :src="file.objectURL" height="auto" :class="imageClass" />
      <button type="button" class="btn-remove" @click.prevent="$emit('remove')" aria-label="Delete">
        <i class="fa fa-times-circle"></i>
      </button>
    </div>
    <div class="bottom-wrapper">
      <div class="item-text">
        {{file.name}} ({{ Math.round(file.size/1024 * 100) / 100 }}KB)
      </div>
      <div class="button-wrapper">
        <div v-if="!file.active && file.success">
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
    <ProgressBar :file="file"/>
  </div>
</template>

<script>
import ProgressBar from './ProgressBar'

export default {
  props: {
    file: Object,
    index: Number,
    fileCount: Number
  },
  components: {
    ProgressBar
  },
  computed: {
    imageClass() {
      let rotation = this.file.rotation;
      while (rotation < 0) {
        rotation += 360;
      }
      while (rotation > 360) {
        rotation -= 360;
      }
      if (rotation === 90) {
        return 'rotate-90';
      }
      if (rotation === 180) {
        return 'rotate-180';
      }
      if (rotation === 270) {
        return 'rotate-270';
      }      
      return 'rotate-0';
    }
  },
}
</script>

<style scoped lang="scss">
    .item-tile {
      margin-bottom: 5px;
      position: relative;

      .image-wrap {
        height: 160px;
        border: 1px solid black;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        background-color: white;
      }

      .image-wrap {
        overflow-y: hidden;
      }

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

      img.rotate-0 {
        width: 98%;
      }

      img.rotate-90 {
        transform: rotate(90deg);
        height: 98%;
        max-width: 98%;        
      }

      img.rotate-180 {
        transform: rotate(180deg);
        width: 98%;
      }
      
      img.rotate-270 {
        transform: rotate(270deg);
        height: 98%;
        max-width: 98%;
      }

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

        &.btn-remove {
          position: absolute;
          top: 130px;
          left: 130px;
          background-color: white;
          border-radius: 10px;
          height: 22px;
          line-height: 1;

          i.fa {
            color: #365EBE;
            font-size: 23px;
          }
        }
      }
    }
</style>
