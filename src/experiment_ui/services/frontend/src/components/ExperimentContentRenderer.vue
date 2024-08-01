<script setup>
import markdownit from 'markdown-it'
import {ref, watch} from "vue";

const md = markdownit()

const props = defineProps({
    doc: Object
})

const display = ref(0)

watch(props.doc, (old_doc, new_doc) => {
    if (new_doc.type === 'prompts'){
        display.value = 2;
        return
    }
    if (new_doc.type === 'webview'){
        display.value = 3;
        return
    }
    if (new_doc.type === 'markdown' && display.value > 1){
        display.value = 0;
    }
})
</script>

<template>
    <div class="flex flex-col flex-1 overflow-y-hidden overflow-x-hidden">
        <div class="flex gap-2 bg-slate-50 font-mono text-slate-700 border-b border-slate-400 py-1 px-2 text-sm items-center">
            <span v-if="doc.type !== 'webview'" class="flex-1">
                {{doc.name}}
            </span>
            <span v-if="doc.type === 'markdown'" v-bind:class="display === 0 ? 'btn active' : 'btn'" @click="display = 0">
                MARKDOWN
            </span>
            <span v-if="doc.type === 'markdown'" v-bind:class="display === 1 ? 'btn active' : 'btn'" @click="display = 1">
                PLAIN TEXT
            </span>
            <div v-if="doc.type === 'webview'" class="flex flex-col w-full gap-1">
                <span class="px-1">{{doc.name}}</span>
                <span class="border border-slate-400 w-full text-xs py-0.5 px-1 bg-white">
                    SRC
                    <a :href="doc.content" target="_blank">{{doc.content}}</a>
                </span>
            </div>
        </div>
        <div v-if="display === 0" class="overflow-y-scroll overflow-x-clip h-full w-full p-3 markdown-body"
             v-html="md.render(doc.content)">
        </div>
        <textarea v-if="display === 1" readonly
              class="p-3 overflow-y-scroll overflow-x-clip resize-none flex-grow h-full w-full rounded-md
                     cursor-default focus:outline-none"
              :value="doc.content">
                </textarea>
        <div v-if="display === 2" class="overflow-y-scroll overflow-x-clip h-full w-full p-3 flex flex-col">
            <span class="section">Task</span>
            <textarea readonly rows="2" v-html="doc.content.task"></textarea>
            <span class="section">Initial Prompt</span>
            <textarea readonly rows="10" v-html="doc.content.prompt_1"></textarea>
            <span class="section">Refine Prompt</span>
            <textarea readonly rows="10" v-html="doc.content.prompt_2"></textarea>
        </div>
        <div v-if="display === 3" class="overflow-y-hidden overflow-x-hidden h-full w-full">
            <iframe :src="doc.content" class="w-full h-full"></iframe>
        </div>
    </div>
</template>

<style scoped>
.btn {
    @apply text-xs py-0 px-1 border border-slate-700 content-center cursor-pointer;
    @apply hover:bg-slate-400 hover:text-slate-800;
}

.btn.active {
    @apply bg-green-200;
}

textarea {
    @apply border border-slate-400 w-full font-mono text-sm mb-3 p-2 overflow-x-clip overflow-y-scroll;
}

.section {
    @apply font-bold
}
</style>