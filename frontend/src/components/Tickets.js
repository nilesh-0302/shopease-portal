import { useState, useEffect } from 'react';
import { get_tickets, create_ticket } from '../api';

const EMPTY_FORM = { order_id: '', issue: '' };

function Tickets() {
  const [tickets, set_tickets] = useState([]);
  const [loading, set_loading] = useState(true);
  const [error, set_error] = useState(null);
  const [form, set_form] = useState(EMPTY_FORM);
  const [submitting, set_submitting] = useState(false);
  const [submit_error, set_submit_error] = useState(null);
  const [submit_success, set_submit_success] = useState(false);
  const [show_form, set_show_form] = useState(false);

  useEffect(() => {
    get_tickets()
      .then(set_tickets)
      .catch((err) => set_error(err.message))
      .finally(() => set_loading(false));
  }, []);

  function handle_change(e) {
    const { name, value } = e.target;
    set_form((prev) => ({ ...prev, [name]: value }));
  }

  async function handle_submit(e) {
    e.preventDefault();
    if (!form.order_id.trim() || !form.issue.trim()) return;

    set_submitting(true);
    set_submit_error(null);

    try {
      const new_ticket = await create_ticket(form);
      set_tickets((prev) => [new_ticket, ...prev]);
      set_form(EMPTY_FORM);
      set_submit_success(true);
      set_show_form(false);
      setTimeout(() => set_submit_success(false), 4000);
    } catch (err) {
      set_submit_error(err.message);
    } finally {
      set_submitting(false);
    }
  }

  return (
    <div className="section-container">
      <div className="section-header">
        <h1 className="section-heading">Support Tickets</h1>
        <button
          className="primary-btn"
          onClick={() => {
            set_show_form((v) => !v);
            set_submit_error(null);
          }}
        >
          {show_form ? 'Cancel' : '+ New Ticket'}
        </button>
      </div>

      {submit_success && (
        <div className="success-banner">
          Your ticket was submitted successfully. We'll get back to you soon!
        </div>
      )}

      {show_form && (
        <form className="ticket-form" onSubmit={handle_submit}>
          <h2 className="form-title">Create a Support Ticket</h2>

          <div className="form-group">
            <label htmlFor="order_id">Order ID *</label>
            <input
              id="order_id"
              name="order_id"
              type="text"
              value={form.order_id}
              onChange={handle_change}
              placeholder="e.g. ORD001"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="issue">Describe your issue *</label>
            <textarea
              id="issue"
              name="issue"
              value={form.issue}
              onChange={handle_change}
              placeholder="Tell us what went wrong and we'll help you out…"
              rows={5}
              required
            />
          </div>

          {submit_error && <div className="error-state">{submit_error}</div>}

          <button className="primary-btn" type="submit" disabled={submitting}>
            {submitting ? 'Submitting…' : 'Submit Ticket'}
          </button>
        </form>
      )}

      {loading && <div className="loading-state">Loading your tickets…</div>}
      {error && <div className="error-state">{error}</div>}

      {!loading && !error && tickets.length === 0 && (
        <div className="empty-state">No support tickets yet. Need help? Create one above.</div>
      )}

      {!loading && !error && tickets.length > 0 && (
        <div className="tickets-list">
          {tickets.map((ticket) => (
            <div key={ticket.id} className="ticket-item">
              <div className="ticket-top">
                <span className="ticket-subject">{ticket.id}</span>
                <span className={`status-badge status-${ticket.status?.toLowerCase().replace('-', '_')}`}>
                  {ticket.status}
                </span>
              </div>
              <p className="ticket-meta">Order: {ticket.order_id}</p>
              <p className="ticket-message">{ticket.issue}</p>
              {ticket.created_at && (
                <p className="ticket-date">
                  {new Date(ticket.created_at).toLocaleDateString()}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Tickets;
