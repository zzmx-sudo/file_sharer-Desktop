<template>
  <div id="download">
    <el-table
      :data="DownloadList"
      style="width: 100%">
      <el-table-column
        label="文件名"
        prop="file_name"
        width="80"
        >
      </el-table-column>
      <el-table-column
        label="下载状态">
        <template slot-scope="scope">
          <trans-progess :transItem="scope.row" :statusList="statusList"></trans-progess>
        </template>
      </el-table-column>
      <el-table-column
        label="操作"
        width="80">
        <template slot-scope="scope">
          <trans-options
            :transItem="scope.row"
            @RefreshClick="refresh_click"
            @PlayClick="play_click"
            @PauseClick="pause_click"
            @RemoveClick="remove_click">
          </trans-options>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { mapMutations } from "vuex";
import TransOptions from '../../components/common/transitem/TransOptions.vue';
import TransProgess from '../../components/common/transitem/TransProgess.vue';

export default {
  components: { TransProgess, TransOptions },
  name: 'Download',
  data() {
    return {
      DownloadList: this.$store.state.download_history,
      statusList: [
        "下载失败, 请删除后重新下载",
        "已暂停",
        "下载中...",
        "合并分片中...",
        "已完成"
      ]
    }
  },
  methods: {
    ...mapMutations(["PAUSE_DOWNLOAD_ITEM", "REMOVE_DOWNLOAD_ITEM"]),
    refresh_click(download_item) {
      this.$store.dispatch("REDOWNLOAD_FILE", download_item.uuid);
      this.$message({"message": "已开始重新下载", type: "success"});
    },
    play_click(download_item) {
      this.$store.dispatch("REDOWNLOAD_FILE", download_item.uuid);
      this.$message({"message": "继续下载成功", type: "success"});
    },
    pause_click(download_item) {
      this.PAUSE_DOWNLOAD_ITEM(download_item.uuid);
      this.$message({"message": "暂停下载成功", type: "success"});
    },
    remove_click(download_item) {
      this.REMOVE_DOWNLOAD_ITEM(download_item.uuid);
      this.$message({"message": "删除下载成功", type: "success"});
    }
  }
};
</script>

<style scoped>

</style>
