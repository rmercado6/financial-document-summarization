<script setup>
import markdownit from 'markdown-it'
import {ref} from "vue";

const md = markdownit()

const props = defineProps({
    text: String
})

const plain_text = ref(false);
</script>

<template>
    <div class="flex h-full w-full overflow-x-hidden overflow-y-hidden relative">
        <div v-bind:class="plain_text ? 'md-display-btn active' : 'md-display-btn inactive'"
             @click="plain_text = !plain_text">
            Aa
        </div>
        <div v-if="!plain_text" class="overflow-y-scroll overflow-x-clip h-full w-full p-3 markdown-body" v-html="md.render(props.text)">
        </div>
        <textarea v-if="plain_text" readonly
                  class="p-3 overflow-y-scroll overflow-x-clip resize-none flex-grow h-full w-full rounded-md
                         cursor-default focus:outline-none"
                  :value="text">
                    </textarea>
    </div>
</template>

<style scoped>
.md-display-btn {
    @apply absolute bottom-1 right-6;
    @apply flex justify-center items-center aspect-square border rounded-md text-xs h-6 font-mono text-center;
    @apply hover:cursor-pointer hover:bg-slate-300 hover:border-slate-500 hover:text-slate-800;
}

.md-display-btn.inactive {
    @apply bg-slate-50 border-slate-400 text-slate-500;
}

.md-display-btn.active {
    @apply bg-blue-200 border-blue-400 text-blue-700;
}
</style>