import { useState, useEffect } from 'react';
import { get_orders, get_order, create_order, register } from '../api';

function StatusBadge({ status }) {
  return <span className={`status-badge status-${status?.toLowerCase()}`}>{status}</span>;
}

function OrderDetail({ order_id, on_back }) {
  const [order, set_order] = useState(null);
  const [loading, set_loading] = useState(true);
  const [error, set_error] = useState(null);

  useEffect(() => {
    set_loading(true);
    set_error(null);
    get_order(order_id)
      .then(set_order)
      .catch((err) => set_error(err.message))
      .finally(() => set_loading(false));
  }, [order_id]);

  if (loading) return <div className="loading-state">Loading order details…</div>;
  if (error) return (
    <div>
      <button className="back-btn" onClick={on_back}>← Back to Orders</button>
      <div className="error-state">{error}</div>
    </div>
  );
  if (!order) return null;

  const total_rupees = (order.total / 100).toFixed(2);

  return (
    <div className="order-detail">
      <button className="back-btn" onClick={on_back}>← Back to Orders</button>

      <div className="detail-card">
        <div className="detail-header">
          <div>
            <h2 className="detail-title">Order {order.id}</h2>
            <p className="detail-meta">Customer: {order.customer}</p>
          </div>
          <StatusBadge status={order.status} />
        </div>

        {order.created_at && (
          <p className="detail-date">Placed on {new Date(order.created_at).toLocaleDateString()}</p>
        )}

        {order.items && order.items.length > 0 && (
          <div className="detail-section">
            <h3 className="section-title">Items</h3>
            <ul className="items-list">
              {order.items.map((item, i) => (
                <li key={i} className="item-row">{item}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="detail-total">
          <span>Total</span>
          <span className="total-amount">₹{total_rupees}</span>
        </div>
      </div>
    </div>
  );
}

function CreateOrderForm({ on_created, on_cancel }) {
  const [customer, set_customer] = useState('');
  const [items_input, set_items_input] = useState('');
  const [total, set_total] = useState('');
  const [temp_password, set_temp_password] = useState('');
  const [new_customer, set_new_customer] = useState(false);
  const [submitting, set_submitting] = useState(false);
  const [error, set_error] = useState(null);

  async function place_order() {
    const items = items_input.split(',').map((s) => s.trim()).filter(Boolean);
    return create_order({
      customer: customer.trim(),
      items,
      total: Math.round(parseFloat(total) * 100),
      status: 'pending',
    });
  }

  async function handle_submit(e) {
    e.preventDefault();
    set_submitting(true);
    set_error(null);

    try {
      if (new_customer) {
        await register(customer.trim(), temp_password);
      }
      const order = await place_order();
      on_created(order);
    } catch (err) {
      if (err.status === 404) {
        set_new_customer(true);
      } else {
        set_error(err.message);
      }
    } finally {
      set_submitting(false);
    }
  }

  return (
    <div className="section-container">
      <button className="back-btn" onClick={on_cancel}>← Back to Orders</button>
      <h1 className="section-heading">Place New Order</h1>

      <form className="create-form" onSubmit={handle_submit}>
        <div className="form-group">
          <label className="form-label">Customer Email</label>
          <input
            className="form-input"
            type="email"
            value={customer}
            onChange={(e) => { set_customer(e.target.value); set_new_customer(false); set_error(null); }}
            placeholder="e.g. customer@example.com"
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Items <span className="form-hint">(comma-separated)</span></label>
          <input
            className="form-input"
            type="text"
            value={items_input}
            onChange={(e) => set_items_input(e.target.value)}
            placeholder="e.g. Shirt, Pants, Shoes"
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Total (₹)</label>
          <input
            className="form-input"
            type="number"
            min="0"
            step="0.01"
            value={total}
            onChange={(e) => set_total(e.target.value)}
            placeholder="e.g. 1299.00"
            required
          />
        </div>

        {new_customer && (
          <div className="new-customer-notice">
            <p className="new-customer-msg">
              No account found for <strong>{customer}</strong>. Set a temporary password to create their account and place the order.
            </p>
            <div className="form-group">
              <label className="form-label">Temporary Password</label>
              <input
                className="form-input"
                type="password"
                value={temp_password}
                onChange={(e) => set_temp_password(e.target.value)}
                placeholder="Min. 8 characters"
                required
                autoFocus
              />
            </div>
          </div>
        )}

        {error && <div className="error-state">{error}</div>}

        <div className="form-actions">
          <button className="secondary-btn" type="button" onClick={on_cancel} disabled={submitting}>
            Cancel
          </button>
          <button className="primary-btn" type="submit" disabled={submitting}>
            {submitting
              ? (new_customer ? 'Creating & Placing…' : 'Placing…')
              : (new_customer ? 'Create Account & Place Order' : 'Place Order')}
          </button>
        </div>
      </form>
    </div>
  );
}

function Orders({ role }) {
  const [orders, set_orders] = useState([]);
  const [loading, set_loading] = useState(true);
  const [error, set_error] = useState(null);
  const [selected_order_id, set_selected_order_id] = useState(null);
  const [show_create, set_show_create] = useState(false);
  const [success_msg, set_success_msg] = useState(null);

  function load_orders() {
    set_loading(true);
    set_error(null);
    get_orders()
      .then(set_orders)
      .catch((err) => set_error(err.message))
      .finally(() => set_loading(false));
  }

  useEffect(() => {
    load_orders();
  }, []);

  if (selected_order_id) {
    return (
      <OrderDetail
        order_id={selected_order_id}
        on_back={() => set_selected_order_id(null)}
      />
    );
  }

  if (show_create) {
    return (
      <CreateOrderForm
        on_cancel={() => set_show_create(false)}
        on_created={(order) => {
          set_show_create(false);
          set_success_msg(`Order ${order.id} placed successfully!`);
          load_orders();
        }}
      />
    );
  }

  return (
    <div className="section-container">
      <div className="section-header-row">
        <h1 className="section-heading">My Orders</h1>
        {role === 'admin' && (
          <button className="primary-btn" onClick={() => { set_success_msg(null); set_show_create(true); }}>
            + New Order
          </button>
        )}
      </div>

      {success_msg && <div className="success-state">{success_msg}</div>}
      {loading && <div className="loading-state">Loading your orders…</div>}
      {error && <div className="error-state">{error}</div>}

      {!loading && !error && orders.length === 0 && (
        <div className="empty-state">You haven't placed any orders yet.</div>
      )}

      {!loading && !error && orders.length > 0 && (
        <div className="orders-grid">
          {orders.map((order) => (
            <button
              key={order.id}
              className="order-card"
              onClick={() => set_selected_order_id(order.id)}
            >
              <div className="order-card-top">
                <span className="order-number">{order.id}</span>
                <StatusBadge status={order.status} />
              </div>
              <p className="order-date">
                {new Date(order.created_at).toLocaleDateString()}
              </p>
              <p className="order-items">
                {order.items.slice(0, 2).join(', ')}
                {order.items.length > 2 && ` +${order.items.length - 2} more`}
              </p>
              <p className="order-total">₹{(order.total / 100).toFixed(2)}</p>
              <span className="order-link">View details →</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default Orders;
