import {ref, computed} from 'vue'
import {defineStore} from 'pinia'

export const useQueryLLMs = defineStore(
    'QueryLLMs',
    () => {
        const querying = ref(false)
        const query = ref({});
        const response = ref({});

        let query_model = async params => {
            querying.value = true;
            query.value = params

            await fetch('/api/query_model', {
                method: 'POST',
                body: JSON.stringify(query.value),
                headers: {
                    "Content-Type": "application/json",
                },
            }).then(response =>
                !response.ok
                    ? Promise.reject(response)
                    : Promise.resolve(response.json())
            ).then(data => {
                response.value = data;
                querying.value = false;
            })
        }

        return {querying, query, query_model, response}
    })
