<script setup>
import router from "@/router/index.js";

import {useQueryLLMs} from "@/stores/query_llms.js";
import {onBeforeMount, ref} from "vue";
import ExperimentViewer from "@/components/ExperimentViewer.vue";

let queryLLMs = useQueryLLMs();

const d = queryLLMs.query.document


window.addEventListener("beforeunload", event => {
    event.preventDefault();
})

onBeforeMount(() => {
    if (Object.keys(queryLLMs.query).length === 0) {
        router.back();
    }
})

</script>

<template>
    <div v-if="d" class="flex flex-col h-full overflow-y-hidden overflow-x-hidden">
        <div v-if="queryLLMs.querying">Querying model ...</div>
        <ExperimentViewer v-if="!queryLLMs.querying" :experiment="queryLLMs.response"></ExperimentViewer>
    </div>
</template>

<style scoped>
</style>