<script setup>
import MarkdownIt from "markdown-it";
import VueMarkdownIt from 'vue3-markdown-it';

const markdown = new MarkdownIt();

const props = defineProps({
    text: String
})
</script>

<template>
    <div class="overflow-y-auto overflow-x-clip h-full p-3 markdown-body" >
        <VueMarkdownIt :source="props.text"></VueMarkdownIt>
    </div>
</template>

<style scoped></style>
