<script setup>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputText from "primevue/inputtext";
import router from "@/router/index.js";

import {ref, onMounted} from 'vue';
import {FilterMatchMode} from '@primevue/core/api';
import {useFetchExperimentListStore} from "@/stores/experiments_list.js";

const experimentsStore = useFetchExperimentListStore()
const experiments = experimentsStore.experiments;

const loading = ref(true);
const filters = ref({
    global: {value: null, matchMode: FilterMatchMode.CONTAINS},
    'query.document.title': {value: null, matchMode: FilterMatchMode.CONTAINS},
    'query.document.ticker': {value: null, matchMode: FilterMatchMode.CONTAINS},
    'query.document.document_type': {value: null, matchMode: FilterMatchMode.CONTAINS},
    'query.document.year': {value: null, matchMode: FilterMatchMode.CONTAINS},
    'query.model': {value: null, matchMode: FilterMatchMode.CONTAINS},
    'query.pipeline': {value: null, matchMode: FilterMatchMode.CONTAINS},
    time: {value: null, matchMode: FilterMatchMode.CONTAINS}
});

const selected_experiment = ref();

function selectExperiment() {
    router.push({
        name: 'experiment', params: {
            uuid: selected_experiment.value.uuid
        }
    })
}

onMounted(() => {
    loading.value = false;
});
</script>

<template>
    <main>
        <DataTable v-model:filters="filters" :value="experiments" paginator :rows="9" filterDisplay="row"
                   v-model:selection="selected_experiment" selectionMode="single" :metaKeySelection="false"
                   @rowSelect="selectExperiment"
                   :loading="loading"
                   :globalFilterFields="[
                       'query.document.title', 'query.document.ticker', 'query.document.document_type', 'query.document.year', 'query.model', 'query.pipeline', 'time']">
            <template #header>
                <div class="flex justify-end">
                    <InputText v-model="filters['global'].value" placeholder="Search"/>
                </div>
            </template>
            <template #empty> No experiments found.</template>
            <template #loading> Loading experiments data. Please wait.</template>
            <Column filterField="query.document.title" header="Document">
                <template #body="{ data }">
                    {{data.query.document.title}}
                </template>
            </Column>
            <Column filterField="query.document.ticker" header="Ticker">
                <template #body="{ data }">
                    {{data.query.document.ticker}}
                </template>
            </Column>
            <Column filterField="query.document.document_type" header="Type">
                <template #body="{ data }">
                    {{data.query.document.document_type.replace('_', ' ').replace(/\b\w/g, s => s.toUpperCase())}}
                </template>
            </Column>
            <Column filterField="query.document.year" header="Year">
                <template #body="{ data }">
                    {{data.query.document.year}}
                </template>
            </Column>
            <Column field="query.model" header="Model">
                <template #body="{ data }">
                    {{data.query.model}}
                </template>
            </Column>
            <Column field="query.pipeline" header="Pipeline">
                <template #body="{ data }">
                    {{data.query.pipeline}}
                </template>
            </Column>
            <Column field="time" header="Time">
                <template #body="{ data }">
                    {{data.time}}
                </template>
            </Column>
        </DataTable>
    </main>
</template>
