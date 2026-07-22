import { useState, useEffect, useRef } from 'react';
import { get_notifications, mark_notification_read } from '../api';

function Notifications() {
  const [notifications, set_notifications] = useState([]);
  const [open, set_open] = useState(false);
  const wrapper_ref = useRef(null);

  function load() {
    get_notifications()
      .then(set_notifications)
      .catch(() => {});
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!open) return;
    function on_outside_click(e) {
      if (wrapper_ref.current && !wrapper_ref.current.contains(e.target)) {
        set_open(false);
      }
    }
    document.addEventListener('mousedown', on_outside_click);
    return () => document.removeEventListener('mousedown', on_outside_click);
  }, [open]);

  async function handle_mark_read(e, id) {
    e.stopPropagation();
    try {
      const updated = await mark_notification_read(id);
      set_notifications(prev => prev.map(n => n.id === id ? updated : n));
    } catch {}
  }

  const unread_count = notifications.filter(n => !n.is_read).length;

  return (
    <div className="notif-wrapper" ref={wrapper_ref}>
      <button className="notif-bell" onClick={() => set_open(!open)} aria-label="Notifications">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
        {unread_count > 0 && (
          <span className="notif-badge">{unread_count > 99 ? '99+' : unread_count}</span>
        )}
      </button>

      {open && (
        <div className="notif-panel">
          <div className="notif-panel-header">
            <span className="notif-panel-title">Notifications</span>
            {unread_count > 0 && <span className="notif-new-count">{unread_count} new</span>}
          </div>

          {notifications.length === 0 ? (
            <div className="notif-empty">No notifications yet</div>
          ) : (
            <ul className="notif-list">
              {notifications.map(n => (
                <li key={n.id} className={`notif-item${n.is_read ? ' is-read' : ''}`}>
                  {!n.is_read && <span className="notif-dot" />}
                  <div className="notif-body">
                    <p className="notif-msg">{n.message}</p>
                    <div className="notif-footer">
                      <span className="notif-time">
                        {new Date(n.created_at).toLocaleString()}
                      </span>
                      {!n.is_read && (
                        <button className="notif-mark-btn" onClick={(e) => handle_mark_read(e, n.id)}>
                          Mark as read
                        </button>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default Notifications;
