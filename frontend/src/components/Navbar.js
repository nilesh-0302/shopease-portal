import Notifications from './Notifications';
import UserProfile from './UserProfile';

function Navbar({ active_tab, set_active_tab, on_logout, role }) {
  const tabs = [
    { id: 'shop', label: 'Shop' },
    { id: 'orders', label: 'My Orders' },
    { id: 'tickets', label: 'Support Tickets' },
    { id: 'tracking', label: 'Track Order' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-brand">
          <span className="brand-icon">🛍</span>
          <span className="brand-name">ShopEase</span>
        </div>
        <div className="navbar-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-btn${active_tab === tab.id ? ' active' : ''}`}
              onClick={() => set_active_tab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="navbar-actions">
          {role === 'admin' && <Notifications />}
          <UserProfile />
          <button className="logout-btn" onClick={on_logout}>Sign Out</button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
