<script setup>
const props = defineProps({
    title: String,
    ticker: String,
    document_type: String,
    year: String,
    oneline: Boolean
})
</script>

<template>
    <div v-bind:class="oneline ? 'flex gap-2' : ''">
        <h1 class="text-2xl font-semibold">
            {{title}}
            <span class="text-xl">[{{ticker}}]</span>
        </h1>
        <div v-bind:class="oneline ? 'flex gap-2 text-xl items-end' : 'flex gap-2 text-xl'">
            <span>{{document_type.replace('_', ' ').replace(/\b\w/g, s => s.toUpperCase())}}</span>
            <span>({{year}})</span>
        </div>
    </div>
</template>

<style scoped>

</style>