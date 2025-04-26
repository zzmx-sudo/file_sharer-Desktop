<template>
  <el-menu :collapse="isCollapse" :default-active="$route.path">
    <el-menu-item index="/browse" @click="itemClick('/browse')">
      <i class="el-icon-mobile-phone"></i>
      <span slot="title">文件列表</span>
    </el-menu-item>
    <el-menu-item index="/history" @click="itemClick('/history')">
      <i class="el-icon-time"></i>
      <span slot="title">浏览历史</span>
    </el-menu-item>
    <el-menu-item index="/downloads" @click="itemClick('/downloads')">
      <i class="el-icon-download"></i>
      <span slot="title">下载记录</span>
    </el-menu-item>
    <el-menu-item index="/uploads" @click="itemClick('/uploads')">
      <i class="el-icon-upload2"></i>
      <span slot="title">上传记录</span>
    </el-menu-item>
    <el-menu-item index="/settings" @click="itemClick('/settings')">
      <i class="el-icon-setting"></i>
      <span slot="title">设置</span>
    </el-menu-item>
  </el-menu>
</template>

<script>
  export default {
    name: "MenuBar",
    data() {
      return {
        isCollapse: true
      };
    },
    methods: {
      itemClick(link) {
        this.$router.replace(link);
      }
    }
  }
</script>

<style scoped>

</style>
