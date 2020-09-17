<template>
<div>
  <h5 class="uploader-label">
    {{ formInfo.preText }} 
    <a href="javascript:void(0)" :id="'Tooltip-' + uniqueId">
      {{ formInfo.name }} <i class="fa fa-question-circle"></i>
    </a>
    <strong v-if="party === 1"> - For You</strong>
    <strong v-if="party === 2"> - For Your Spouse</strong>
  </h5>  
  <tooltip :text="formInfo.help" :target="'#Tooltip-' + uniqueId"></tooltip>
  <label :for="inputId" class="sr-only">
    {{ formInfo.preText }} {{ formInfo.name }} 
    <span v-if="party === 1"> - For You</span>
    <span v-if="party === 2"> - For Your Spouse</span>
  </label>
  <div @dragover="draggingOn" @dragenter="draggingOn" @dragleave="draggingOff" @dragend="draggingOff" @drop="draggingOff">
    <file-upload
      ref="upload"
      v-model="files"
      :multiple="true"
      :drop="true"
      :drop-directory="false"
      :post-action="postAction"
      :input-id="inputId"
      name="file"
      :class="['drop-zone', dragging ? 'dragging' : '']"
      :data="data"
      @input-file="inputFile"
      @input-filter="inputFilter">
    <div v-if="files.length === 0" class="placeholder">
      <i class="fa fa-plus-circle"></i><br>
      <em>Drag and Drop the PDF document or JPG pages here,<br>or click here to Browse for files.</em>
    </div>
    <div v-else class="cards">
      <div v-for="(file, index) in files" v-bind:key="index" class="card">
        <item-tile
          :file="file"
          :index="index"
          :file-count="files.length"
          @remove="remove(file)"
          @moveup="moveUp(index)"
          @movedown="moveDown(index)"
          @rotateleft="rotateLeft(index)"
          @rotateright="rotateRight(index)"/>
      </div>
      <div class="card upload-button">
        <div class="upload-button-wrapper">
        <i class="fa fa-plus-circle"></i>
        </div>
      </div>      
    </div>
    </file-upload>
  </div>
</div>
</template>

<script>
import VueUploadComponent from 'vue-upload-component'
import { Tooltip } from 'uiv';
import ItemTile from './ItemTile'
import Forms from "../utils/forms";

export default {
  props: {
    docType: String,
    party: { type: Number, default: 0 }
  },
  data: function () {
    return {
      files: [],
      dragging: false
    }
  },
  components: {
    FileUpload: VueUploadComponent,
    ItemTile,
    Tooltip
  },
  computed: {
    uniqueId() {
      if (this.party === 0) {
        return this.docType;
      }
      return this.docType + this.party;
    },    
    inputId() {
      return "Uploader-" + this.uniqueId;
    },
    formInfo() {
      return Forms[this.docType];
    },
    postAction() {
      return this.$parent.proxyRootPath + "poc/storage"
    },
    data() {
      return {
        docType: this.docType, 
        partyId: this.party
      };
    }
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
        this.$refs.upload.active = true;

      if (newFile) {
        console.log('inputFile newFile=' + newFile.name);
      }

      if (oldFile) {
        console.log('inputFile oldFile=' + oldFile.name);
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

        this.files.forEach(function(f) {
          // prevent duplicates (based on filename and length)
          if (f.name === newFile.name && f.length === newFile.length) {
            return prevent();
          }
        });
      }

      // Add extra data to to the file object
      if (newFile) {
        newFile.objectURL = ''
        let URL = window.URL || window.webkitURL
        if (URL && URL.createObjectURL) {
          newFile.objectURL = URL.createObjectURL(newFile.file)
          newFile.rotation = 0;
          const img = new Image();
          img.onload = function() {
            newFile.width = this.width;
            newFile.height = this.height;
          }
          img.src = newFile.objectURL;
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
    rotateLeft(index) {
      this.files[index].rotation -= 90;
    },
    rotateRight(index) {
      this.files[index].rotation += 90;
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
    background-color: white;
    width: 100%;
    display: block;
    text-align: left;
    border: 2px #365EBE dashed;
    border-radius: 6px;
    padding: 18px;

    &.dragging {
      background-color: #F2E3F2;
    }

    .cards {
      display: flex;
      flex-wrap: wrap;
      justify-content: left;
    }

    .card {
      flex: 0 1 160px;
      margin-bottom: 10px;
      width: 160px;
      margin-right: 18px;

      &.upload-button {
        display: flex;
        flex-direction: column;
        justify-content: center;
      }
    }

    .fa-plus-circle {
      font-size: 3rem;
      margin-bottom: 8px;
      color: #365EBE;

      &:hover {
        cursor: pointer;
      }
    }

    .placeholder {
      text-align: center;
    }
  }

  h5.uploader-label {
    display: block;   
    margin-top: 30px;
    margin-bottom: 10px;
    font-weight: normal;
    font-size: 1em;

    a {
      font-weight: bold;
      text-decoration: underline;
    }
  }
</style>
