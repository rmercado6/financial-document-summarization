<script setup>
import PipelineStep from "@/components/PipelineStep.vue";
import DocumentDetail from "@/components/DocumentDetail.vue";
import DocumentViewer from "@/components/DocumentViewer.vue";
import {onMounted, ref, watch} from "vue";

const props = defineProps({
    experiment: Object
})

const active_step = ref(-1);

const stepsPanel = ref(null);
const finalStep = ref(null);

function get_input_doc() {
    if (active_step.value >= 0) {
        return props.experiment.pipeline_outputs.input_documents[active_step.value].page_content
    }
    return ''
}

function get_model_response() {
    if (active_step.value >= 0) {
        return props.experiment.pipeline_outputs.intermediate_steps[active_step.value]
    }
    return props.experiment.pipeline_outputs.output_text
}

function get_prompt() {
    if (active_step.value >= 0) {
        return props.experiment.query.question_prompt
    }
    return props.experiment.query.refine_prompt
}

watch(stepsPanel, (new_value, old_value) => {
    new_value.scrollTo({
        top: new_value.scrollHeight,
        behavior: 'smooth'
    });
})

</script>

<template>
    <div v-if="experiment" class="flex flex-col overflow-y-hidden overflow-x-hidden divide-y divide-slate-300">
        <div class="flex gap-4 pb-2 bg-slate-50 text-sm p-2 px-3">
            <DocumentDetail :title="experiment.query.document.title"
                            :ticker="experiment.query.document.ticker"
                            :document_type="experiment.query.document.document_type"
                            :year="experiment.query.document.year"
                            class="flex-1" oneline></DocumentDetail>
            <div class="flex gap-2">
                <div class="flex-1 content-center text-end"><span
                    class="detail-pill">{{experiment.query.model}}</span></div>
                <div class="flex-1 content-center text-end"><span
                    class="detail-pill">{{experiment.query.pipeline}}</span></div>
            </div>
        </div>
        <div class="flex flex-1 overflow-y-hidden overflow-x-hidden divide-x ">
            <div class="steps-panel" ref="stepsPanel">
                <PipelineStep v-for="(x, index) in experiment.pipeline_outputs.input_documents"
                                   :i="(index + 1).toString()" :input_doc="x.page_content"
                                   v-bind:active="active_step === index"
                                    @click="active_step = index"></PipelineStep>
                <PipelineStep :i="''" :input_doc="'FINAL ANSWER'" ref="finalStep"
                                   v-bind:active="active_step === -1"
                                   @click="active_step = -1"></PipelineStep>
            </div>
            <div class="flex flex-col flex-1 overflow-y-hidden overflow-x-hidden">
                <div class="flex p-1 bg-slate-50 border-b border-slate-200">
                        <textarea
                            class="flex-grow resize-none overflow-x-clip overflow-y-auto font-mono border border-slate-200 rounded-md text-sm py-1 px-2"
                            rows="4" :value="get_prompt()"></textarea>
                </div>
                <div class="flex flex-1 overflow-y-hidden overflow-x-hidden divide-x divide-slate-200">
                    <div v-if="active_step >= 0" class="content-panel">
                        <span class="label">Input</span>
                        <DocumentViewer
                            :text="get_input_doc()">
                        </DocumentViewer>
                    </div>
                    <div class="content-panel">
                        <span class="label">Output</span>
                        <DocumentViewer :text="get_model_response()">
                        </DocumentViewer>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.steps-panel {
    @apply w-1/5 overflow-x-hidden overflow-y-auto divide-y;
}

.content-panel {
    @apply flex-1 overflow-y-hidden overflow-x-hidden flex flex-col;
}

.content-panel .label {
    @apply px-3 py-1 text-sm font-semibold border-b border-slate-200 bg-slate-50;
}

.detail-pill {
    @apply font-mono px-2 py-1 border border-slate-600 bg-white text-slate-700 rounded-md;
}
</style>