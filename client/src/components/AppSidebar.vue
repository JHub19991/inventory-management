<template>
  <div class="sidebar-root">
    <div
      v-if="open"
      class="sidebar-backdrop"
      aria-hidden="true"
      @click="$emit('close')"
    ></div>

    <aside
      class="app-sidebar"
      :class="{ 'is-collapsed': collapsed, 'is-open': open }"
    >
      <div class="sidebar-brand">
        <div class="brand-mark">{{ brandInitials }}</div>
        <div v-if="!collapsed" class="brand-text">
          <span class="brand-name">{{ t('nav.companyName') }}</span>
          <span class="brand-sub">{{ t('nav.subtitle') }}</span>
        </div>
      </div>

      <nav class="sidebar-nav" aria-label="Primary">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          :class="{ active: isActive(item.to) }"
          :aria-current="isActive(item.to) ? 'page' : null"
          :title="collapsed ? t(item.labelKey) : null"
          @click="$emit('close')"
        >
          <svg
            class="nav-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path v-for="(d, i) in item.paths" :key="i" :d="d" />
          </svg>
          <span v-if="!collapsed" class="nav-label">{{ t(item.labelKey) }}</span>
        </router-link>
      </nav>

      <button
        type="button"
        class="sidebar-collapse"
        :aria-label="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        @click="$emit('toggle-collapse')"
      >
        <svg
          class="collapse-chevron"
          :class="{ flipped: collapsed }"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M15 6l-6 6 6 6" />
        </svg>
        <span v-if="!collapsed">{{ t('nav.collapseSidebar') }}</span>
      </button>
    </aside>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from '../composables/useI18n'

const navItems = [
  {
    to: '/',
    labelKey: 'nav.overview',
    paths: [
      'M3 3h7v7H3z', 'M14 3h7v7h-7z', 'M14 14h7v7h-7z', 'M3 14h7v7H3z'
    ]
  },
  {
    to: '/inventory',
    labelKey: 'nav.inventory',
    paths: [
      'M3 7l9-4 9 4-9 4-9-4z', 'M3 7v10l9 4 9-4V7', 'M12 11v10'
    ]
  },
  {
    to: '/orders',
    labelKey: 'nav.orders',
    paths: [
      'M6 4h12a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z',
      'M9 4V3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1', 'M8 11h8', 'M8 15h6'
    ]
  },
  {
    to: '/restocking',
    labelKey: 'nav.restocking',
    paths: [
      'M4 12a8 8 0 0 1 13.66-5.66L20 8', 'M20 4v4h-4',
      'M20 12a8 8 0 0 1-13.66 5.66L4 16', 'M4 20v-4h4'
    ]
  },
  {
    to: '/spending',
    labelKey: 'nav.finance',
    paths: [
      'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z', 'M12 7v10',
      'M14.5 9.3c0-1-1.1-1.6-2.5-1.6s-2.5.6-2.5 1.8S10.6 13 12 13s2.5.8 2.5 2-1.1 1.7-2.5 1.7-2.5-.7-2.5-1.6'
    ]
  },
  {
    to: '/demand',
    labelKey: 'nav.demandForecast',
    paths: [
      'M4 5v14', 'M4 19h16', 'M7 14l4-4 3 3 6-7'
    ]
  },
  {
    to: '/reports',
    labelKey: 'nav.reports',
    paths: [
      'M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z',
      'M14 3v5h5', 'M9 13h6', 'M9 17h6'
    ]
  }
]

export default {
  name: 'AppSidebar',
  props: {
    collapsed: { type: Boolean, default: false },
    open: { type: Boolean, default: false }
  },
  emits: ['close', 'toggle-collapse'],
  setup() {
    const route = useRoute()
    const { t } = useI18n()

    const isActive = (to) => {
      if (to === '/') return route.path === '/'
      return route.path.startsWith(to)
    }

    const brandInitials = computed(() => {
      const name = t('nav.companyName') || ''
      const initials = name
        .split(/\s+/)
        .filter(Boolean)
        .map((word) => word[0])
        .slice(0, 2)
        .join('')
      return (initials || name.slice(0, 2)).toUpperCase()
    })

    return { t, navItems, isActive, brandInitials }
  }
}
</script>

<style scoped>
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: 190;
}

.app-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: var(--sidebar-w);
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  z-index: 200;
  transition: width 0.18s ease, transform 0.2s ease;
  overflow: hidden;
}

/* Brand ---------------------------------------------------------------- */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-4);
  border-bottom: 1px solid var(--sidebar-border);
  min-height: var(--topbar-h);
}

.brand-mark {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.8125rem;
  letter-spacing: 0.02em;
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  color: #fff;
  font-weight: 600;
  font-size: 0.9375rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-sub {
  color: var(--sidebar-fg-muted);
  font-size: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Nav ----------------------------------------------------------------- */
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--space-4) var(--space-3);
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0.625rem var(--space-3);
  border-radius: var(--radius-md);
  color: var(--sidebar-fg);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  border-left: 3px solid transparent;
  transition: background 0.15s ease, color 0.15s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.nav-item.active {
  background: var(--sidebar-active-bg);
  color: var(--sidebar-active-fg);
  border-left-color: var(--accent);
}

.nav-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Collapse toggle --------------------------------------------------------- */
.sidebar-collapse {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: 0.75rem var(--space-4);
  background: none;
  border: none;
  border-top: 1px solid var(--sidebar-border);
  color: var(--sidebar-fg-muted);
  font: inherit;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.15s ease;
}

.sidebar-collapse:hover {
  color: #fff;
}

.collapse-chevron {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  transition: transform 0.18s ease;
}

.collapse-chevron.flipped {
  transform: rotate(180deg);
}

/* Collapsed rail -------------------------------------------------------- */
.app-sidebar.is-collapsed .sidebar-brand,
.app-sidebar.is-collapsed .nav-item,
.app-sidebar.is-collapsed .sidebar-collapse {
  justify-content: center;
}

.app-sidebar.is-collapsed .nav-item {
  padding-left: 0;
  padding-right: 0;
  border-left-width: 0;
}

.app-sidebar.is-collapsed .nav-item.active {
  background: var(--sidebar-active-bg);
  box-shadow: inset 3px 0 0 var(--accent);
}

.app-sidebar.is-collapsed .sidebar-brand {
  padding-left: 0;
  padding-right: 0;
}

/* Mobile drawer ------------------------------------------------------- */
@media (max-width: 1024px) {
  .app-sidebar {
    width: 264px;
    transform: translateX(-100%);
  }

  .app-sidebar.is-open {
    transform: none;
    box-shadow: var(--shadow-lg);
  }
}
</style>
