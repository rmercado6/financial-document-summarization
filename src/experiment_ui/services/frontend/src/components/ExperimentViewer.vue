<script setup>
import {ref, watch} from "vue";

import DocumentDetail from "@/components/DocumentDetail.vue";
import ExperimentCommentsPanel from "@/components/ExperimentCommentsPanel.vue";
import ExperimentContentRenderer from "@/components/ExperimentContentRenderer.vue";
import NavitemIcon from "@/components/NavitemIcon.vue";

const props = defineProps({
    experiment: Object
})

const experiment_view = ref(null);

const navigator = ref([
    {
        name: "Input Documents",
        type: 'folder',
        content: 'experiment.pipeline_outputs.input_documents',
        open: false,
        content_prefix: 'Document',
        content_type: 'input_documents'
    },
    {
        name: "Intermediate Steps",
        type: 'folder',
        content: 'experiment.pipeline_outputs.intermediate_steps',
        open: false,
        content_prefix: 'Output',
        content_type: 'markdown'
    },
    {
        name: "Final Response",
        type: 'output',
        content: 'experiment.pipeline_outputs.output_text',
        content_type: 'markdown'
    },
    {
        name: "Original Input PDF/Web document",
        type: 'webview',
        content: 'experiment.original_document.src_url',
        content_type: 'webview'
    },
    {
        name: "Original Input Text",
        type: 'document',
        content: 'experiment.original_document.doc',
        content_type: 'markdown'
    },
    {
        name: 'Prompt Templates',
        type: 'prompt-template',
        content: 'experiment.query',
        content_type: 'prompts'
    }
]);

const open_doc = ref({
    name: '',
    content: '',
    type: ''    // webview, md, prompts
})

function click_nav_item(nav_item) {
    if (nav_item.type === 'folder') {
        nav_item.open = !nav_item.open
        return
    }
    display_content(
        nav_item.content.split('.').reduce((p, c) => p && p[c] || null, props),
        nav_item.name,
        nav_item.content_type
    )
}

function display_content(content, name, content_type) {
    open_doc.value.name = name;
    if (content_type === 'input_documents') {
        open_doc.value.content = content.page_content;
        open_doc.value.type = 'markdown';
        return
    }

    open_doc.value.content = content;
    open_doc.value.type = content_type;
}

watch(experiment_view, () => {
    click_nav_item(navigator.value[2])
})
</script>

<template>
    <div v-if="experiment" ref="experiment_view"
         class="flex flex-col h-full w-full overflow-y-hidden overflow-x-hidden divide-y divide-slate-300">
        <div class="flex gap-4 pb-2 bg-slate-50 text-sm p-2 px-3">
            <DocumentDetail :title="experiment.original_document.title"
                            :ticker="experiment.original_document.ticker"
                            :document_type="experiment.original_document.document_type"
                            :year="experiment.original_document.year"
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
            <div class="flex flex-col overflow-x-auto overflow-y-auto bg-slate-100 w-1/6 p-2
                        font-mono text-xs text-slate-600 border-r border-slate-300">
                <!-- Navigator -->
                <div class="folder" v-for="nav_item in navigator">
                    <span v-bind:class="open_doc.name === nav_item.name ? 'nav-element active' : 'nav-element'"
                          @click="click_nav_item(nav_item)">
                        <NavitemIcon :type="nav_item.type" :open="nav_item.open"></NavitemIcon>
                        <span class="">
                            {{nav_item.name}}
                        </span>
                    </span>
                    <div v-if="nav_item.type === 'folder' && nav_item.open"
                         v-for="(x, index) in nav_item.content.split('.').reduce((p,c)=>p&&p[c]||null, props)"
                         @click="display_content(x, nav_item.content_prefix + ' ' + (index + 1), nav_item.content_type)"
                         v-bind:class="open_doc.name === nav_item.content_prefix + ' ' + (index + 1) ? 'nav-element active !pl-4' : 'nav-element !pl-4'">
                        <NavitemIcon
                            :type="nav_item.content_prefix.toLowerCase() === 'output' ? 'output' : 'document'"></NavitemIcon>
                        <span>
                            {{nav_item.content_prefix}} {{index + 1}}
                        </span>
                    </div>
                </div>
            </div>
            <ExperimentContentRenderer :doc="open_doc"></ExperimentContentRenderer>
            <ExperimentCommentsPanel :uuid="experiment.uuid"></ExperimentCommentsPanel>
        </div>
    </div>
</template>

<style scoped>
.detail-pill {
    @apply font-mono text-xs px-2 py-1 border border-slate-600 bg-white text-slate-700 rounded-md;
}

.folder {
    @apply flex flex-col gap-1;
}

.nav-element {
    @apply flex gap-1 cursor-default py-1 px-2;
    @apply hover:bg-slate-300
}

.nav-element.active {
    @apply bg-blue-200 text-blue-800;
}
</style>