<template>
  <div class="trans_options">
    <el-button-group>
      <el-button
        v-if="failed"
        type="primary"
        icon="el-icon-refresh"
        size="small"
        @click="RefreshClick"
        :disabled="progess == 100">
      </el-button>
      <el-button
        v-else-if="is_pause"
        type="primary"
        icon="el-icon-video-play"
        size="small"
        @click="PlayClick"
        :disabled="progess == 100">
      </el-button>
      <el-button
        v-else
        type="primary"
        icon="el-icon-video-pause"
        size="small"
        @click="PauseClick"
        :disabled="progess == 100">
      </el-button>
      <el-button
        type="danger"
        icon="el-icon-delete"
        size="small"
        @click="RemoveClick"
        :disabled="!can_remove">
      </el-button>
    </el-button-group>
  </div>
</template>

<script>

export default {
  name: 'TransOptions',
  props: {
    transItem: {
      type: Object,
      require: true,
      default: {}
    }
  },
  computed: {
    failed() {
      return this.transItem.failed;
    },
    is_pause() {
      return this.transItem.is_pause;
    },
    is_downloading() {
      return !this.transItem.is_pause;
    },
    can_remove() {
      return this.transItem.failed || this.transItem.is_pause || this.transItem.merged;
    },
    progess() {
      return (this.transItem.succed_chunks.length / this.transItem.chunk_count) * 100
    }
  },
  methods: {
    RefreshClick() {
      this.$emit("RefreshClick", this.transItem)
    },
    PlayClick() {
      this.$emit("PlayClick", this.transItem);
    },
    PauseClick() {
      this.$emit("PauseClick", this.transItem);
    },
    RemoveClick() {
      this.$emit("RemoveClick", this.transItem)
    }
  }
};
</script>

<style scoped>
</style>
