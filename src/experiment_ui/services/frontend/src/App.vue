<script setup>
</script>

<template>
    <div class="flex flex-col h-full w-full bg-white overflow-y-hidden overflow-x-hidden">
        <header class="border-b border-slate-400 px-4 py-1 bg-slate-100 z-10">
            <nav class="flex">
                <h1 class="flex-grow text-xl text-slate-500 font-serif font-extrabold content-center">
                    LLM Summarization Experiment Tracker
                </h1>
                <RouterLink to="/">
                    <div class="router_link group relative">
                        <div class="icon">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                                <path
                                    d="M7.5 3.375c0-1.036.84-1.875 1.875-1.875h.375a3.75 3.75 0 0 1 3.75 3.75v1.875C13.5 8.161 14.34 9 15.375 9h1.875A3.75 3.75 0 0 1 21 12.75v3.375C21 17.16 20.16 18 19.125 18h-9.75A1.875 1.875 0 0 1 7.5 16.125V3.375Z"/>
                                <path
                                    d="M15 5.25a5.23 5.23 0 0 0-1.279-3.434 9.768 9.768 0 0 1 6.963 6.963A5.23 5.23 0 0 0 17.25 7.5h-1.875A.375.375 0 0 1 15 7.125V5.25ZM4.875 6H6v10.125A3.375 3.375 0 0 0 9.375 19.5H16.5v1.125c0 1.035-.84 1.875-1.875 1.875h-9.75A1.875 1.875 0 0 1 3 20.625V7.875C3 6.839 3.84 6 4.875 6Z"/>
                            </svg>
                        </div>
                        <span
                            class="absolute hidden group-hover:flex px-2 py-1 bg-slate-700 rounded-lg
                                   text-center text-white text-sm -bottom-6 right-0">
                            Documents
                        </span>

                    </div>
                </RouterLink>
                <RouterLink to="/history">
                    <div class="router_link group relative">
                        <div class="icon">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                                <path fill-rule="evenodd"
                                      d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 6a.75.75 0 0 0-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 0 0 0-1.5h-3.75V6Z"
                                      clip-rule="evenodd"/>
                            </svg>
                        </div>
                        <span
                            class="absolute hidden group-hover:flex px-2 py-1 bg-slate-700 rounded-lg
                                   text-center text-white text-sm -bottom-6 right-0">
                            History
                        </span>
                    </div>
                </RouterLink>
            </nav>
        </header>
        <RouterView/>
    </div>
</template>

<style scoped>
.router_link {
    @apply flex gap-1 text-slate-600 rounded-md p-2 font-light text-sm;
    @apply hover:text-blue-800 hover:bg-white hover:underline hover:cursor-pointer;
}

.router_link .icon {
    @apply w-5 h-5;
}
</style>
