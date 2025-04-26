<template>
  <div>
    <span>{{ TransStatus }}</span>
    <el-progress v-if="!transItem.failed" :percentage="progess"></el-progress>
    <el-progress v-else status="exception" :percentage="progess"></el-progress>
  </div>
</template>

<script>

export default {
  name: 'TransProgess',
  props: {
    transItem: {
      type: Object,
      require: true,
      default: {}
    },
    statusList: {
      type: Array,
      require: true,
      default: [
        "下载失败",
        "已暂停",
        "下载中...",
        "合并分片中...",
        "已完成"
      ]
    }
  },
  computed: {
    TransStatus() {
      if ( this.transItem.failed ) {
        return this.statusList[0]
      } else if ( this.transItem.is_pause ) {
        return this.statusList[1]
      } else if ( this.transItem.succed_chunks.length != this.transItem.chunk_count ) {
        return this.statusList[2]
      } else if ( !this.transItem.merged ) {
        return this.statusList[3]
      } else {
        return this.statusList[4]
      }
    },
    progess() {
      return Math.floor((this.transItem.succed_chunks.length / this.transItem.chunk_count) * 100)
    }
  }
};
</script>

<style scoped>

</style>
