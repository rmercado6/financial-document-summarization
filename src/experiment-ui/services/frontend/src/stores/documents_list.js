import {ref, computed} from 'vue'
import {defineStore} from 'pinia'

export const useFetchDocumentsListStore = defineStore(
    'documents',
    () => {
        const document_list = ref([]);

        const documents = computed(() => {
            if (document_list.value.length === 0) {
                fetch('/api/documents').then(response =>
                    !response.ok
                        ? Promise.reject(response)
                        : Promise.resolve(response.json())
                ).then(data => document_list.value = data)
            }
            return document_list
        })

        return {documents}
    })
