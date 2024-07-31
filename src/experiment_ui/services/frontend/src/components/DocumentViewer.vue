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
            <div class="flex-1 overflow-y-hidden overflow-x-hidden truncate">
                <span v-if="document.src_url !== null">
                    Source
                    <a :href="document.src_url" target="_blank" class="truncate">{{document.src_url}}</a>
                </span>
            </div>
            <div v-if="document.src_url !== null"
                 v-bind:class="display === 2 ? 'md-display-btn active' : 'md-display-btn inactive'"
                 @click="display = 2">
                Original Source
            </div>
            <div v-bind:class="display === 0 ? 'md-display-btn active' : 'md-display-btn inactive'"
                 @click="display = 0">
                Rendered MD
            </div>
            <div v-bind:class="display === 1 ? 'md-display-btn active' : 'md-display-btn inactive'"
                 @click="display = 1">
                Plain Text
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
.md-display-btn {
    @apply flex justify-center items-center border rounded-md text-xs font-mono text-center p-1;
    @apply hover:cursor-pointer hover:bg-slate-300 hover:border-slate-500 hover:text-slate-800;
}

.md-display-btn.inactive {
    @apply bg-slate-50 border-slate-400 text-slate-500;
}

.md-display-btn.active {
    @apply bg-blue-200 border-blue-400 text-blue-700;
}
</style>