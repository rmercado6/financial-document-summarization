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
            query.value = {
                model: params.model,
                pipeline: params.pipeline,
                question_prompt: params.question_prompt,
                refine_prompt: params.refine_prompt,
                document: params.document
            }

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
