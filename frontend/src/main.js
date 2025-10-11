import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import './assets/styles/main.css';
import { useUserStore } from './store/user';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

// 在路由导航之前初始化用户状态
const userStore = useUserStore();
userStore.initialize();

app.use(router);
app.use(ElementPlus);

app.mount('#app');
