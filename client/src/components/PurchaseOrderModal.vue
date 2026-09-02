<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ mode === 'view' ? 'Purchase Order Details' : 'Create Purchase Order' }}
            </h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="shortage-context">
              <div class="context-item">
                <span class="context-label">Item</span>
                <span class="context-value">{{ backlogItem.item_name }}</span>
              </div>
              <div class="context-item">
                <span class="context-label">SKU</span>
                <span class="context-value sku">{{ backlogItem.item_sku }}</span>
              </div>
              <div class="context-item">
                <span class="context-label">Shortage</span>
                <span class="context-value">{{ shortage }} units</span>
              </div>
            </div>

            <!-- View mode -->
            <template v-if="mode === 'view'">
              <div v-if="viewLoading" class="state-message">Loading purchase order...</div>
              <div v-else-if="viewError" class="state-message error-text">{{ viewError }}</div>
              <div v-else-if="purchaseOrder" class="info-grid">
                <div class="info-item">
                  <div class="info-label">PO Number</div>
                  <div class="info-value po-id">{{ purchaseOrder.id }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Status</div>
                  <div class="info-value">
                    <span class="badge">{{ purchaseOrder.status }}</span>
                  </div>
                </div>
                <div class="info-item">
                  <div class="info-label">Supplier</div>
                  <div class="info-value">{{ purchaseOrder.supplier_name }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Quantity</div>
                  <div class="info-value">{{ purchaseOrder.quantity }} units</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Unit Cost</div>
                  <div class="info-value">{{ formatCurrency(purchaseOrder.unit_cost) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Total Cost</div>
                  <div class="info-value">{{ formatCurrency(purchaseOrder.unit_cost * purchaseOrder.quantity) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Expected Delivery</div>
                  <div class="info-value">{{ formatDate(purchaseOrder.expected_delivery_date) }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Created</div>
                  <div class="info-value">{{ formatDate(purchaseOrder.created_date) }}</div>
                </div>
                <div class="info-item full-span">
                  <div class="info-label">Notes</div>
                  <div class="info-value">{{ purchaseOrder.notes || '—' }}</div>
                </div>
              </div>
            </template>

            <!-- Create mode -->
            <template v-else>
              <form class="po-form" @submit.prevent="submit">
                <div class="form-group">
                  <label for="po-supplier">Supplier Name</label>
                  <input
                    id="po-supplier"
                    v-model="form.supplier_name"
                    type="text"
                    class="form-input"
                    placeholder="e.g. Acme Components Ltd."
                    required
                  />
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label for="po-quantity">Quantity</label>
                    <input
                      id="po-quantity"
                      v-model.number="form.quantity"
                      type="number"
                      min="1"
                      class="form-input"
                      required
                    />
                  </div>

                  <div class="form-group">
                    <label for="po-unit-cost">Unit Cost</label>
                    <input
                      id="po-unit-cost"
                      v-model.number="form.unit_cost"
                      type="number"
                      min="0"
                      step="0.01"
                      class="form-input"
                      required
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label for="po-delivery">Expected Delivery Date</label>
                  <input
                    id="po-delivery"
                    v-model="form.expected_delivery_date"
                    type="date"
                    class="form-input"
                    required
                  />
                </div>

                <div class="form-group">
                  <label for="po-notes">Notes (optional)</label>
                  <textarea
                    id="po-notes"
                    v-model="form.notes"
                    class="form-input form-textarea"
                    rows="3"
                    placeholder="Additional details for this order"
                  ></textarea>
                </div>

                <div v-if="submitError" class="state-message error-text">{{ submitError }}</div>
              </form>
            </template>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="close">Close</button>
            <button
              v-if="mode !== 'view'"
              class="btn-primary"
              :disabled="submitting"
              @click="submit"
            >
              {{ submitting ? 'Creating...' : 'Create Purchase Order' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { api } from '../api'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  backlogItem: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'create'
  }
})

const emit = defineEmits(['close', 'po-created'])

const form = reactive({
  supplier_name: '',
  quantity: 0,
  unit_cost: 0,
  expected_delivery_date: '',
  notes: ''
})

const submitting = ref(false)
const submitError = ref(null)

const purchaseOrder = ref(null)
const viewLoading = ref(false)
const viewError = ref(null)

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return props.backlogItem.quantity_needed - props.backlogItem.quantity_available
})

const resetForm = () => {
  form.supplier_name = ''
  form.quantity = shortage.value > 0 ? shortage.value : 0
  form.unit_cost = 0
  form.expected_delivery_date = ''
  form.notes = ''
  submitting.value = false
  submitError.value = null
}

const loadPurchaseOrder = async () => {
  if (!props.backlogItem) return
  viewLoading.value = true
  viewError.value = null
  purchaseOrder.value = null
  try {
    purchaseOrder.value = await api.getPurchaseOrderByBacklogItem(props.backlogItem.id)
  } catch (err) {
    if (err.response?.status === 404) {
      viewError.value = 'No purchase order found for this shortage.'
    } else {
      viewError.value = err.response?.data?.detail || err.message
    }
  } finally {
    viewLoading.value = false
  }
}

watch(
  () => props.isOpen,
  (open) => {
    if (!open) return
    if (props.mode === 'view') {
      loadPurchaseOrder()
    } else {
      resetForm()
    }
  }
)

const close = () => {
  emit('close')
}

const submit = async () => {
  if (submitting.value) return
  submitError.value = null

  if (!form.supplier_name.trim()) {
    submitError.value = 'Supplier name is required.'
    return
  }
  if (!form.quantity || form.quantity <= 0) {
    submitError.value = 'Quantity must be greater than zero.'
    return
  }
  if (!form.expected_delivery_date) {
    submitError.value = 'Expected delivery date is required.'
    return
  }

  submitting.value = true
  try {
    const created = await api.createPurchaseOrder({
      backlog_item_id: props.backlogItem.id,
      supplier_name: form.supplier_name.trim(),
      quantity: form.quantity,
      unit_cost: form.unit_cost || 0,
      expected_delivery_date: form.expected_delivery_date,
      notes: form.notes.trim() || null
    })
    emit('po-created', created)
    emit('close')
  } catch (err) {
    submitError.value = err.response?.data?.detail || err.message
  } finally {
    submitting.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatCurrency = (value) => {
  const num = Number(value) || 0
  return num.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  max-width: 640px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.close-button {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.shortage-context {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  margin-bottom: 1.5rem;
}

.context-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.context-label {
  font-size: 0.688rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.context-value {
  font-size: 0.938rem;
  font-weight: 600;
  color: #0f172a;
}

.context-value.sku {
  font-family: 'Monaco', 'Courier New', monospace;
  color: #4f46e5;
}

.po-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.813rem;
  font-weight: 600;
  color: #334155;
}

.form-input {
  padding: 0.625rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.938rem;
  color: #0f172a;
  font-family: inherit;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.form-input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.form-textarea {
  resize: vertical;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.25rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.info-item.full-span {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.info-value {
  font-size: 0.938rem;
  color: #0f172a;
  font-weight: 500;
}

.info-value.po-id {
  font-family: 'Monaco', 'Courier New', monospace;
  color: #4f46e5;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
  background: #e0e7ff;
  color: #3730a3;
}

.state-message {
  padding: 1.5rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

.error-text {
  color: #dc2626;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: #4f46e5;
  border: 1px solid #4f46e5;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-primary:hover:not(:disabled) {
  background: #4338ca;
  border-color: #4338ca;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
