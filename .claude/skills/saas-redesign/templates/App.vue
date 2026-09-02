<!--
  TEMPLATE — client/src/App.vue  (sidebar shell)
  Reference for vue-expert. RECONCILE against the live App.vue before applying:
  the <script> below must keep ALL existing task/modal logic verbatim — only the
  sidebar state (sidebarCollapsed / sidebarOpen) is new. The <style> block is the
  full global stylesheet: tokens + shell + restyled shared primitives.
-->
<template>
  <div
    class="app-shell"
    :class="{ 'sidebar-collapsed': sidebarCollapsed, 'sidebar-open': sidebarOpen }"
    @keydown.esc="sidebarOpen = false"
  >
    <AppSidebar
      :collapsed="sidebarCollapsed"
      :open="sidebarOpen"
      @toggle-collapse="toggleCollapse"
      @close="sidebarOpen = false"
    />

    <div class="app-main">
      <header class="app-topbar">
        <button
          type="button"
          class="topbar-hamburger"
          :aria-label="t('nav.openMenu')"
          @click="sidebarOpen = true"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" aria-hidden="true">
            <path d="M4 7h16M4 12h16M4 17h16" />
          </svg>
        </button>

        <div class="topbar-spacer"></div>

        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
      </header>

      <FilterBar />

      <main class="app-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import AppSidebar from './components/AppSidebar.vue'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

const SIDEBAR_KEY = 'sidebar-collapsed'

export default {
  name: 'App',
  components: {
    AppSidebar,
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()

    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // --- Sidebar state (new) ------------------------------------------------
    const sidebarCollapsed = ref(localStorage.getItem(SIDEBAR_KEY) === '1')
    const sidebarOpen = ref(false)

    const toggleCollapse = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
      localStorage.setItem(SIDEBAR_KEY, sidebarCollapsed.value ? '1' : '0')
    }

    // Close the mobile drawer whenever the route changes.
    watch(() => route.path, () => { sidebarOpen.value = false })

    // --- Tasks (unchanged from the original App.vue) ----------------------
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)
        if (isMockTask) {
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)
        if (mockTask) {
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask,
      sidebarCollapsed,
      sidebarOpen,
      toggleCollapse
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* ============================================================
   DESIGN TOKENS
   ============================================================ */
:root {
  --accent: #4f46e5;
  --accent-hover: #4338ca;
  --accent-pressed: #3730a3;
  --accent-subtle: #eef2ff;
  --accent-border: #c7d2fe;

  --bg-app: #f6f7f9;
  --bg-surface: #ffffff;
  --bg-subtle: #f2f4f7;
  --bg-hover: #f9fafb;

  --sidebar-bg: #0d1117;
  --sidebar-fg: #c9d1d9;
  --sidebar-fg-muted: #8b949e;
  --sidebar-active-bg: rgba(99, 102, 241, 0.16);
  --sidebar-active-fg: #ffffff;
  --sidebar-border: #21262d;

  --text-primary: #101828;
  --text-secondary: #475467;
  --text-tertiary: #667085;
  --text-inverse: #ffffff;

  --border: #e4e7ec;
  --border-strong: #d0d5dd;

  --success-fg: #067647;  --success-bg: #ecfdf3;
  --warning-fg: #b54708;  --warning-bg: #fffaeb;
  --danger-fg:  #b42318;  --danger-bg:  #fef3f2;
  --info-fg:    #175cd3;  --info-bg:    #eff8ff;

  --space-1: 0.25rem;  --space-2: 0.5rem;  --space-3: 0.75rem;
  --space-4: 1rem;      --space-5: 1.25rem; --space-6: 1.5rem;
  --space-8: 2rem;      --space-10: 2.5rem; --space-12: 3rem;

  --radius-sm: 6px; --radius-md: 8px; --radius-lg: 12px;
  --radius-xl: 16px; --radius-full: 999px;

  --shadow-xs: 0 1px 2px rgba(16, 24, 40, 0.05);
  --shadow-sm: 0 1px 3px rgba(16, 24, 40, 0.10), 0 1px 2px rgba(16, 24, 40, 0.06);
  --shadow-md: 0 4px 8px -2px rgba(16, 24, 40, 0.10), 0 2px 4px -2px rgba(16, 24, 40, 0.06);
  --shadow-lg: 0 12px 16px -4px rgba(16, 24, 40, 0.08), 0 4px 6px -2px rgba(16, 24, 40, 0.03);

  --sidebar-w: 264px;
  --sidebar-w-collapsed: 76px;
  --topbar-h: 60px;
  --content-max: 1440px;

  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

body {
  font-family: var(--font-sans);
  background: var(--bg-app);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ============================================================
   APP SHELL
   ============================================================ */
.app-shell {
  --sidebar-w: 264px;
  min-height: 100vh;
}

.app-shell.sidebar-collapsed {
  --sidebar-w: var(--sidebar-w-collapsed);
}

.app-main {
  margin-left: var(--sidebar-w);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left 0.18s ease;
}

.app-topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  height: var(--topbar-h);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0 var(--space-8);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
}

.topbar-spacer {
  flex: 1;
}

.topbar-hamburger {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  color: var(--text-secondary);
  cursor: pointer;
}

.topbar-hamburger svg {
  width: 20px;
  height: 20px;
}

.app-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  margin: 0 auto;
  padding: var(--space-6) var(--space-8);
}

@media (max-width: 1024px) {
  .app-shell { --sidebar-w: 0px; }
  .app-main { margin-left: 0; }
  .topbar-hamburger { display: flex; }
  .app-topbar { padding: 0 var(--space-4); }
  .app-content { padding: var(--space-5) var(--space-4); }
}

/* ============================================================
   PAGE HEADER
   ============================================================ */
.page-header {
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: 1.5rem;
  line-height: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-1);
  letter-spacing: -0.02em;
}

