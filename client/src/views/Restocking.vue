<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">{{ t('restocking.budget') }}</h3>
      </div>
      <div class="budget-control">
        <div class="budget-amount">{{ formatMoney(budget) }}</div>
        <input
          type="range"
          class="budget-slider"
          :min="0"
          :max="200000"
          :step="1000"
          v-model.number="budget"
        />
        <p class="budget-help">{{ t('restocking.budgetHelp') }}</p>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card info">
        <div class="stat-label">{{ t('restocking.allocated') }}</div>
        <div class="stat-value">{{ formatMoney(recommendation ? recommendation.total_cost : 0) }}</div>
      </div>
      <div class="stat-card success">
        <div class="stat-label">{{ t('restocking.remaining') }}</div>
        <div class="stat-value">{{ formatMoney(recommendation ? recommendation.remaining_budget : budget) }}</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-label">{{ t('restocking.itemsRecommended') }}</div>
        <div class="stat-value">{{ recommendation ? recommendation.item_count : 0 }}</div>
      </div>
    </div>

    <div v-if="placedOrder" class="success-banner">
      <span>
        {{ t('restocking.orderPlaced', { orderNumber: placedOrder.order_number, date: formatDate(placedOrder.expected_delivery) }) }}
      </span>
      <router-link to="/orders" class="success-link">{{ t('restocking.viewInOrders') }}</router-link>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">{{ t('restocking.recommendations') }}</h3>
        <button
          class="place-order-btn"
          :disabled="!hasItems || submitting"
          @click="placeOrder"
        >
          {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
        </button>
      </div>

      <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="!hasItems" class="empty-text">{{ t('restocking.noRecommendations') }}</div>
      <div v-else class="table-container">
        <table class="restock-table">
          <thead>
            <tr>
              <th>{{ t('restocking.table.sku') }}</th>
              <th>{{ t('restocking.table.itemName') }}</th>
              <th>{{ t('restocking.table.trend') }}</th>
              <th>{{ t('restocking.table.unitCost') }}</th>
              <th>{{ t('restocking.table.demandGap') }}</th>
              <th>{{ t('restocking.table.quantity') }}</th>
              <th>{{ t('restocking.table.lineCost') }}</th>
              <th>{{ t('restocking.table.leadTime') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in recommendation.items" :key="item.item_sku">
              <td><strong>{{ item.item_sku }}</strong></td>
              <td>{{ translateProductName(item.item_name) }}</td>
              <td>
                <span :class="['badge', item.trend]">{{ t('trends.' + item.trend) }}</span>
              </td>
              <td>{{ formatMoney(item.unit_cost) }}</td>
              <td>{{ item.demand_gap.toLocaleString() }}</td>
              <td>
                {{ item.recommended_quantity.toLocaleString() }}
                <span v-if="item.fully_funded === false" class="partial-tag">{{ t('restocking.partial') }}</span>
              </td>
              <td>{{ formatMoney(item.line_cost) }}</td>
              <td>{{ t('orders.leadTimeDays', { days: item.lead_time_days }) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentLocale, currentCurrency, translateProductName } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })

    const budget = ref(50000)
    const recommendation = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const submitting = ref(false)
    const placedOrder = ref(null)

    const hasItems = computed(() => {
      return !!recommendation.value && recommendation.value.items.length > 0
    })

    const formatMoney = (value) => {
      const num = Number(value) || 0
      return `${currencySymbol.value}${num.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
    }

    const formatDate = (dateString) => {
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return dateString
      return date.toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const loadRecommendations = async () => {
      try {
        loading.value = true
        error.value = null
        recommendation.value = await api.getRestockRecommendations(budget.value)
      } catch (err) {
        error.value = 'Failed to load recommendations: ' + err.message
      } finally {
        loading.value = false
      }
    }

    let debounceTimer = null
    watch(budget, () => {
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        loadRecommendations()
      }, 300)
    })

    const placeOrder = async () => {
      try {
        submitting.value = true
        error.value = null
        const order = await api.createSubmittedOrder(budget.value)
        placedOrder.value = order
        await loadRecommendations()
      } catch (err) {
        error.value = 'Failed to place order: ' + err.message
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadRecommendations)

    return {
      t,
      budget,
      recommendation,
      loading,
      error,
      submitting,
      placedOrder,
      hasItems,
      formatMoney,
      formatDate,
      placeOrder,
      currencySymbol,
      translateProductName
    }
  }
}
</script>

<style scoped>
.budget-control {
  padding: 0.5rem 0.25rem;
}

.budget-amount {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 1rem;
}

.budget-slider {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: #e2e8f0;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #0f172a;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  cursor: pointer;
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #0f172a;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  cursor: pointer;
}

.budget-help {
  margin-top: 0.75rem;
  font-size: 0.813rem;
  color: #64748b;
}

.place-order-btn {
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  border: 1px solid #0f172a;
  background: #0f172a;
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1e293b;
}

.place-order-btn:disabled {
  background: #cbd5e1;
  border-color: #cbd5e1;
  cursor: not-allowed;
}

.success-banner {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  background: #d1fae5;
  border: 1px solid #6ee7b7;
  color: #065f46;
  padding: 0.875rem 1.25rem;
  border-radius: 10px;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}

.success-link {
  color: #065f46;
  font-weight: 600;
  text-decoration: underline;
}

.restock-table {
  width: 100%;
}

.empty-text {
  padding: 1.5rem 0.25rem;
  color: #64748b;
  font-size: 0.875rem;
}

.partial-tag {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.125rem 0.5rem;
  border-radius: 6px;
  background: #fed7aa;
  color: #92400e;
  font-size: 0.688rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}
</style>
