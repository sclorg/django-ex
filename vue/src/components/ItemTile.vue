<template>
  <div class="item-tile" v-if="file.progress === '100.00' || file.error">
    <div class="image-wrap" @click.prevent="showImage($event)">
      <img v-if="file.objectURL  && !file.error && file.type !== 'application/pdf'" :src="file.objectURL" :style="imageStyle"/>
      <i class="fa fa-file-pdf-o" v-if="file.type === 'application/pdf'"></i>
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
    <modal v-model="showModal" ref="modal" :footer="false">
      <img v-if="file.objectURL  && !file.error && file.type !== 'application/pdf'" :src="file.objectURL" :style="imageStyle">
    </modal>
  </div>
  <div v-else>
    <ProgressBar :file="file"/>
  </div>
</template>

<script>
import ProgressBar from './ProgressBar'
import { Modal } from 'uiv';

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
    Modal
  },
  methods: {
    showImage($event) {
      if ($event.target.tagName !== 'I' && $event.target.tagName !== 'BUTTON') {
        this.showModal = true;
      }
    }
  },
  computed: {
    rotateVal() {
      let rotation = this.file.rotation;
      while (rotation < 0) {
        rotation += 360;
      }
      while (rotation > 360) {
        rotation -= 360;
      }
      if (rotation === 90) {
        return 90;
      }
      if (rotation === 180) {
        return 180;
      }
      if (rotation === 270) {
        return 270;
      }      
      return 0;
    },
    imageStyle() {
      if (this.rotateVal === 90) {
        let scale = this.file.width / this.file.height;
        let yshift = -100 * scale;
        return "transform:rotate(90deg) translateY("+yshift+"%) scale("+scale+"); transform-origin: top left;";
      }
      if (this.rotateVal === 270) {
        let scale = this.file.width / this.file.height;
        let xshift = -100 * scale;
        return "transform:rotate(270deg) translateX("+xshift+"%) scale("+scale+"); transform-origin: top left;";
      }
      if (this.rotateVal === 180) {
        return "transform:rotate(180deg);";
      }      
      return '';
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
        overflow: hidden;
        position: relative;
        z-index: 2;

        i.fa-file-pdf-o {
          color: silver;
          display: block;
          font-size: 50px;
          margin-left: 15px;
          margin-top: 15px;
          opacity: 0.75;
        }

        &::after {
          font-family: FontAwesome;
          content: "\f06e";
          position: absolute;
          left: 58px;
          top: 52px; 
          font-size: 43px;
          color: transparent;        
        }

        &:hover {
          background-color: #6484d3;
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

        &:hover img { 
          opacity: 0.3;
        } 
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
          z-index: 4;

          i.fa {
            color: #365EBE;
            font-size: 23px;
          }
        }
      }
    }
</style>

<style lang="css">
    .modal-content {
      background-color: inherit;
      box-shadow: none;
      -webket-box-shadow: none;
      border: none;
    } 

    .modal-content button.close {
      font-size: 80px;
      margin-right: 75px;
      margin-bottom: -100px;
    }
</style>