.page-header p {
  color: var(--text-secondary);
  font-size: 0.9375rem;
}

/* ============================================================
   STATS
   ============================================================ */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--bg-surface);
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.stat-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-sm);
}

.stat-label {
  color: var(--text-tertiary);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: var(--space-2);
}

.stat-value {
  font-size: 1.75rem;
  line-height: 2.25rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.stat-card.info .stat-value { color: var(--info-fg); }
.stat-card.success .stat-value { color: var(--success-fg); }
.stat-card.warning .stat-value { color: var(--warning-fg); }
.stat-card.danger .stat-value { color: var(--danger-fg); }

/* ============================================================
   CARD
   ============================================================ */
.card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
  margin-bottom: var(--space-6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-size: 1.0625rem;
  line-height: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

/* ============================================================
   TABLE
   ============================================================ */
.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--bg-subtle);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

th {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  font-weight: 600;
  color: var(--text-tertiary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

td {
  padding: var(--space-2) var(--space-3);
  border-top: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.875rem;
}

tbody tr {
  transition: background-color 0.15s ease;
}

tbody tr:hover {
  background: var(--bg-hover);
}

/* ============================================================
   BADGES
   ============================================================ */
.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.badge.success,
.badge.increasing { background: var(--success-bg); color: var(--success-fg); }

.badge.warning,
.badge.medium { background: var(--warning-bg); color: var(--warning-fg); }

.badge.danger,
.badge.decreasing,
.badge.high { background: var(--danger-bg); color: var(--danger-fg); }

.badge.info,
.badge.stable,
.badge.low { background: var(--info-bg); color: var(--info-fg); }

/* ============================================================
   STATES
   ============================================================ */
.loading {
  text-align: center;
  padding: var(--space-12);
  color: var(--text-tertiary);
  font-size: 0.9375rem;
}

.error {
  background: var(--danger-bg);
  border: 1px solid var(--danger-fg);
  color: var(--danger-fg);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: 0.9375rem;
}
</style>
