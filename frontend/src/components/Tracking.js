import { useState } from 'react';
import { get_tracking, create_tracking } from '../api';

function Tracking({ role }) {
  const [order_id, set_order_id] = useState('');
  const [tracking, set_tracking] = useState(null);
  const [loading, set_loading] = useState(false);
  const [error, set_error] = useState(null);

  const [create_order_id, set_create_order_id] = useState('');
  const [location, set_location] = useState('');
  const [eta, set_eta] = useState('');
  const [submitting, set_submitting] = useState(false);
  const [create_error, set_create_error] = useState(null);
  const [create_success, set_create_success] = useState(null);

  async function handle_search(e) {
    e.preventDefault();
    if (!order_id.trim()) return;

    set_loading(true);
    set_error(null);
    set_tracking(null);

    try {
      const data = await get_tracking(order_id.trim());
      set_tracking(data);
    } catch (err) {
      set_error(err.message);
    } finally {
      set_loading(false);
    }
  }

  async function handle_create(e) {
    e.preventDefault();
    if (!create_order_id.trim() || !location.trim()) return;

    set_submitting(true);
    set_create_error(null);
    set_create_success(null);

    try {
      const data = await create_tracking({
        order_id: create_order_id.trim(),
        location: location.trim(),
        ...(eta && { eta }),
      });
      set_create_success(`Tracking created for order ${data.order_id}.`);
      set_create_order_id('');
      set_location('');
      set_eta('');
    } catch (err) {
      set_create_error(err.message);
    } finally {
      set_submitting(false);
    }
  }

  return (
    <div className="section-container">
      <h1 className="section-heading">Track Your Order</h1>

      <form className="track-form" onSubmit={handle_search}>
        <div className="track-input-row">
          <input
            type="text"
            className="track-input"
            value={order_id}
            onChange={(e) => set_order_id(e.target.value)}
            placeholder="Enter Order ID (e.g. ORD001)"
          />
          <button className="primary-btn" type="submit" disabled={loading || !order_id.trim()}>
            {loading ? 'Searching…' : 'Track'}
          </button>
        </div>
      </form>

      {loading && <div className="loading-state">Looking up tracking info…</div>}
      {error && <div className="error-state">{error}</div>}

      {tracking && (
        <div className="tracking-card">
          <div className="tracking-header">
            <h2 className="tracking-title">Order {tracking.order_id}</h2>
          </div>

          <div className="tracking-status-row">
            <div className="tracking-location-block">
              <span className="tracking-label">Current Location</span>
              <span className="tracking-value">{tracking.location}</span>
            </div>
            <div className="tracking-updated-block">
              <span className="tracking-label">Last Updated</span>
              <span className="tracking-value">
                {new Date(tracking.updated_at).toLocaleString()}
              </span>
            </div>
          </div>

          {tracking.eta && (
            <div className="estimated-delivery">
              <span className="delivery-label">Estimated Delivery</span>
              <span className="delivery-date">
                {new Date(tracking.eta).toLocaleDateString(undefined, {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
            </div>
          )}
        </div>
      )}

      {role === 'admin' && (
        <>
          <div className="divider" />

          <h2 className="section-subheading">Create Tracking Entry</h2>

          <form className="create-form" onSubmit={handle_create}>
            <div className="form-group">
              <label className="form-label">Order ID</label>
              <input
                className="form-input"
                type="text"
                value={create_order_id}
                onChange={(e) => set_create_order_id(e.target.value)}
                placeholder="e.g. ORD001"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Current Location</label>
              <input
                className="form-input"
                type="text"
                value={location}
                onChange={(e) => set_location(e.target.value)}
                placeholder="e.g. Mumbai Warehouse"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Estimated Delivery <span className="form-hint">(optional)</span></label>
              <input
                className="form-input"
                type="date"
                value={eta}
                onChange={(e) => set_eta(e.target.value)}
              />
            </div>

            {create_error && <div className="error-state">{create_error}</div>}
            {create_success && <div className="success-state">{create_success}</div>}

            <div className="form-actions">
              <button className="primary-btn" type="submit" disabled={submitting}>
                {submitting ? 'Creating…' : 'Create Tracking'}
              </button>
            </div>
          </form>
        </>
      )}
    </div>
  );
}

export default Tracking;
