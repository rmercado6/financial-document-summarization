<script setup>
const props = defineProps({
    i: String,
    input_doc: String,
    active: Boolean
})

function get_class(){
    let c = 'step';
    c += ' ' + (props.active ? 'active' : 'inactive');
    c += props.i === '' ? ' final' : '';
    return c;
}
</script>

<template>
<div v-bind:class="get_class()">
    <span v-if="i !== ''" class="content-center">{{i}}</span>
    <span class="line-clamp-3 text-sm">{{input_doc}}</span>
</div>
</template>

<style scoped>
.step {
    @apply flex gap-4 py-2 px-4;
}
.step.inactive {
    @apply hover:bg-blue-50 hover:cursor-pointer;
}

.step.active {
    @apply border border-blue-200 bg-blue-50 font-semibold text-blue-800;
}
.step.final {
    @apply text-center justify-center;
}
</style>