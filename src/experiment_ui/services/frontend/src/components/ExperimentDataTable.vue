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
    document: {value: null, matchMode: FilterMatchMode.CONTAINS},
    model: {value: null, matchMode: FilterMatchMode.CONTAINS},
    pipeline: {value: null, matchMode: FilterMatchMode.CONTAINS},
    time: {value: null, matchMode: FilterMatchMode.CONTAINS}
});

const selected_experiment = ref();

function selectExperiment(){
    router.push({name: 'experiment', params: selected_experiment.value})
}

function getDocumentName(doc) {
    return doc.title
}

onMounted(() => {
    loading.value = false;
});
</script>

<template>
    <main>
        <DataTable v-model:filters="filters"  :value="experiments" paginator :rows="9" filterDisplay="row"
                   v-model:selection="selected_experiment" selectionMode="single" :metaKeySelection="false"
                   @rowSelect="selectExperiment"
                   :loading="loading"
                   :globalFilterFields="['document', 'model', 'pipeline', 'time']">
            <template #header>
                <div class="flex justify-end">
                    <InputText v-model="filters['global'].value" placeholder="Search"/>
                </div>
            </template>
            <template #empty> No experiments found.</template>
            <template #loading> Loading experiments data. Please wait.</template>
            <Column field="document" header="Document" style="min-width: 12rem">
                <template #body="{ data }">
                    {{getDocumentName(data.query.document)}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by document"/>
                </template>
            </Column>
            <Column field="model" header="Model" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.query.model}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by model"/>
                </template>
            </Column>
            <Column field="pipeline" header="Pipeline" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.query.pipeline}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by pipeline"/>
                </template>
            </Column>
            <Column field="time" header="Time" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.time}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by query time"/>
                </template>
            </Column>
        </DataTable>
    </main>
</template>
