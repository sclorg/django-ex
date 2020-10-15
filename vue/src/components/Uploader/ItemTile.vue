<template>
  <div
    :class="['item-tile', file.error ? 'error' : '']"
    v-if="file.progress === '100.00' || file.error"
  >
    <uploaded-image
      :file="file"
      :image-style="imageStyle"
      @imageclick="showPreview"
      @removeclick="$emit('remove')"
    />
    <div class="bottom-wrapper">
      <div class="item-text">
        <div class="filename-text">
          {{ file.name }}
        </div>
        <div class="size-text">
          ({{ Math.round((file.size / 1024 / 1024) * 100) / 100 }} MB)
        </div>
      </div>
      <div
        class="button-wrapper"
        v-if="file.error || file.type !== 'application/pdf'"
      >
        <div v-if="file.success && !isPdf">
          <button
            type="button"
            @click.prevent="$emit('moveup')"
            :disabled="index === 0"
            aria-label="Move down one position"
          >
            <i class="fa fa-chevron-circle-left"></i>
          </button>
          <button
            type="button"
            @click.prevent="$emit('movedown')"
            :disabled="index >= fileCount - 1"
            aria-label="Move up one position"
          >
            <i class="fa fa-chevron-circle-right"></i>
          </button>
          <button
            type="button"
            aria-label="Rotate counter-clockwise"
            @click.prevent="$emit('rotateleft')"
          >
            <i class="fa fa-undo"></i>
          </button>
          <button
            type="button"
            aria-label="Rotate clockwise"
            @click.prevent="$emit('rotateright')"
          >
            <i class="fa fa-undo fa-flip-horizontal"></i>
          </button>
        </div>
        <div class="alert alert-danger" v-if="file.error">
          File Upload Error
        </div>
      </div>
    </div>
  </div>
  <div v-else>
    <progress-bar :file="file" />
  </div>
</template>

<script>
  import UploadedImage from "./Image";
  import ProgressBar from "./ProgressBar";

  export default {
    props: {
      file: Object,
      index: Number,
      fileCount: Number,
    },
    data: function() {
      return {
        showModal: false,
      };
    },
    components: {
      ProgressBar,
      UploadedImage,
    },
    methods: {
      showPreview() {
        this.showModal = true;
      },
      closePreview() {
        this.showModal = false;
      },
    },
    computed: {
      isPdf() {
        return this.file.type === "application/pdf";
      },
    },
  };
</script>

<style lang="scss">
  .item-tile {
    margin-bottom: 5px;
    position: relative;
    border: none !important;

    .item-text {
      text-align: center;
      padding: 7px 10px;
      font-size: 16px;
      line-height: 24px;
      min-height: 87px;

      .filename-text {
        min-height: 25px;
        max-height: 50px;
        overflow: hidden;
        overflow-wrap: anywhere;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }

      .size-text {
        min-height: 25px;
        max-height: 25px;
      }
    }

    .button-wrapper {
      margin-top: -4px;
      text-align: center;
      min-height: 32px;
    }

    .bottom-wrapper {
      border-bottom-left-radius: 6px;
      border-bottom-right-radius: 6px;
      border: 1px solid silver;
      border-top: none;
      background-color: #f2f2f2;
      margin-bottom: 10px;

      .alert-danger {
        background-color: inherit;
        border: none;
        margin-bottom: 0;
        padding: 2px 0 0 0;
        font-weight: 700;
        font-size: 16px;
        line-height: 24px;
      }
    }

    &.error {
      .bottom-wrapper {
        background-color: #f7d4d5;
        border: 1px solid #d8292f;
        border-top: none;
      }
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
        opacity: 0.8;
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

    &.error {
      button.btn-remove i.fa {
        color: #d8292f;
      }
    }
  }
</style>
