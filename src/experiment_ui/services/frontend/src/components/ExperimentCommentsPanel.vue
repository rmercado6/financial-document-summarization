<script setup>
import {onMounted, ref} from "vue";
import {useExperimentCommentsStore} from "@/stores/experiment_comments.js";

const props = defineProps({
    uuid: String
})

const experimentComments = useExperimentCommentsStore();

const new_comment = ref('');

onMounted(() => {
    experimentComments.fetch_comments(props.uuid)
})

function post_comment(){
    if (new_comment.value.trim() !== ''){
        experimentComments.post_comment(props.uuid, new_comment.value)
    }
    new_comment.value = '';
}
</script>

<template>
    <div class="comments-panel">
        <div v-if="experimentComments.loading" class="comments-section">
            loading comments...
        </div>
        <div v-if="!experimentComments.loading" class="comments-section">
            <div class="comment" v-for="c in experimentComments.comments">
                <span class="content">{{c.text}}</span>
                <span class="date">{{(new Date(c.datetime).toLocaleString())}}</span>
            </div>
        </div>
        <div class="input-section">
            <textarea rows="7"
                      class="resize-none overflow-y-scroll overflow-x-hidden border border-slate-300
                             rounded-md p-2 font-mono text-sm"
                      v-model="new_comment">
            </textarea>
            <div class="flex justify-end text-sm font-mono">
                <span class="bg-blue-100 border border-blue-600 text-blue-600 px-2 py-1 rounded-md hover:bg-blue-200
                             hover:text-blue-800 hover:border-blue-800 hover:cursor-pointer" @click="post_comment">
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
    @apply flex flex-col text-sm p-2 bg-slate-50 border border-slate-300 rounded-md font-mono;
}

.date {
    @apply text-xs font-mono content-center text-end text-slate-400 pt-2;
}

.content {
    @apply text-slate-600;
}
</style>