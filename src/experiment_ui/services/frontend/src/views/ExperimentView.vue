<script setup>
import {useExperimentStore} from "@/stores/experiment.js";
import ExperimentViewer from "@/components/ExperimentViewer.vue";

const experimentStore = useExperimentStore();

const props = defineProps({
    uuid: String,
})

experimentStore.fetch_experiment(props.uuid)
</script>

<template>
    <ExperimentViewer :experiment="experimentStore.experiment"></ExperimentViewer>
</template>

<style scoped>
</style>
