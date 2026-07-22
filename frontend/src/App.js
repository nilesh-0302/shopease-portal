import { useState } from 'react';
import './App.css';
import Navbar from './components/Navbar';
import Orders from './components/Orders';
import Tickets from './components/Tickets';
import Tracking from './components/Tracking';
import Products from './components/Products';
import Auth from './components/Auth';

function get_role(token) {
  try {
    return JSON.parse(atob(token.split('.')[1])).role;
  } catch {
    return null;
  }
}

function App() {
  const [token, set_token] = useState(() => localStorage.getItem('token'));
  const [active_tab, set_active_tab] = useState('shop');

  function handle_auth(access_token) {
    localStorage.setItem('token', access_token);
    set_token(access_token);
  }

  function handle_logout() {
    localStorage.removeItem('token');
    set_token(null);
  }

  if (!token) {
    return <Auth on_auth={handle_auth} />;
  }

  const role = get_role(token);

  return (
    <div className="app">
      <Navbar active_tab={active_tab} set_active_tab={set_active_tab} on_logout={handle_logout} role={role} />
      <main className="app-content">
        {active_tab === 'shop' && <Products role={role} />}
        {active_tab === 'orders' && <Orders role={role} />}
        {active_tab === 'tickets' && <Tickets />}
        {active_tab === 'tracking' && <Tracking role={role} />}
      </main>
    </div>
  );
}

export default App;
