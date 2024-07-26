import {ref} from 'vue'
import {defineStore} from 'pinia'

export const useExperimentStore = defineStore(
    'experiment',
    () => {
        const experiment = ref();

        async function fetch_experiment(uuid) {
            await fetch('/api/experiments/' + uuid)
                .then(response => Promise.resolve(response.json()))
                .then(data => experiment.value = data)
        }

        return {experiment, fetch_experiment}
    })
