<script setup>
import router from "@/router/index.js";
import DocumentDetail from "@/components/DocumentDetail.vue";
import PipelineStepPanel from "@/components/PipelineStepPanel.vue";
import DocumentViewer from "@/components/DocumentViewer.vue";

import {useQueryLLMs} from "@/stores/query_llms.js";
import {onBeforeMount, ref} from "vue";

let queryLLMs = useQueryLLMs();

const d = queryLLMs.query.document
const active_step = ref(0);

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
        <div v-if="!queryLLMs.querying"
             class="flex flex-col overflow-y-hidden overflow-x-hidden border border-slate-300 h-full w-full rounded-lg divide-y divide-slate-300">
            <div class="flex gap-4 pb-2 bg-slate-50 text-sm p-2">
                <DocumentDetail :title="d.title" :ticker="d.ticker" :document_type="d.document_type"
                                :year="d.year" class="flex-1" oneline></DocumentDetail>
                <div class="flex gap-2">
                    <div class="flex-1 content-center text-end"><span
                        class="detail-pill">{{queryLLMs.query.model}}</span></div>
                    <div class="flex-1 content-center text-end"><span
                        class="detail-pill">{{queryLLMs.query.pipeline}}</span></div>
                </div>
            </div>
            <div class="flex flex-1 overflow-y-hidden overflow-x-hidden divide-x ">
                <div class="steps-panel">
                    <PipelineStepPanel v-for="(x, index) in queryLLMs.response.pipeline_outputs.input_documents"
                                       :i="index + 1"
                                       v-bind:class="active_step === index ? 'step active' : 'step inactive'"
                                       :input_doc="x.page_content" @click="active_step = index"></PipelineStepPanel>
                </div>
                <div class="flex flex-col flex-1 overflow-y-hidden overflow-x-hidden">
                    <div class="flex p-1 bg-slate-50 border-b border-slate-200">
                        <textarea class="flex-grow resize-none overflow-x-clip overflow-y-auto font-mono border border-slate-200 rounded-md text-sm py-1 px-2"
                                  rows="3" :value="queryLLMs.query.question_prompt"></textarea>
                    </div>
                    <div class="flex flex-1 overflow-y-hidden overflow-x-hidden">
                        <div class="content-panel">
                            <DocumentViewer
                                :text="queryLLMs.response.pipeline_outputs.input_documents[active_step].page_content">
                            </DocumentViewer>
                        </div>
                        <div class="content-panel">
                            <DocumentViewer :text="queryLLMs.response.pipeline_outputs.intermediate_steps[active_step]">
                            </DocumentViewer>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.steps-panel {
    @apply w-1/4 overflow-x-hidden overflow-y-auto divide-y;
}

.content-panel {
    @apply flex-1 overflow-y-hidden overflow-x-hidden flex;
}

.detail-pill {
    @apply font-mono px-2 py-1 border border-slate-600 bg-white text-slate-700 rounded-md;
}
</style>