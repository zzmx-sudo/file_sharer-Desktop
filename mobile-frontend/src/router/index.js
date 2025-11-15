import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* 解决双击切换路由报错 */
// 解决双击时路由通过push报错
const originalPush = Router.prototype.push
Router.prototype.push = function (location) {
  return originalPush.call(this, location).catch(err => { err })
}
// 解决双击时路由通过replace报错
const originalReplace = Router.prototype.replace
Router.prototype.replace = function (location) {
  return originalReplace.call(this, location).catch(err => { err })
}

export default new Router({
  routes: [
    // {
    //   path: '/',
    //   redirect: '/browse'
    // },
    {
      path: '/browse',
      name: 'Browse',
      component: () => import('@/views/browse/Browse')
    },
    {
      path: '/history',
      name: 'History',
      component: () => import('@/views/history/History')
    },
    {
      path: '/downloads',
      name: 'Downloads',
      component: () => import('@/views/downloads/Downloads')
    },
    {
      path: '/uploads',
      name: 'Uploads',
      component: () => import('@/views/uploads/Uploads')
    },
    {
      path: '/settings',
      name: "Settings",
      component: () => import('@/views/settings/Settings')
    }
  ],
  mode: 'history'
})
