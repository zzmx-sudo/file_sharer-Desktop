// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import 'element-ui/lib/theme-chalk/index.css';
import App from './App'
import router from './router'
import store from './store'
import '@/assets/css/base.css'
import {
  Menu,
  MenuItem,
  Container,
  Header,
  Aside,
  Main,
  Button,
  ButtonGroup,
  Table,
  TableColumn,
  Alert,
  Icon,
  Progress,
  MessageBox,
  Message,
  Loading
} from 'element-ui';

Vue.config.productionTip = false
Vue.use(Menu);
Vue.use(MenuItem);
Vue.use(Container);
Vue.use(Header);
Vue.use(Aside);
Vue.use(Main);
Vue.use(Button);
Vue.use(ButtonGroup);
Vue.use(Table);
Vue.use(TableColumn);
Vue.use(Alert);
Vue.use(Icon);
Vue.use(Progress);
Vue.use(MessageBox);
Vue.use(Message);
Vue.use(Loading);
Vue.prototype.$alert = MessageBox.alert;
Vue.prototype.$prompt = MessageBox.prompt;
Vue.prototype.$confirm = MessageBox.confirm;
Vue.prototype.$message = Message;

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
})
