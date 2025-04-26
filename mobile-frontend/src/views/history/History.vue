<template>
  <div id="history">
    <el-table
      id="history_table"
      :data="browse_history"
      @row-click="row_click">
      <el-table-column
        label="文件/文件夹名">
        <template slot-scope="scope">
          <i v-if="scope.row.is_dir" class="el-icon-folder folder"></i>
          <i v-else class="el-icon-document"></i>
          <span style="margin-left: 10px">{{ scope.row.file_name }}</span>
        </template>
      </el-table-column>
      <el-table-column
        prop="save_date"
        label="上次浏览日期"
        width="120">
      </el-table-column>
      <el-table-column
        label="操作"
        width="80">
        <el-button
          type="danger"
          icon="el-icon-delete"
          size="small">
        </el-button>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { mapMutations } from "vuex";

export default {
  name: 'History',
  data() {
    return {
      browse_history: this.$store.state.browse_history,
    }
  },
  methods: {
    ...mapMutations(["SET_BROWSE_PARAMS", "REMOVE_BROWSE_HISTORY"]),
    row_click(row, column) {
      if (column.label == "操作") {
        this.remove_click(row);
      } else {
        this.history_click(row);
      }
    },
    history_click(row) {
      const { base_url, uuid, secret_key, pwd } = row;
      document.getElementById("baseUrl").innerText = base_url;
      document.getElementById("uuid").innerText = uuid;
      if (secret_key != "" && pwd != "") {
        this.SET_BROWSE_PARAMS({
          "uuid": uuid,
          "secret_key": secret_key,
          "pwd": pwd
        })
      };
      this.$router.replace("/browse");
    },
    remove_click(row) {
      const { uuid } = row;
      this.REMOVE_BROWSE_HISTORY(uuid);
      this.$message({"message": "移除历史成功", type: "success"});
    }
  }
};
</script>

<style scoped>

</style>
