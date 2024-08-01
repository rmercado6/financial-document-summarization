import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/history',
            name: 'history',
            component: () => import('../views/ExperimentListView.vue')
        },
        {
            path: '/document/:document_id',
            name: 'document',
            props: true,
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/DocumentView.vue')
        },
        {
            path: '/experiment/:uuid',
            name: 'experiment',
            props: true,
            component: () => import('../views/ExperimentView.vue')
        },
        {
            path: '/query/response',
            name: 'query_response',
            component: () => import('../views/QueryResponseView.vue'),
            beforeEnter: (to, from) => {
                if (from.name === 'experiment'){
                    return false
                }
            }
        }
    ]
})

export default router
