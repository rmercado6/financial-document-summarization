<script setup>
import {ref} from "vue";
import router from "@/router/index.js";

import {useQueryLLMs} from "@/stores/query_llms.js";

const props = defineProps({
    title: String,
    ticker: String,
    year: String,
    document_type: String,
})

const store = useQueryLLMs();

const model = ref('llama');
const pipeline = ref('refine');
const question_prompt = ref(
    'Please provide a summary of the following text.\n' +
    'TEXT: {text}\n' +
    'SUMMARY:'
);
const refine_prompt = ref(
    'Write a concise summary of the following text delimited by triple backquotes.\n' +
    'Return your response in bullet points which covers the key points of the text.\n' +
    '```{text}```\n' +
    'BULLET POINT SUMMARY:'
);

function query_model() {
    store.query_model({
        model: model.value,
        pipeline: pipeline.value,
        question_prompt: question_prompt.value,
        refine_prompt: refine_prompt.value,
        document: {
            title: props.title,
            year: props.year,
            ticker: props.ticker,
            document_type: props.document_type,
        }
    })
    router.push({name: 'query_response'})
}
</script>

<template>
    <div class="flex flex-col h-full w-full">
        <div class="flex gap-3 my-2 pb-2 pr-3 items-center border-b border-slate-100">
            <h3 class="text-xl px-1 grow font-semibold">
                Query Model
            </h3>
        </div>
        <div class="flex flex-col gap-3 overflow-y-auto rounded-md">
            <div>
                <h4>Model</h4>
                <div class="flex gap-2">
                    <span v-bind:class="model === 'gpt' ? 'select-pill active' : 'select-pill inactive'"
                          @click="model = 'gpt'">ChatGPT 4 Turbo</span>
                    <span v-bind:class="model === 'mistral' ? 'select-pill active' : 'select-pill inactive'"
                          @click="model = 'mistral'">Mistral</span>
                    <span v-bind:class="model === 'llama' ? 'select-pill active' : 'select-pill inactive'"
                          @click="model = 'llama'">Llama</span>
                </div>
            </div>
            <div>
                <h4>Pipeline</h4>
                <div class="flex gap-2">
                    <span v-bind:class="pipeline === 'refine' ? 'select-pill active' : 'select-pill inactive'"
                          @click="model = 'refine'">Refine</span>
                    <span v-bind:class="pipeline === 'mapreduce' ? 'select-pill active' : 'select-pill inactive'"
                          @click="model = 'mapreduce'">MapReduce</span>
                </div>
            </div>
            <div>
                <h4>Question Prompt</h4>
                <textarea class="prompt-input" rows="7" v-model="question_prompt"></textarea>
            </div>
            <div>
                <h4>Refine Prompt</h4>
                <textarea class="prompt-input" rows="7" v-model="refine_prompt"></textarea>
            </div>
            <div class="flex justify-end">
                <span class="btn" @click="query_model">
                    Query
                </span>
            </div>
        </div>
    </div>
</template>

<style scoped>
h4 {
    @apply font-semibold mb-1;
}

span.select-pill {
    @apply py-1 px-3 border rounded-md flex-1 text-center content-center font-mono text-sm;
}

span.select-pill.inactive {
    @apply border-slate-300 bg-slate-100 text-slate-400;
    @apply hover:border-slate-500 hover:bg-slate-200 hover:text-slate-700
}

span.select-pill.active {
    @apply border-blue-600 bg-blue-100 text-blue-600;
}

textarea.prompt-input {
    @apply overflow-x-clip overflow-y-scroll resize-none w-full border border-slate-200 rounded-md text-sm p-2;
}

.btn {
    @apply py-1 px-3 font-mono border rounded-md border-emerald-600 bg-emerald-50 text-emerald-600 text-center content-center;
    @apply hover:border-emerald-600 hover:bg-emerald-100 hover:text-emerald-700 hover:cursor-pointer hover:font-semibold;
}
</style>