<script setup>
import {ref} from "vue";

const props = defineProps({
    uuid: String
})

// TODO: replace comments with fetch from API
const comments = ref([
    {date: 'date', content: 'sample content'},
    {date: 'date', content: 'sample content'},
]);

const new_comment = ref('');
</script>

<template>
    <div class="comments-panel">
        <div class="comments-section">
            <div class="comment" v-for="c in comments">
                <span class="content">{{c.content}}</span>
                <span class="date">{{c.date}}</span>
            </div>
        </div>
        <div class="input-section">
            <textarea rows="7"
                      class="resize-none overflow-y-scroll overflow-x-hidden border border-slate-300
                             rounded-md p-2 font-mono text-sm"
                      :value="new_comment">
            </textarea>
            <div class="flex justify-end text-sm font-mono">
                <span class="bg-blue-100 border border-blue-600 text-blue-600 px-2 py-1 rounded-md hover:bg-blue-200
                             hover:text-blue-800 hover:border-blue-800 hover:cursor-pointer">
                    Comment
                </span>
            </div>
        </div>
    </div>
</template>

<style scoped>
.comments-panel {
    @apply bg-slate-100 shadow-inner shadow-slate-300 flex flex-col divide-y divide-slate-300
    overflow-x-hidden overflow-y-hidden;
}

.comments-section {
    @apply flex-1 flex flex-col gap-2 p-2 overflow-x-hidden overflow-y-scroll;
}

.input-section {
    @apply h-1/3 p-2 flex flex-col gap-2;
}

.comment {
    @apply flex flex-col text-sm p-2 bg-slate-50 border border-slate-300 rounded-md;
}

.date {
    @apply text-xs font-mono content-center text-end text-slate-400;
}

.content {
    @apply text-slate-600;
}
</style>