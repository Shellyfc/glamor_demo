<template>
  <div class="q-pa-md">

    <q-form @submit="onSubmit" @reset="onReset" class="q-gutter-md">
      <div class="q-gutter-md row items-start flex flex-center">
        <q-input filled v-model="formA" label="Your choice of A" hint="A" lazy-rules
          :rules="[val => val && val.length > 0 || 'Please type something']" />

        <q-input filled v-model="formB" label="Your choice of B" hint="B" lazy-rules
          :rules="[val => val && val.length > 0 || 'Please type something']" />

        <q-input filled v-model="formC" label="Your choice of C" hint="C" lazy-rules
          :rules="[val => val && val.length > 0 || 'Please type something']" />

        <q-input filled v-model="formD" label="Your choice of D" hint="D" lazy-rules
          :rules="[val => val && val.length > 0 || 'Please type something']" />
      </div>
      <div>
        <q-btn label="Submit" type="submit" color="primary" />
        <q-btn label="Reset" type="reset" color="primary" flat class="q-ml-sm" />
      </div>

    </q-form>

  </div>

  <div class="q-pa-md flex flex-center" v-if="bIsLoading">
    <q-circular-progress
      indeterminate
      rounded
      size="50px"
      color="light-blue"
      class="q-ma-md"
    />
  </div>

  <div class="q-pa-md" v-if="rowsB">
    <q-table title="Model Predictions for B" :rows="rowsB" :columns="columnsB" row-key="name" />
  </div>
  <div class="q-pa-md" v-if="rowsD">
    <q-table title="Model Predictions for D" :rows="rowsD" :columns="columnsD" row-key="name" />
  </div>


  <div v-if="(bAskingQuestions && examples)">
    <div class="q-pa-md">
      {{examples[exampleIndex]["A"]}} is to {{examples[exampleIndex]["B"]}} as {{examples[exampleIndex]["C"]}} is to _______.
    <div class="q-pa-md flex flex-center">
    <q-input style="max-width: 150px" v-model="answer" label="Your answer" />
    </div>
    <div class="q-pa-md q-gutter-sm">
        <q-btn label="Submit" @click="submitAnswer()" color="primary" />
        <q-btn label="Next" @click="nextExample()" color="primary"/>
      </div>
  </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useQuasar } from 'quasar'
import { getAuth } from "firebase/auth";

export default {
  setup() {
    const answer = ref(null)

    const examples = ref(null)

    const formA = ref(null)
    const formB = ref(null)
    const formC = ref(null)
    const formD = ref(null)
    const columnsB = [
      {
        name: 'model',
        required: true,
        label: 'model',
        align: 'left',
        field: 'model',
        sortable: true
      },
      { name: 'topB', align: 'center', label: 'topB', field: 'topD', sortable: true },
      { name: 'topBScore', label: 'topBScore', field: 'topDScore', sortable: true },
      { name: 'topBRank', label: 'topBRank', field: 'topDRank', sortable: true },
      { name: 'topBSentence', label: 'topBSentence', field: 'topDSentence' },
      { name: 'trueB', label: 'trueB', field: 'trueD' },
      { name: 'trueBScore', label: 'trueBScore', field: 'trueDScore', sortable: true },
      { name: 'trueBRank', label: 'trueBRank', field: 'trueDRank', sortable: true },
      { name: 'trueBSentence', label: 'trueBSentence', field: 'trueDSentence' }
    ]
    const columnsD = [
      {
        name: 'model',
        required: true,
        label: 'model',
        align: 'left',
        field: 'model',
        sortable: true
      },
      { name: 'topD', align: 'center', label: 'topD', field: 'topD', sortable: true },
      { name: 'topDScore', label: 'topDScore', field: 'topDScore', sortable: true },
      { name: 'topDRank', label: 'topDRank', field: 'topDRank', sortable: true },
      { name: 'topDSentence', label: 'topDSentence', field: 'topDSentence' },
      { name: 'trueD', label: 'trueD', field: 'trueD' },
      { name: 'trueDScore', label: 'trueDScore', field: 'trueDScore', sortable: true },
      { name: 'trueDRank', label: 'trueDRank', field: 'trueDRank', sortable: true },
      { name: 'trueDSentence', label: 'trueDSentence', field: 'trueDSentence' }
    ]
    const rowsB = ref(null)
    const rowsD = ref(null)
    const bIsLoading = ref(false)
    const bAskingQuestions = ref(true)

    const $q = useQuasar()

    const email = ref(null)
    getAuth().onAuthStateChanged(function (user) {
      if (user) {
        email.value = user.email
      } else {
        email.value = ""
      }
    })

    const exampleIndex = ref(0)

    function queryExamples() {
        let axiosConfig = {
          headers: {
            'Content-Type': 'application/json;charset=UTF-8',
            "Access-Control-Allow-Origin": "http://localhost:8080",
          }
        };
        axios.post("http://127.0.0.1:8888/examples", {
          num: 10
        }, axiosConfig)
          .then(function (response) {
            console.log(response);
            examples.value = response.data
          })
          .catch(function (error) {
            console.log(error);
          });
      }

    onMounted(()=>{
      queryExamples()
    })

    return {
      formA,
      formB,
      formC,
      formD,
      columnsB,
      rowsB,
      columnsD,
      rowsD,
      $q,
      email,
      bIsLoading,
      bAskingQuestions,
      examples,
      exampleIndex,
      queryExamples,
      answer,

      onSubmit() {
        // $q.loading.show({
        //   spinner: QSpinnerInfinity,
        //   message: 'Fetching data. Hang on...',
        // });
        rowsB.value = null;
        rowsD.value = null;
        bIsLoading.value = true;
        bAskingQuestions.value = true;
        let axiosConfig = {
          headers: {
            'Content-Type': 'application/json;charset=UTF-8',
            "Access-Control-Allow-Origin": "*",
          }
        };
        axios.post("http://127.0.0.1:8888/search2", {
          email: email.value,
          formA: formA.value,
          formB: formB.value,
          formC: formC.value,
          formD: formD.value,
        }, axiosConfig)
          .then(function (response) {
            // $q.loading.hide()
            bIsLoading.value = false
            console.log(response);
            rowsB.value = response.data["B"]
            rowsD.value = response.data["D"]
          })
          .catch(function (error) {
            console.log(error);
            $q.loading.hide()
          });
      },

      onReset() {
        formA.value = null
        formB.value = null
        formC.value = null
        formD.value = null
        bIsLoading.value = false
        bAskingQuestions.value = false
      },

      submitAnswer() {
        let axiosConfig = {
          headers: {
            'Content-Type': 'application/json;charset=UTF-8',
            "Access-Control-Allow-Origin": "http://localhost:8080",
          }
        };
      axios.post("http://127.0.0.1:8888/answer", {
          formA: examples.value[exampleIndex.value]["A"],
          formB: examples.value[exampleIndex.value]["B"],
          formC: examples.value[exampleIndex.value]["C"],
          answer: answer.value
        }, axiosConfig)
          .then(function (response) {
            console.log(response);
          })
          .catch(function (error) {
            console.log(error);
          });
      },

      nextExample() {
        if (exampleIndex.value < examples.value.size)
        {
          exampleIndex.value += 1;
          answer.value = null
        } else 
        {
          this.queryExamples();
        }
      }
    }
  }
}
</script>