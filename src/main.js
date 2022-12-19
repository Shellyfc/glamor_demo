import { createApp } from 'vue'
import App from './App.vue'
import { Quasar, Loading, Notify } from 'quasar'
import quasarUserOptions from './quasar-user-options'
import router from './router'

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
// import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyADSf8yj-AFdKYMceIOYc5vMvGrfmwr-ck",
  authDomain: "glamor-f4e46.firebaseapp.com",
  projectId: "glamor-f4e46",
  storageBucket: "glamor-f4e46.appspot.com",
  messagingSenderId: "816329817401",
  appId: "1:816329817401:web:6fc20be53d0225f020bce8",
  measurementId: "G-VBT7RQCSDE"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app);
export default app;
export const auth = getAuth(app);

createApp(App).use(router).use(Quasar, {
  plugins: {
    Loading,
    Notify
  },
  config: {
    loading: { /* look at QuasarConfOptions from the API card */ },
    notify: { /* look at QuasarConfOptions from the API card */ }
  }
}).use(Quasar, quasarUserOptions).mount('#app')



