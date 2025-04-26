<template>
  <div id="settings">
    {{ msg }}
  </div>
</template>

<script>
export default {
  name: 'Settings',
  data() {
    return {
      msg: '暂未定具体配置项, 待版本更新'
    };
  }
};
</script>

<style scoped>
#settings {
  text-align: center;
  line-height: 200px;
}
</style>
