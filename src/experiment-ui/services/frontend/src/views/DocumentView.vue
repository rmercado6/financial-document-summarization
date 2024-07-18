<script setup>
import DocumentPreview from "@/components/DocumentPreview.vue";

const props = defineProps({
    title: String,
    ticker: String,
    year: String,
    document_type: String
})
</script>

<template>
    <div class="flex flex-col max-h-full h-full overflow-y-hidden">
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
        <div class="mt-2 flex flex-col h-full overflow-y-hidden">
            <DocumentPreview :title="title" :ticker="ticker" :document_type="document_type" :year="year">
            </DocumentPreview>
        </div>
    </div>
</template>

<style scoped>
</style>
