<template>
  <div class="container">
    <form @submit.prevent="register">
      <h2 class="mb-3">Register</h2>
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
        Already have an account? <button @click="moveToLogin">Login</button>
      </div>

      <button type="submit" id="register_button" class="mt-4 btn-pers">
        Register
      </button>
    </form>
  </div>
</template>

<script>
import { getAuth, createUserWithEmailAndPassword } from "firebase/auth";
import { ref } from 'vue' // used for conditional rendering
import { Notify } from 'quasar';

export default {
  data() {
    return {
      email: "",
      password: "123456",
    };
  },
  methods: {
    register(submitEvent) {
      // data update
      this.email = submitEvent.target.elements.email.value;
      this.password = submitEvent.target.elements.password.value;

      // firebase registration
      const auth = getAuth();
      createUserWithEmailAndPassword(auth, this.email, this.password)
        .then((userCredential) => {
          const user = userCredential.user;
          console.log(user);
          console.log("Registration completed");
          this.$router.push("/");
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
    moveToLogin() {
      this.$router.push("/");
    },
  },
};
</script>
