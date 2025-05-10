<template>
  <div id="upload">
    <el-table
      :data="UploadList"
      style="width: 100%">
      <el-table-column
        label="文件名"
        prop="file_name"
        width="80"
        >
      </el-table-column>
      <el-table-column
        label="上传状态">
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
      <input ref="fileInput" type="file" @change="file_change" style="display: none">
    </el-table>
  </div>
</template>

<script>
import { mapMutations, mapGetters } from "vuex";
import TransOptions from '../../components/common/transitem/TransOptions.vue';
import TransProgess from '../../components/common/transitem/TransProgess.vue';

export default {
  components: { TransProgess, TransOptions },
  name: 'Upload',
  data() {
    return {
      statusList: [
        "已暂停",
        "上传中...",
        "请求合并中...",
        "已完成"
      ],
      fileResolve: null,
    }
  },
  methods: {
    ...mapMutations(["PAUSE_UPLOAD_ITEM", "UPDATE_UPLOAD_ITEM"]),
    refresh_click(upload_item) {
      if ( upload_item.file == null ) {
        this.reselect_file(upload_item);
        return;
      }
      this.$store.dispatch("REUPLOAD_FILE", upload_item.file_id);
      this.$message({"message": "已开始重新上传", type: "success"});
    },
    play_click(upload_item) {
      if ( upload_item.file == null ) {
        this.reselect_file(upload_item);
        return;
      }
      this.$store.dispatch("REUPLOAD_FILE", upload_item.file_id);
      this.$message({"message": "继续上传成功", type: "success"});
    },
    pause_click(upload_item) {
      this.PAUSE_UPLOAD_ITEM(upload_item.file_id);
      this.$message({"message": "暂停上传成功", type: "success"});
    },
    remove_click(upload_item) {
      this.$store.dispatch("REMOVE_UPLOAD_FILE", upload_item.file_id);
      this.$message({"message": "删除上传成功", type: "success"});
    },
    async reselect_file(upload_item) {
      this.$message({"message": "文件对象已丢失, 请重新选择该上传的文件", type: "warning"});
      const file = await new Promise(resolve => {
        this.fileResolve = resolve;
        this.$refs.fileInput.click();
      });
      this.process_file(file, upload_item);
    },
    file_change(event) {
      if ( this.fileResolve ) {
        this.fileResolve(event.target.files[0]);
        this.fileResolve = null;
      }
    },
    process_file(file, upload_item) {
      if ( !file ) {
        this.$message({"message": "未选择文件, 已取消重新上传", type: "warning"});
        return;
      }
      if ( file.name == upload_item.file_name && file.size == upload_item.file_size ) {
        this.UPDATE_UPLOAD_ITEM({file_id: upload_item.file_id, data: {file: file}});
        this.$store.dispatch("REUPLOAD_FILE", upload_item.file_id);
        this.$message({"message": "继续上传成功", type: "success"});
        return;
      }
      this.$message({"message": "非同一文件或文件已更新, 请选择正确文件或删除记录重新上传", type: "warning"});
    }
  },
  computed: {
    ...mapGetters({UploadList: "upload_list"})
  }
};
</script>

<style scoped>

</style>
