import {ref, computed} from 'vue'
import {defineStore} from 'pinia'
import theme from "tailwindcss/defaultTheme.js";

export const useExperimentCommentsStore = defineStore(
    'experiment_comments',
    () => {
        const comments = ref();
        const loading = ref(false);

        async function fetch_comments(uuid) {
            loading.value = true;
            await fetch('/api/comments/' + uuid)
                .then(response => Promise.resolve(response.json()))
                .then(data => {
                    comments.value = data;
                    loading.value = false;
                })
        }

        return {comments, fetch_comments}
    })
