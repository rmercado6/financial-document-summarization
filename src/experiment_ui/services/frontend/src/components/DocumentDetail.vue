<script setup>
const props = defineProps({
    title: String,
    ticker: String,
    document_type: String,
    year: String
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
</template>

<style scoped>

</style>