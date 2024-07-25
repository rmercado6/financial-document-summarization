<script setup>
import {ref} from "vue";
import DocumentPreview from "@/components/DocumentPreview.vue";
import PromptForm from "@/components/PromptForm.vue";
import DocumentDetail from "@/components/DocumentDetail.vue";

defineProps({
    title: String,
    ticker: String,
    year: String,
    document_type: String
})

const display_prompt_form = ref(false);
</script>

<template>
    <div class="flex gap-4 max-h-full h-full overflow-y-hidden m-4">
        <div class="flex flex-col flex-1 max-h-full h-full overflow-y-hidden">
            <div class="flex">
                <DocumentDetail :title="title" :ticker="ticker" :document_type="document_type" :year="year">
                </DocumentDetail>
                <div class="flex-grow flex justify-end">
                    <span v-if="!display_prompt_form" class="btn" @click="display_prompt_form = true">
                        Query Model
                    </span>
                </div>
            </div>
            <div class="mt-2 flex flex-col h-full overflow-y-hidden">
                <DocumentPreview :title="title" :ticker="ticker" :document_type="document_type" :year="year">
                </DocumentPreview>
            </div>
        </div>
        <div v-if="display_prompt_form" class="flex flex-col flex-1 relative">
            <div @click="display_prompt_form = false" class="hide-btn">
                >
            </div>
            <PromptForm :title="title" :ticker="ticker" :document_type="document_type" :year="year"
                        class="absolute z-10 bg-white border border-slate-300 rounded-md p-3"></PromptForm>
        </div>
    </div>
</template>

<style scoped>
.btn {
    @apply p-1 px-2 bg-blue-50 border border-blue-100 text-blue-800 rounded-md h-fit;
    @apply hover:cursor-pointer hover:bg-blue-200 hover:border-blue-900 hover:text-blue-950
}

.hide-btn {
    @apply absolute -left-8 z-0 mt-3 p-3 text-center content-center bg-slate-50;
    @apply border-y border-l rounded-md border-slate-300 text-slate-500;
    @apply hover:cursor-pointer hover:bg-slate-100 hover:text-slate-700 hover:border-slate-700;
}
</style>
