<script setup>
import MarkdownRender from "@/components/MarkdownRender.vue";


import {useDocumentStore} from "@/stores/document.js";
import {onMounted, ref} from "vue";
import DocumentViewer from "@/components/DocumentViewer.vue";

const loading = ref(true);
// const plain_text = ref(false);
const documentStore = useDocumentStore();
const props = defineProps({
    title: String,
    ticker: String,
    year: String,
    document_type: String
})

onMounted(async () => {
    await documentStore.fetch_document(props);
    loading.value = false;
})
</script>

<template>
    <div class="flex flex-col h-full w-full">
        <div class="flex gap-3 my-2 pb-1 pr-3 items-center border-b border-slate-200">
            <h3 class="text-xl px-1 grow">
                Document preview
            </h3>
        </div>
        <div v-if="loading" class="md-display bg-slate-50 text-slate-600 flex justify-center items-center">
            loading ...
        </div>
        <div class="flex md-display">
            <DocumentViewer :text="documentStore.document.doc"></DocumentViewer>
        </div>
    </div>
</template>

<style scoped>
.md-display {
    @apply flex-grow h-full border border-slate-200 rounded-md overflow-y-hidden overflow-x-clip;
}
</style>