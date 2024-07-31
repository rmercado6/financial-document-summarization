<script setup>
import markdownit from 'markdown-it'
import {ref} from "vue";

const md = markdownit()

const props = defineProps({
    document: Object
})

const display = ref(0);
</script>

<template>
    <div class="flex flex-col h-full w-full overflow-x-hidden overflow-y-hidden relative">
        <div class="flex border-b border-slate-400 py-1 px-2 text-xs font-mono items-center gap-2">
            <div class="text-xs font-semibold">
                <span>DOC PREVIEW</span>
            </div>
            <div class="flex-1 overflow-y-hidden overflow-x-hidden truncate border border-slate-400 px-1">
                <span v-if="document.src_url !== null">
                    SRC
                    <a :href="document.src_url" target="_blank" class="truncate">{{document.src_url}}</a>
                </span>
            </div>
            <div v-if="document.src_url !== null"
                 v-bind:class="display === 2 ? 'btn active' : 'btn'"
                 @click="display = 2">
                ORIGINAL SOURCE
            </div>
            <div v-bind:class="display === 0 ? 'btn active' : 'btn'"
                 @click="display = 0">
                MARKDOWN
            </div>
            <div v-bind:class="display === 1 ? 'btn active' : 'btn'"
                 @click="display = 1">
                PLAIN TEXT
            </div>
        </div>
        <div v-if="display === 0" class="overflow-y-scroll overflow-x-clip h-full w-full p-3 markdown-body"
             v-html="md.render(props.document.doc)">
        </div>
        <textarea v-if="display === 1" readonly
                  class="p-3 overflow-y-scroll overflow-x-clip resize-none flex-grow h-full w-full rounded-md
                         cursor-default focus:outline-none"
                  :value="document.doc">
                    </textarea>
        <div v-if="display === 2" class="flex flex-col h-full w-full">
            <iframe :src="document.src_url" class="h-full w-full"></iframe>
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
</style>