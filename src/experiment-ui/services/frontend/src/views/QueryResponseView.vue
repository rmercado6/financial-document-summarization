<script setup>
import router from "@/router/index.js";

import {useQueryLLMs} from "@/stores/query_llms.js";

import DocumentDetail from "@/components/DocumentDetail.vue";
import {onBeforeMount, onMounted} from "vue";

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
    <div v-if="d">
        <DocumentDetail :title="d.title" :ticker="d.ticker" :document_type="d.document_type"
                        :year="d.year"></DocumentDetail>
        <div v-if="queryLLMs.querying">Querying model ...</div>
        <div v-if="!queryLLMs.querying">
            RESPONSE
            {{queryLLMs.query}}
        </div>
    </div>
</template>

<style scoped>

</style>