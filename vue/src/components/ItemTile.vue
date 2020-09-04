<template>
  <div class="item-tile">
    <div class="image-wrap">
      <img v-if="file.blob" :src="file.blob" height="auto" />
      <button type="button"class="btn-remove" @click.prevent="$emit('remove')" aria-label="Delete">
        <i class="fa fa-times-circle"></i>
      </button>
    </div>
    <div class="bottom-wrapper">
      <div class="item-text">
      {{file.name}} ({{ Math.round(file.size/1024 * 100) / 100 }}KB)
      </div>
      <div class="button-wrapper">
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

      .image-wrap {
        height: 160px;
        overflow-y: hidden;
        border: 1px solid black;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        background-color: white;
      }

      .item-text {
        text-align: center;
        min-height: 75px;
        max-height: 75px;
        overflow: hidden;
        padding: 5px;
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

        i.fa {
          color: #003366;
        }

        &:last-of-type {
          margin-right: 0;
        }

        &.btn-remove {
          position: absolute;
          top: 125px;
          left: 130px;

         i.fa {
          color: #365EBE;
         }
        }
      }
    }
</style>
