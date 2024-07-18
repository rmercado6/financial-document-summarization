import {ref, computed} from 'vue'
import {defineStore} from 'pinia'
import theme from "tailwindcss/defaultTheme.js";

export const useDocumentStore = defineStore(
    'document',
    () => {
        const document = ref({});

        async function fetch_document(doc_props) {
            await fetch('/api/documents/' + doc_props.title + '/' + doc_props.ticker + '/' + doc_props.document_type + '/' + doc_props.year)
                .then(response => Promise.resolve(response.json()))
                .then(data => document.value = data)
        }

        return {fetch_document, document}
    })
