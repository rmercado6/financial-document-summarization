import {ref} from 'vue'
import {defineStore} from 'pinia'

export const useDocumentStore = defineStore(
    'document',
    () => {
        const document = ref({});

        async function fetch_document(document_id) {
            await fetch('/api/documents/' + document_id)
                .then(response => Promise.resolve(response.json()))
                .then(data => document.value = data)
            // await fetch('/api/documents/' + doc_props.title + '/' + doc_props.ticker + '/' + doc_props.document_type + '/' + doc_props.year)
            //     .then(response => Promise.resolve(response.json()))
            //     .then(data => document.value = data)
        }

        return {fetch_document, document}
    })
