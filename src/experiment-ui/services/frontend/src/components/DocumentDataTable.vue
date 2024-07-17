<script setup>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import IconField from "primevue/iconfield";
import InputIcon from 'primevue/inputicon';
import InputText from "primevue/inputtext";

import {ref, onMounted} from 'vue';
import {FilterMatchMode} from '@primevue/core/api';

let products = [
    {
        'code': 123,
        'name': 'asd',
        'category': 'asd category',
        'quantity': 2
    },
    {
        'code': 1234,
        'name': 'asdf',
        'category': 'asd category',
        'quantity': 2
    }
]

const customers = ref();
const loading = ref(true);
const filters = ref({
    global: {value: null, matchMode: FilterMatchMode.CONTAINS},
    code: {value: null, matchMode: FilterMatchMode.CONTAINS},
    name: {value: null, matchMode: FilterMatchMode.CONTAINS},
    category: {value: null, matchMode: FilterMatchMode.CONTAINS},
    quantity: {value: null, matchMode: FilterMatchMode.CONTAINS}
});

onMounted(() => {
    customers.value = products;
    loading.value = false;
});
</script>

<template>
    <main>
        <DataTable v-model:filters="filters" :value="customers" paginator :rows="10" dataKey="id" filterDisplay="row"
                   :loading="loading"
                   :globalFilterFields="['code', 'name', 'category', 'quantity']">
            <template #header>
                <div class="flex justify-end">
                    <IconField>
                        <InputIcon>
                            <i class="pi pi-search"/>
                        </InputIcon>
                        <InputText v-model="filters['global'].value" placeholder="Keyword Search"/>
                    </IconField>
                </div>
            </template>
            <template #empty> No customers found.</template>
            <template #loading> Loading customers data. Please wait.</template>
            <Column field="code" header="Code" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.code}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by code"/>
                </template>
            </Column>
            <Column field="name" header="Name" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.name}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by name"/>
                </template>
            </Column>
            <Column field="category" header="Category" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.category}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by name"/>
                </template>
            </Column>
            <Column field="quantity" header="Quantity" style="min-width: 12rem">
                <template #body="{ data }">
                    {{data.quantity}}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()"
                               placeholder="Search by name"/>
                </template>
            </Column>
        </DataTable>
    </main>
</template>
