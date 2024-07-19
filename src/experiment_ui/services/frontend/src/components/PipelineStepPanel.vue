<script setup>
defineProps({
    i: String,
    input_doc: String
})
</script>

<template>
<div class="flex gap-4 py-2 px-4">
    <span class="content-center">{{i}}</span>
    <span class="line-clamp-3 text-sm">{{input_doc}}</span>
</div>
</template>

<style scoped>
.step.inactive {
    @apply hover:bg-blue-50 hover:cursor-pointer;
}

.step.active {
    @apply border border-blue-200 bg-blue-50 font-semibold text-blue-800;
}
</style>