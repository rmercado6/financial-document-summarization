import {ref, computed} from 'vue'
import {defineStore} from 'pinia'

export const useFetchExperimentListStore = defineStore(
    'experiments',
    () => {
        const experiment_list = ref([]);

        const experiments = computed(() => {
            if (experiment_list.value.length === 0) {
                fetch('/api/experiments').then(response =>
                    !response.ok
                        ? Promise.reject(response)
                        : Promise.resolve(response.json())
                ).then(data => experiment_list.value = data)
            }
            return experiment_list
        })

        return {experiments}
    })
