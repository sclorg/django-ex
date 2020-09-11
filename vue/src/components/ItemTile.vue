<template>
  <div class="item-tile" v-if="file.progress === '100.00' || file.error">
    <div class="image-wrap">
      <img v-if="file.objectURL && !file.error" :src="file.objectURL" height="auto" />
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
          <button type="button" aria-label="Rotate counter-clockwise">
            <i class="fa fa-undo"></i>
          </button>
          <button type="button" aria-label="Rotate clockwise">
            <i class="fa fa-undo fa-flip-horizontal"></i>
          </button>
        </div>
        <div class="alert alert-danger" style="padding: 4px; margin-bottom: 0" v-if="file.error">Upload Error</div>
      </div>
    </div>
  </div>
  <div class="item-tile" v-else-if="file.progress !== '0.00'"> 
    <div class="status-wrap">
      <div>
      Uploading... {{ file.progress}}%
      </div>
      <div class="progress">
        <div :style="'width:' + file.progress + '%'">
        </div>
      </div>
    </div>
  </div>
  <div class="item-tile" v-else> 
    <div class="status-wrap">
      <div>
      Waiting...
      </div>
      <div class="progress"></div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    file: Object,
    index: Number,
    fileCount: Number
  }
}
</script>

<style scoped lang="scss">
    .item-tile {
      margin-bottom: 5px;
      position: relative;

      .image-wrap, .status-wrap {
        height: 160px;
        border: 1px solid black;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        background-color: white;
      }

      .image-wrap {
        overflow-y: hidden;
      }

      .status-wrap {
        border-bottom-left-radius: 6px;
        border-bottom-right-radius: 6px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
      }

      .progress {
        width: calc(100% - 1.5px);
        background-color: #F2F2F3;
        height: 22px;
        position: absolute;
        bottom: -19.5px;
        left: 1px;
        border-radius: 0;
        border-bottom-left-radius: 4px;
        border-bottom-right-radius: 4px;

        > div {
          background-color: #365EBE;
          height: 22px;
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

      img {
        width: 98%;
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
