<template>
  <div class="q-pa-md">

    <q-form @submit="onSubmit" @reset="onReset" class="q-gutter-md">
      <div class="q-gutter-md row items-start">
        <q-input filled v-model="formA" label="Your choice of A" hint="A" lazy-rules
          :rules="[ val => val && val.length > 0 || 'Please type something']" />

        <q-input filled v-model="formB" label="Your choice of B" hint="B" lazy-rules
          :rules="[ val => val && val.length > 0 || 'Please type something']" />

        <q-input filled v-model="formC" label="Your choice of C" hint="C" lazy-rules
          :rules="[ val => val && val.length > 0 || 'Please type something']" />

        <q-input filled v-model="formD" label="Your choice of D" hint="D" lazy-rules
          :rules="[ val => val && val.length > 0 || 'Please type something']" />
      </div>
      <div>
        <q-btn label="Submit" type="submit" color="primary" />
        <q-btn label="Reset" type="reset" color="primary" flat class="q-ml-sm" />
      </div>

    </q-form>

  </div>
  <div class="q-pa-md"  v-if="rowsB">
    <q-table title="Model Predictions for B" :rows="rowsB" :columns="columnsB" row-key="name" />
  </div>
  <div class="q-pa-md"  v-if="rowsD">
    <q-table title="Model Predictions for D" :rows="rowsD" :columns="columnsD" row-key="name" />
  </div>
</template>

<script>
import { ref, onBeforeUnmount } from 'vue'
import axios from 'axios'
// import { QSpinnerInfinity } from 'quasar'

export default {
  setup() {
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
      { name: 'trueBScore', label: 'trueBScore', field: 'trueDScore', sortable: true},
      { name: 'trueBRank', label: 'trueBRank', field: 'trueDRank', sortable: true},
      { name: 'trueBSentence', label: 'trueBSentence', field: 'trueDSentence'}
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
      { name: 'trueDScore', label: 'trueDScore', field: 'trueDScore', sortable: true},
      { name: 'trueDRank', label: 'trueDRank', field: 'trueDRank', sortable: true},
      { name: 'trueDSentence', label: 'trueDSentence', field: 'trueDSentence'}
    ]
    const rowsB = ref(null)
    const rowsD = ref(null)

    // const $q = useQuasar()
    let timer

    onBeforeUnmount(() => {
      if (timer !== void 0) {
        clearTimeout(timer)
        // $q.loading.hide()
      }
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

      onSubmit() {
        // this.$q.loading.show({
        //   spinner: QSpinnerInfinity,
        //   message: 'Fetching data. Hang on...',
        // });
        rowsB.value = null;
        rowsD.value = null;
        let axiosConfig = {
          headers: {
            'Content-Type': 'application/json;charset=UTF-8',
            "Access-Control-Allow-Origin": "*",
          }
        };
        axios.post("http://127.0.0.1:8888/search2", {
          formA: formA.value,
          formB: formB.value,
          formC: formC.value,
          formD: formD.value,
        }, axiosConfig)
          .then(function (response) {
            // $q.loading.hide()
            console.log(response);
            rowsB.value = response.data["B"]
            rowsD.value = response.data["D"]
          })
          .catch(function (error) {
            console.log(error);
          });


        // timer = setTimeout(() => {
        //   $q.loading.hide()
        //   timer = void 0
        // }, 3000);
      },

      onReset() {
        formA.value = null
        formB.value = null
        formC.value = null
        formD.value = null
      }
    }
  }
}
</script>