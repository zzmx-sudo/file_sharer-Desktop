<template>
  <div id="browse">
    <div class="button-list">
      <el-button
        class="backup-bt"
        type="primary"
        icon="el-icon-back"
        :disabled="!has_backup"
        @click="backup_click">
      </el-button>
      <el-button
        type="primary"
        :disabled="!can_upload"
        @click="upload_click">
        在此处上传文件
      </el-button>
      <input ref="fileInput" type="file" @change="file_change" style="display: none">
    </div>
    <el-table
      id="file_table"
      v-loading="loading"
      :data="fileList"
      @row-click="file_click"
      style="width: 100%">
      <el-table-column
        label="文件/文件夹名">
        <template slot-scope="scope">
          <i v-if="scope.row.isDir" class="el-icon-folder folder"></i>
          <i v-else class="el-icon-document"></i>
          <span style="margin-left: 10px">{{ scope.row.fileName }}</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import request from "@/network/request";
import { encrypt } from '@/utils/credentials';
import { GetListMobile, PostListMobile } from "@/network/browse";
import { GetFileSize } from "@/network/download";
import { mapMutations } from "vuex";

export default {
  name: 'Browse',
  data() {
    return {
      loading: false,
      has_backup: false,
      can_upload: false,
      fileList: [],
      backup_list: [],
      base_url: "",
      uuid: "",
      secret_key: "",
      curr_dir: "",
      chunk_size: 10485760,
    }
  },
  mounted() {
    this.loading = true;
    // 获取baseURL
    this.base_url = document.getElementById('baseUrl').innerText;
    // 获取uuid并正式请求文件列表
    this.uuid = document.getElementById('uuid').innerText;
    request.defaults.baseURL = this.base_url;
    this.get_list_mobile();
  },
  methods: {
    ...mapMutations(["SET_BROWSE_PARAMS", "UPDATE_BROWSE_HISTORY", "UPDATE_DOWNLOAD_HISTORY", "UPDATE_UPLOAD_HISTORY", "UPDATE_UPLOAD_ITEM"]),
    get_list_mobile() {
      GetListMobile(this.uuid).then(res => {
        if ( !("errno" in res) ) {
          this.loading = false;
          this.$message.error("访问文件列表错误, " + res + ", 请重新扫描！");
          return;
        }
        if (res.errno == 200) {
          this.UPDATE_BROWSE_HISTORY({
            "base_url": this.base_url,
            "uuid": this.uuid,
            "secret_key": "",
            "pwd": "",
            "file_name": res.data.fileName,
            "is_dir": res.data.isDir,
            "save_date": this.currentTime,
          });
          this.fileList = [res.data];
          this.curr_dir = res.data.targetPath;
          if (!res.data.isDir) {
            this.can_upload = true;
          }
          this.loading = false;
        } else if (res.errno == 4003) {
          var secret_key = res.secret_key;
          const browse_params = this.$store.state.browse_params;
          if (browse_params != null && browse_params.uuid == this.uuid
              && browse_params.secret_key == secret_key) {
            return this.post_list_mobile(secret_key, browse_params.pwd);
          }
          this.$prompt("请输入浏览密码", "提示", {
            confirmButtonText: "确定",
            showClose: false,
            showCancelButton: false,
            closeOnClickModal: false,
            closeOnPressEscape: false
          }).then(({ value }) => {
            value = encrypt(value, secret_key);
            this.post_list_mobile(secret_key, value);
          })
        } else if (res.errno == 400) {
          this.loading = false;
          this.$alert("访问受限, 请合法访问文件列表", "For Bidden!", {
            showClose: false,
            center: true,
            confirmButtonText: '确定'
          });
        } else {
          this.loading = false;
          var errmsg = "errmsg" in res ? res.errmsg : res;
          this.$alert(errmsg + ", 请重新扫描", "访问文件列表异常", {
            showClose: false,
            center: true,
            confirmButtonText: '确定'
          });
        }
      }).catch(err => {
        this.loading = false;
        this.$message.error("访问文件列表错误, " + err + ", 请重新扫描！")
      })
    },
    post_list_mobile(secret_key, pwd) {
      this.secret_key = secret_key;
      PostListMobile(this.uuid, secret_key, pwd).then(res => {
        if ( !("errno" in res) ) {
          this.loading = false;
          this.$message.error("访问文件列表错误, " + res + ", 请重新扫描！");
          return;
        }
        if (res.errno == 200) {
          this.$message({
            message: "密码正确, 正在加载文件列表...",
            type: "success"
          });
          this.SET_BROWSE_PARAMS({
            "uuid": this.uuid,
            "secret_key": this.secret_key,
            "pwd": pwd
          });
          this.UPDATE_BROWSE_HISTORY({
            "base_url": this.base_url,
            "uuid": this.uuid,
            "secret_key": this.secret_key,
            "pwd": pwd,
            "file_name": res.data.fileName,
            "is_dir": res.data.isDir,
            "save_date": this.currentTime,
          });
          this.fileList = [res.data];
          this.curr_dir = res.data.targetPath;
          if (!res.data.isDir) {
            this.can_upload = true;
          }
          this.loading = false;
        } else if (res.errno == 4003) {
          this.$message.error('密码错误, 请重新输入密码');
          var secret_key = res.secret_key;
          this.$prompt("请输入浏览密码", "提示", {
            confirmButtonText: "确定",
            inputErrorMessage: "密码不正确",
            showClose: false,
            showCancelButton: false,
            closeOnClickModal: false,
            closeOnPressEscape: false
          }).then(({ value }) => {
            value = encrypt(value, secret_key);
            this.post_list_mobile(secret_key, value);
          });
        } else if (res.errno == 400) {
          this.loading = false;
          this.$alert("访问受限, 请合法访问文件列表", "For Bidden!", {
            showClose: false,
            center: true,
            confirmButtonText: '确定'
          });
        } else {
          this.loading = false;
          var errmsg = "errmsg" in res ? res.errmsg : res;
          this.$alert(errmsg + ", 请重新扫描！", "访问文件列表异常", {
            showClose: false,
            center: true,
            confirmButtonText: '确定'
          });
        }
      }).catch(err => {
        this.loading = false;
        this.$message.error("访问文件列表错误, " + err + ", 请重新扫描！")
      })
    },
    file_click(row) {
      if (row.isDir) {
        this.backup_list.push(this.fileList);
        this.fileList = row.children;
        this.curr_dir = row.targetPath;
        this.has_backup = true;
        this.can_upload = true;
      } else {
        this.$confirm('正在请求下载文件: ' + row.fileName + ", 是否确定下载?", '是否下载文件', {
          confirmButtonText: '确定',
          cancelButtonText: '点错了',
          type: 'info'
        }).then(() => {
          GetFileSize(row.uuid).then(res => {
            if ( res.errno == 200 ) {
              var file_size = res.fileSize;
              this.start_download(row, file_size);
            } else {
              if ( res.errno == 404 ) {
                this.$message({message: "该文件已被删除, 加入下载失败", type: "error"});
              } else {
                this.$message({message: "获取文件大小错误(" + res.err_msg + "), 加入下载失败", type: "error"});
              }
            }
          });
        });
      }
    },
    upload_click() {
      this.$refs.fileInput.click()
    },
    file_change(event) {
      const files = event.target.files
      if (!files || files.length === 0) {
        return;
      }
      const selectedFile = files[0];
      this.start_upload(selectedFile);
    },
    backup_click() {
      if (this.backup_list.length == 0) {
        return;
      }
      this.fileList = this.backup_list.pop();
      this.curr_dir = this.fileList[0].targetPath.split('/').slice(0, -1).join('/');
      this.has_backup = this.backup_list.length > 0;
      this.can_upload = this.backup_list.length > 0;
    },
    start_download(row, file_size) {
      var browse_params = this.$store.state.browse_params;
      var download_history = this.$store.state.download_history;
      if ( download_history != null ) {
        var download_item = download_history[row.uuid];
        if ( download_item != undefined ) {
          if ( download_item.is_pause ) {
            this.$store.dispatch("REDOWNLOAD_FILE", download_item.uuid);
            this.$message({message: "该文件在历史下载中, 已继续对该文件下载", type: "success"})
          } else {
            this.$message({message: "该文件已在历史下载中且未暂停, 请勿重复下载", type: "warning"})
          };
          return;
        }
      };
      this.UPDATE_DOWNLOAD_HISTORY({
        uuid: row.uuid,
        file_name: row.fileName,
        file_size: file_size,
        is_pause: false,
        chunk_size: this.chunk_size,
        succed_chunks: [],
        chunk_count: Math.ceil(file_size / this.chunk_size),
        merged: false,
        secret_key: browse_params != null ? browse_params.secret_key : "",
        pwd: browse_params != null ? browse_params.pwd : "",
        failed: false,
        err_msg: "",
      });
      this.$store.dispatch("START_DOWNLOAD_FILE", row.uuid);
      this.$message({message: "加入下载成功", type: "success"});
    },
    start_upload(selectedFile) {
      const file_id = Date.now().toString();
      var browse_params = this.$store.state.browse_params;
      var upload_history = this.$store.state.upload_history;
      if ( upload_history != null ) {
        var upload_item = null;
        Object.values(upload_history).forEach(obj => {
          if ( obj.uuid == this.uuid && obj.curr_dir == this.curr_dir && obj.file_name == selectedFile.name ) {
            upload_item = obj;
          }
        })
        if ( upload_item != null ) {
          if ( upload_item.is_pause ) {
            if ( upload_item.file == null ) {
              this.UPDATE_UPLOAD_ITEM({file_id: upload_item.file_id, data: {file: selectedFile}});
            }
            this.$store.dispatch("REUPLOAD_FILE", upload_item.file_id);
            this.$message({message: "该文件在历史上传中, 已继续对该文件上传", type: "success"});
          } else {
            this.$message({message: "该文件已在历史上传中且未暂停, 请勿重复下载", type: "warning"})
          }
          return;
        }
      };
      this.UPDATE_UPLOAD_HISTORY({
        file_id: file_id,
        uuid: this.uuid,
        file: selectedFile,
        file_name: selectedFile.name,
        file_size: selectedFile.size,
        type: selectedFile.type,
        curr_path: this.curr_dir,
        is_pause: false,
        chunk_size: this.chunk_size,
        succed_chunks: [],
        chunk_count: Math.ceil(selectedFile.size / this.chunk_size),
        merged: false,
        secret_key: browse_params != null ? browse_params.secret_key : "",
        pwd: browse_params != null ? browse_params.pwd : "",
        failed: false,
        err_msg: ""
      });
      this.$store.dispatch("START_UPLOAD_FILE", file_id);
      this.$message({message: "加入下载成功", type: "success"});
    }
  },
  computed: {
    currentTime() {
      return new Date().toLocaleString();
    }
  }
};
</script>

<style scoped>
.backup-bt {
  margin-right: 40px;
  margin-bottom: 20px;
}

.folder {
  color: #409eff;
}
</style>
