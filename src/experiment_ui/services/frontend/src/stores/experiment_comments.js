import {ref, computed} from 'vue'
import {defineStore} from 'pinia'
import theme from "tailwindcss/defaultTheme.js";

export const useExperimentCommentsStore = defineStore(
    'experiment_comments',
    () => {
        const comments = ref([]);
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

        async function post_comment(uuid, text) {
            await fetch('/api/comment', {
                method: 'POST',
                body: JSON.stringify({
                    document_uuid: uuid,
                    text: text
                }),
                headers: {
                    "Content-Type": "application/json",
                }
            }).then(response =>
                !response.ok
                    ? Promise.reject(response)
                    : Promise.resolve(response.json())
            ).then(data => {
                comments.value.unshift(data);
            })
        }

        return {comments, fetch_comments, post_comment}
    })
