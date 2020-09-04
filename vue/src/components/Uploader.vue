<template>
<div>
  <div @dragover="draggingOn" @dragenter="draggingOn" @dragleave="draggingOff" @dragend="draggingOff" @drop="draggingOff">
    <file-upload
      ref="upload"
      v-model="files"
      :multiple="true"
      :drop="true"
      :drop-directory="false"
      post-action="/post.method"
      put-action="/put.method"
      @input-file="inputFile"
      @input-filter="inputFilter"
      :class="['drop-zone', dragging ? 'dragging' : '']"
    >
    <div v-if="files.length === 0" class="placeholder">
    <i class="fa fa-plus-circle"></i><br>
    <em>Drag and Drop the PDF document or JPG pages here,<br>or click here to Browse for files.</em>
    </div>
    <div v-else class="items">
  <div v-for="(file, index) in files" v-bind:key="index" class="item">
    <item-tile 
      :file="file" 
      :index="index" 
      :file-count="files.length"
      @remove="remove(file)"
      @moveup="moveUp(index)"
      @movedown="moveDown(index)"/>
  </div>    
  </div>
    </file-upload>
  </div>
</div>
</template>

<script>
import VueUploadComponent from 'vue-upload-component'
import ItemTile from './ItemTile'

export default {
  data: function () {
    return {
      files: [],
      dragging: false
    }
  },
  components: {
    FileUpload: VueUploadComponent,
    ItemTile
  },
  methods: {
    /**
     * Has changed
     * @param  Object|undefined   newFile   Read only
     * @param  Object|undefined   oldFile   Read only
     * @return undefined
     */
    inputFile(newFile, oldFile) {
      if (newFile && oldFile && !newFile.active && oldFile.active) {
        // Get response data
        console.log('response', newFile.response)
        if (newFile.xhr) {
          //  Get the response status code
          console.log('status', newFile.xhr.status)
        }
      }
    },
    /**
     * Pretreatment
     * @param  Object|undefined   newFile   Read and write
     * @param  Object|undefined   oldFile   Read only
     * @param  Function           prevent   Prevent changing
     * @return undefined
     */
    inputFilter(newFile, oldFile, prevent) {
      if (newFile && !oldFile) {
        // Filter non-image file
        if (!/\.(jpeg|jpg|png|pdf)$/i.test(newFile.name)) {
          return prevent()
        }
      }

      // Create a blob field
      if (newFile) {
        newFile.blob = ''
        let URL = window.URL || window.webkitURL
        if (URL && URL.createObjectURL) {
          newFile.blob = URL.createObjectURL(newFile.file)
        }
      }
    },
    remove(file) {
      this.$refs.upload.remove(file)
    },
    moveUp(old_index) {
      if (old_index >= 1 && this.files.length > 1) {
        this.files.splice(old_index - 1, 0, this.files.splice(old_index, 1)[0]);
      }
    },
    moveDown(old_index) {
      if (old_index <= this.files.length && this.files.length > 1) {
        this.files.splice(old_index + 1, 0, this.files.splice(old_index, 1)[0]);
      }
    },
    draggingOn() {
      this.dragging = true;
    },
    draggingOff() {
      this.dragging = false;
    }    
  }
}
</script>

<style scoped lang="scss">
  .drop-zone {
    width: 100%;
    display: block;
    text-align: left;
    border: 2px #365EBE dashed;
    border-radius: 6px;
    padding: 18px;

    &.dragging {
      background-color: #F2F2F2;
    }

    .item {
      margin-bottom: 10px;
      width: 160px;
      display: inline-block;
      margin-right: 20px;
    }

    .fa-plus-circle {
      font-size: 2rem;
      margin-bottom: 8px;
      color: #365EBE;
    }

    .placeholder {
      text-align: center;
    }
  }
</style>
