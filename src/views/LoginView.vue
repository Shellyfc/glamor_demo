<template>
  <div class="container">
    <form @submit.prevent="login">
      <h2 class="mb-3">Login</h2>
      <div class="input">
        <label for="email">Email address</label>
        <input
          class="form-control"
          type="text"
          name="email"
          placeholder="email@adress.com"
        />
      </div>
      <div class="input">
        <label for="password">Password</label>
        <input
          class="form-control"
          type="password"
          name="password"
          placeholder="password123"
        />
      </div>
      <div class="alternative-option mt-4">
        You don't have an account?
        <button @click="moveToRegister">
          Register
      </button>
      </div>
      <button type="submit" class="mt-4 btn-pers" id="login_button">
        Login
      </button>
    </form>
  </div>
</template>

<script>
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { Notify } from 'quasar';
import { ref } from 'vue' // used for conditional rendering

export default {
  data() {
    return {
      email: "",
      password: "",
      errorCode: ""
    };
  },
  methods: {
    login(submitEvent) {
      this.email = submitEvent.target.elements.email.value;
      this.password = submitEvent.target.elements.password.value;

      const auth = getAuth();
      signInWithEmailAndPassword(auth, this.email, this.password)
        .then(() => {
          this.$router.push("/tableView");
        })
        .catch((error) => {
          this.errorCode = error.code;
          const errMsg = ref(null)
          switch (error.code) {
          case 'auth/invalid-email':
              errMsg.value = 'Invalid email'
              break
          case 'auth/user-not-found':
              errMsg.value = 'No account with that email was found'
              break
          case 'auth/wrong-password':
              errMsg.value = 'Incorrect password'
              break
          default:
              errMsg.value = 'Email or password was incorrect'
              break
        }
          // const errorMessage = error.message;
          // console.log(errorCode);
          // console.log(errorMessage);
          // let alert_1 = document.querySelector("#alert_1");
          // alert_1.classList.remove("d-none");
          // alert_1.innerHTML = errorMessage;
          // console.log(alert_1);
          Notify.create(errMsg.value)
        });
    },
    moveToRegister() {
      this.$router.push("/register");
    },
  },
};
</script>
