import {ref, computed} from 'vue'
import {defineStore} from 'pinia'

export const useQueryLLMs = defineStore(
    'QueryLLMs',
    () => {
        const querying = ref(false)
        const query = ref({});

        let query_model = async params => {
            querying.value = true;
            query.value = {
                model: params.model,
                pipeline: params.pipeline,
                question_prompt: params.question_prompt,
                refine_prompt: params.refine_prompt,
                document: params.document
            }

            setTimeout(() => {
                querying.value = false;
            }, 2500);
            return params
        }

        return {querying, query, query_model}
    })
