<script setup>
import router from "@/router/index.js";

import {useQueryLLMs} from "@/stores/query_llms.js";
import {onBeforeMount, watch} from "vue";
import {storeToRefs} from "pinia";

let queryLLMs = useQueryLLMs();

const d = queryLLMs.query.document

onBeforeMount(() => {
    if (Object.keys(queryLLMs.query).length === 0) {
        router.push('/history');
    }
})

const {querying} = storeToRefs(queryLLMs)

watch(querying, () => {
    router.push('/experiment/' + queryLLMs.response.uuid)
})
</script>

<template>
    <div v-if="d" class="flex flex-col h-full overflow-y-hidden overflow-x-hidden m-4">
        <div v-if="queryLLMs.querying"
             class="bg-slate-50 border border-slate-300 text-slate-600 rounded-md h-full w-full content-center font-mono text-sm text-center">
            Querying model ...
        </div>
    </div>
</template>

<style scoped>
</style>