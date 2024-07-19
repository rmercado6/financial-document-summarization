<script setup>

import MarkdownRender from "@/components/MarkdownRender.vue";
import {ref} from "vue";

defineProps({
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
        <MarkdownRender v-if="!plain_text"
                        :text="text">
        </MarkdownRender>
        <textarea v-if="plain_text" readonly
                  class="p-3 overflow-y-scroll overflow-x-clip resize-none flex-grow h-full rounded-md h-full w-full"
                  :value="text">
                    </textarea>
    </div>
</template>

<style scoped>
.md-display-btn {
    @apply absolute top-1 right-6;
    @apply flex justify-center items-center aspect-square border rounded-md text-xs h-6 font-mono text-center;
    @apply hover:cursor-pointer hover:bg-slate-300 hover:border-slate-500 hover:text-slate-800;
}

.md-display-btn.inactive {
    @apply bg-slate-50 border-slate-300 text-slate-400;
}

.md-display-btn.active {
    @apply bg-slate-200 border-slate-400 text-slate-700;
}
</style>