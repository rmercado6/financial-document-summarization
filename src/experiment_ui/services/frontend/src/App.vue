<script setup>
</script>

<template>
    <div class="flex flex-col h-full w-full rounded-3xl bg-white shadow-lg shadow-slate-400 border border-slate-400 overflow-y-hidden overflow-x-hidden">
        <header class="border-b border-slate-200 px-3 py-4 bg-slate-50">
            <div class="wrapper">
                <nav class="flex gap-3">
                    <h1 class="flex-grow text-3xl text-blue-900">LLM Summarization Experiment Tracker</h1>
                    <RouterLink to="/">
                        <div class="router_link">
                            <div class="icon">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                     strokeWidth={1.5} stroke="currentColor" className="size-6">
                                    <path strokeLinecap="round" strokeLinejoin="round"
                                          d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0
                                          1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1
                                          1.5.124m7.5 10.376h3.375c.621 0
                                          1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0
                                          0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125
                                          1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0
                                          0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0
                                          0-3.375-3.375H9.75"/>
                                </svg>
                            </div>
                            Documents
                        </div>
                    </RouterLink>
                    <RouterLink to="/history">
                        <div class="router_link">
                            <div class="icon">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                     strokeWidth={1.5} stroke="currentColor" className="size-6">
                                    <path strokeLinecap="round" strokeLinejoin="round"
                                          d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
                                </svg>
                            </div>
                            History
                        </div>
                    </RouterLink>
                </nav>
            </div>
        </header>
        <RouterView/>
    </div>


</template>

<style scoped>
.router_link {
    @apply flex gap-1 text-slate-600 rounded-md p-2 font-light text-sm;
    @apply hover:text-blue-800 hover:bg-blue-100 hover:underline hover:cursor-pointer;
}

.router_link .icon {
    @apply w-5 h-5;
}
</style>
