<template>
  <div>
    <div class="item-tile" v-if="file.progress !== '0.00'">
      <div class="status-wrap">
        <div>Uploading...<br />{{ file.progress }}%</div>
        <div class="progress">
          <div :style="'width:' + file.progress + '%'"></div>
        </div>
      </div>
    </div>
    <div class="item-tile" v-else>
      <div class="status-wrap">
        <div>Waiting...<br /><br /></div>
        <div class="progress"></div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    props: {
      file: Object,
    },
  };
</script>

<style scoped lang="scss">
  .status-wrap {
    height: 160px;
    border: 1px solid black;
    border-radius: 6px;
    background-color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    font-size: 16px;

    .progress {
      width: calc(100% - 1.5px);
      background-color: #f2f2f3;
      height: 22px;
      position: relative;
      bottom: -54px;
      left: 1px;
      border-top-left-radius: 0;
      border-top-right-radius: 0;

      > div {
        background-color: #365ebe;
        height: 22px;
        border-bottom-left-radius: 4px;
        border-bottom-right-radius: 4px;
      }
    }
  }
</style>
