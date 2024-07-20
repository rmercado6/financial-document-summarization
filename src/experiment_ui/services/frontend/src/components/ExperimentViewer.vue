<script setup>
import PipelineStep from "@/components/PipelineStep.vue";
import DocumentDetail from "@/components/DocumentDetail.vue";
import DocumentViewer from "@/components/DocumentViewer.vue";
import {ref, watch} from "vue";
import ExperimentCommentsPanel from "@/components/ExperimentCommentsPanel.vue";

const props = defineProps({
    experiment: Object
})

const active_step = ref(-1);

const stepsPanel = ref(null);
const finalStep = ref(null);

const showComments = ref(false);

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
                <div class="content-center">
                    <span class="detail-pill">{{experiment.query.model}}</span>
                </div>
                <div class="content-center">
                    <span class="detail-pill">{{experiment.query.pipeline}}</span>
                </div>
                <div class="content-center">
                    <span class="detail-pill">{{(new Date(experiment.time)).toLocaleString()}}</span>
                </div>
            </div>
        </div>
        <div class="flex flex-1 overflow-y-hidden overflow-x-hidden divide-x ">
            <div v-bind:class="!showComments ? 'w-1/5 steps-panel' : 'w-1/6 steps-panel'" ref="stepsPanel">
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
                    <textarea class="flex-1 resize-none overflow-x-clip overflow-y-auto font-mono border border-slate-200
                                     rounded-md text-sm py-1 px-2" rows="4" :value="get_prompt()"></textarea>
                    <div class="flex items-center p-3 relative">
                        <span v-bind:class="!showComments ? 'comments-btn' : 'comments-btn active'"
                              @click="showComments = !showComments">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5}
                                 stroke="currentColor" className="size-6">
                                <path strokeLinecap="round" strokeLinejoin="round" v-if="!showComments"
                                    d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166
                                    2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0
                                    1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626
                                    2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12
                                    3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"/>
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" v-if="showComments"
                                     strokeWidth={1.5} stroke="currentColor" className="size-6">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5"/>
                                </svg>
                            </svg>
                        </span>
                    </div>
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
            <ExperimentCommentsPanel v-if="showComments" :uuid="experiment.uuid"
                                     class="w-1/4"></ExperimentCommentsPanel>
        </div>
    </div>
</template>

<style scoped>
.steps-panel {
    @apply overflow-x-hidden overflow-y-auto divide-y;
}

.content-panel {
    @apply flex-1 overflow-y-hidden overflow-x-hidden flex flex-col;
}

.content-panel .label {
    @apply px-3 py-1 text-sm font-semibold border-b border-slate-200 bg-slate-50;
}

.detail-pill {
    @apply font-mono text-xs px-2 py-1 border border-slate-600 bg-white text-slate-700 rounded-md;
}

.comments-btn {
    @apply w-10 aspect-square p-2 rounded-full bg-slate-50 text-slate-700;
    @apply hover:bg-blue-200 hover:text-blue-900 hover:cursor-pointer;
}

.comments-btn.active {
    @apply text-slate-500 rounded-l rounded-md border-l border-y border-slate-300 bg-slate-100 absolute -right-2;
    @apply hover:bg-blue-200 hover:text-blue-900 hover:cursor-pointer;
}
</style>