<script setup>
import {onMounted, ref} from "vue";
import PromptForm from "@/components/PromptForm.vue";
import DocumentDetail from "@/components/DocumentDetail.vue";
import DocumentViewer from "@/components/DocumentViewer.vue";

import {useDocumentStore} from "@/stores/document.js";

let props = defineProps({
    document_id: String,
})

const documentStore = useDocumentStore();

const display_prompt_form = ref(false);
const loading = ref(true);

onMounted(async () => {
    await documentStore.fetch_document(props.document_id);
    loading.value = false;
})
</script>

<template>
    <div class="flex max-h-full h-full overflow-y-hidden">
        <div class="flex flex-col flex-1 h-full overflow-y-hidden">
            <div v-if="!loading" class="flex">
                <DocumentDetail :title="documentStore.document.title"
                                :ticker="documentStore.document.ticker"
                                :document_type="documentStore.document.document_type"
                                :year="documentStore.document.year" class="px-3 py-1">
                </DocumentDetail>
                <div class="flex-grow flex justify-end items-center pr-4">
                    <span v-if="!display_prompt_form" class="btn" @click="display_prompt_form = true">
                        Query Model
                    </span>
                </div>
            </div>
            <div class="mt-2 flex flex-col h-full overflow-y-hidden">
                <div v-if="loading"
                     class="h-full w-full md-display bg-slate-50 text-slate-600 flex justify-center items-center">
                    loading ...
                </div>
                <div v-if="!loading" class="flex md-display h-full w-full">
                    <DocumentViewer :document="documentStore.document"></DocumentViewer>
                </div>
            </div>
        </div>
        <div v-if="display_prompt_form" class="flex flex-col flex-1 relative">
            <div @click="display_prompt_form = false" class="hide-btn">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-4">
                    <path fill-rule="evenodd"
                          d="M16.28 11.47a.75.75 0 0 1 0 1.06l-7.5 7.5a.75.75 0 0 1-1.06-1.06L14.69 12 7.72 5.03a.75.75 0 0 1 1.06-1.06l7.5 7.5Z"
                          clip-rule="evenodd"/>
                </svg>

            </div>
            <PromptForm :document_id="document_id"
                        class="absolute border-l border-slate-400 p-3 bg-slate-50 shadow-md shadow-slate-400"></PromptForm>
        </div>
    </div>
</template>

<style scoped>
.btn {
    @apply p-0.5 px-1 border border-blue-600 bg-blue-100 text-blue-600 rounded-md h-fit font-mono text-sm;
    @apply hover:cursor-pointer hover:bg-blue-200 hover:border-blue-900 hover:text-blue-950
}

.hide-btn {
    @apply absolute -left-8 z-0 mt-3 p-3 text-center content-center bg-slate-50 shadow-md shadow-slate-300;
    @apply border-y border-l rounded-md border-slate-400 text-slate-500;
    @apply hover:cursor-pointer hover:bg-slate-100 hover:text-slate-700 hover:border-slate-700;
}
</style>
