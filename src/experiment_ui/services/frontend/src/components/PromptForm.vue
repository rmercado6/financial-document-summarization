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
const prompt_1 = ref(
    "Context information is below.\n" +
    "---------------------\n" +
    "{text}\n" +
    "---------------------\n" +
    "Given the context information and no prior knowledge, {task}:"
);
const prompt_2 = ref(
    "The task is to {task}.\n" +
    "We have provided an initial summary: {existing_answer}\n" +
    "We have the opportunity to refine the existing summary\n" +
    '(only if needed) with some more context below.\n' +
    "------------\n" +
    "{text}\n" +
    "------------\n" +
    "Given the new context, refine the original summary to better fit the task.\n" +
    "You must provide a response, either the initial summary or refined summary."
);
const task = ref('make a summary');
const similarity_filter = ref(false);

function query_model() {
    store.query_model({
        model: model.value,
        pipeline: pipeline.value,
        prompt_1: prompt_1.value,
        prompt_2: prompt_2.value,
        task: task.value,
        similarity_filter: similarity_filter.value,
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
    <div class="flex flex-col h-full w-full text-sm">
        <div class="flex gap-3 mb-2 pb-2 pr-3 items-center border-b border-slate-100">
            <h3 class="text-xl px-1 grow font-semibold">
                Query Model
            </h3>
        </div>
        <div class="flex flex-col gap-2 overflow-y-auto rounded-md">
            <div class="flex gap-2">
                <h4>Model</h4>
                <div class="flex flex-1 gap-2">
                    <span v-bind:class="model === 'gpt' ? 'select-pill active' : 'select-pill inactive'"
                          @click="model = 'gpt'">gpt-4o-2024-05-13</span>
                    <span v-bind:class="model === 'mistral' ? 'select-pill active' : 'select-pill inactive'"
                          @click="model = 'mistral'">Mistral</span>
                    <span v-bind:class="model === 'llama' ? 'select-pill active' : 'select-pill inactive'"
                          @click="model = 'llama'">Llama</span>
                </div>
            </div>
            <div class="flex gap-2">
                <h4>Pipeline</h4>
                <div class="flex flex-1 gap-2">
                    <span v-bind:class="pipeline === 'refine' ? 'select-pill active' : 'select-pill inactive'"
                          @click="pipeline = 'refine'">Refine</span>
<!--                    <span v-bind:class="pipeline === 'mapreduce' ? 'select-pill active' : 'select-pill inactive'"-->
<!--                          @click="pipeline = 'mapreduce'">MapReduce</span>-->
                </div>
            </div>
            <div>
                <h4 v-html="pipeline === 'refine' ? 'Initial Prompt / Question Prompt' : 'Map Prompt'"></h4>
                <textarea class="prompt-input" rows="7" v-model="prompt_1"></textarea>
            </div>
            <div>
                <h4 v-html="pipeline === 'refine' ? 'Refine Prompt' : 'Combine Prompt'"></h4>
                <textarea class="prompt-input" rows="7" v-model="prompt_2"></textarea>
            </div>
            <div>
                <div class="flex gap-2">
                    <h4>Task</h4>
                    <p class="flex-1 italic text-slate-500 text-xs flex justify-end items-center">
                        Replaces the variable `{task}` if provided on the prompts.
                    </p>
                </div>
                <textarea class="prompt-input" rows="2" v-model="task"></textarea>
            </div>
            <div>
                <div class="flex gap-2 px-2 justify-end">
                    <input type="checkbox" id="checkbox" v-model="similarity_filter">
                    <label for="checkbox">Filter relevant documents?</label>
                </div>
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
    @apply font-semibold mb-1 content-center;
}

span.select-pill {
    @apply py-1 px-3 border rounded-md flex-1 text-center content-center font-mono text-xs;
}

span.select-pill.inactive {
    @apply border-slate-300 bg-slate-100 text-slate-400;
    @apply hover:border-slate-500 hover:bg-slate-200 hover:text-slate-700
}

span.select-pill.active {
    @apply border-blue-600 bg-blue-100 text-blue-600;
}

textarea.prompt-input {
    @apply overflow-x-clip overflow-y-scroll resize-none w-full border border-slate-300 rounded-md text-sm p-2;
}

.btn {
    @apply py-1 px-3 font-mono border rounded-md border-emerald-600 bg-emerald-50 text-emerald-600 text-center content-center;
    @apply hover:border-emerald-600 hover:bg-emerald-100 hover:text-emerald-700 hover:cursor-pointer hover:font-semibold;
}
</style>