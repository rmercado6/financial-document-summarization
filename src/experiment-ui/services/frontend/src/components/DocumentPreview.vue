<script setup>
import MarkdownRender from "@/components/MarkdownRender.vue";


import {useDocumentStore} from "@/stores/document.js";
import {onMounted, ref} from "vue";

const loading = ref(true);
const plain_text = ref(false);
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
    <div class="flex gap-3 my-2 pb-2 pr-3 items-center border-b border-slate-100">
        <h3 class="text-xl px-1 grow font-semibold">
            Document preview
        </h3>
        <div v-bind:class="plain_text ? 'md-display-btn active' : 'md-display-btn inactive'"
             @click="plain_text = !plain_text">
            Aa
        </div>
    </div>
    <div v-if="loading" class="md-display bg-slate-50 text-slate-600 flex justify-center items-center">
        loading ...
    </div>
    <textarea v-if="!loading && plain_text" readonly
              class="md-display p-3 !overflow-y-scroll resize-none"
              :value="documentStore.document.doc">
    </textarea>
    <div v-if="!loading && !plain_text" class="md-display flex flex-col h-full">
        <MarkdownRender :text="documentStore.document.doc"></MarkdownRender>
    </div>
</div>

</template>

<style scoped>
.md-display {
    @apply flex-grow h-full border border-slate-200 rounded-md overflow-y-hidden overflow-x-clip;
}
.md-display-btn{
    @apply flex justify-center items-center aspect-square border rounded-md text-xs h-6 font-mono text-center;
    @apply hover:cursor-pointer hover:bg-slate-300 hover:border-slate-500 hover:text-slate-800;
}
.inactive {
    @apply bg-slate-50  border-slate-300 text-slate-400;
}
.active {
    @apply bg-slate-200 border-slate-400 text-slate-700;
}
</style>