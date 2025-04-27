<template>
  <div id="app">
    <div>
      <el-container v-if="!show_msg_box">
        <el-header height="40px">File-Sharer</el-header>
			  <el-container>
			    <el-aside width="65px">
            <menu-bar />
          </el-aside>
			    <el-main>
            <router-view />
          </el-main>
			  </el-container>
			</el-container>
    </div>
  </div>
</template>

<script>
import MenuBar from './components/content/menubar/MenuBar.vue';
import { mapMutations } from "vuex";

export default {
  name: 'App',
  components: {
    MenuBar
  },
  data() {
    return {
      show_backup: true,
      show_msg_box: true
    }
  },
  created() {
    // 将所有未完成下载置为暂停
    this.PAUSE_ALL_DOWNLOAD_HISTORY();
    // 将所有未完成上传置为暂停
    this.PAUSE_ALL_UPLOAD_HISTORY();
    document.title = "File-Sharer";
    this.$alert('请勿在任何情况下刷新页面,否则上传/下载会暂停(下载进度也会消失),且需重新扫码!!!', '温馨提示', {
      showClose: false,
      center: true,
      confirmButtonText: '确定并进入',
      callback: action => {
        this.show_msg_box = false;
        this.$router.replace('/browse');
      }
    });
  },
  methods: {
    ...mapMutations(["PAUSE_ALL_DOWNLOAD_HISTORY", "PAUSE_ALL_UPLOAD_HISTORY"]),
  }
}
</script>

<style>
/* 修复手机浏览器上MessageBox显示不全和位置靠顶的问题 */
@media screen and (max-width: 750px) {
  .el-message-box {
    width: 80% !important;
  }
}

.el-container{
  height: 100%;
}

html,body,#app{
  margin: 0;
  padding: 0;
  height: 100%;
}

.el-header {
  background-color: #81C7FF;
  color: #fff;
  text-align: center;
  line-height: 40px;
}

.el-aside {
  color: #333;
}
</style>
