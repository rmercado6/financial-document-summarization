<script setup>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputText from "primevue/inputtext";

import {ref, onMounted} from 'vue';
import {FilterMatchMode} from '@primevue/core/api';
import {useDocumentsStore} from "@/stores/documents.js";

const documentsStore = useDocumentsStore()

const documents = documentsStore.documents;
const loading = ref(true);
const filters = ref({
    global: {value: null, matchMode: FilterMatchMode.CONTAINS},
    title: {value: null, matchMode: FilterMatchMode.CONTAINS},
    ticker: {value: null, matchMode: FilterMatchMode.CONTAINS},
    year: {value: null, matchMode: FilterMatchMode.CONTAINS},
    document_type: {value: null, matchMode: FilterMatchMode.CONTAINS}
});

onMounted(() => {
    loading.value = false;
    console.log(documents.value)
});
</script>

<template>
    <main>
        <DataTable v-model:filters="filters" :value="documents" paginator :rows="10" dataKey="id" filterDisplay="row"
                   :loading="loading"
                   :globalFilterFields="['title', 'ticker', 'year', 'document_type']">
            <template #header>
                <div class="flex justify-end">
                    <InputText v-model="filters['global'].value" placeholder="Search"/>
                </div>
            </template>
            <template #empty> No documents found.</template>
            <template #loading> Loading documents data. Please wait.</template>
            <Column field="title" header="Title" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.title}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by title"/>
                </template>
            </Column>
            <Column field="ticker" header="Ticker" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.ticker}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by ticker"/>
                </template>
            </Column>
            <Column field="year" header="Year" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.year}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by year"/>
                </template>
            </Column>
            <Column field="document_type" header="Document Type" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.document_type.replace('_', ' ').replace(/\b\w/g, s => s.toUpperCase())}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by document type"/>
                </template>
            </Column>
        </DataTable>
    </main>
</template>
