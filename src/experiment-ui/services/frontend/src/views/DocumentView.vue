<script setup>
import {useDocumentStore} from "@/stores/document.js";
import {onMounted, ref} from "vue";

const loading = ref(true);
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
    <div>
        <h1 class="text-3xl font-bold">
            {{title}}
            <span class="text-xl">[{{ticker}}]</span>
        </h1>
        <p class="flex gap-2 text-xl">
            <span>{{document_type.replace('_', ' ').replace(/\b\w/g, s => s.toUpperCase())}}</span>
            <span>({{year}})</span>
        </p>
    </div>
    <div class="flex-grow mt-3 flex flex-col p-3">
        <h3 class="text-2xl px-1 pb-2">
            Document preview
        </h3>
        <div v-if="loading" class="md-display bg-slate-50 text-slate-600 flex justify-center items-center">
            loading ...
        </div>
        <div v-if="!loading" class="md-display">
            {{documentStore.document.doc}}
        </div>
    </div>
</template>

<style>
@media (min-width: 1024px) {
    .about {
        @apply flex-grow flex flex-col justify-center;
    }
    .md-display {
        @apply flex-grow h-full border border-slate-200 rounded-md p-3 overflow-y-auto overflow-x-clip
    }
}
</style>
