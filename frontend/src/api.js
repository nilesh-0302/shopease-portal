const BASE_URL = 'http://13.126.186.241:8000';

function auth_headers() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function login(email, password) {
  const body = new URLSearchParams({ username: email, password });
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });
  if (!response.ok) throw new Error('Invalid email or password');
  return response.json();
}

export async function register(email, password) {
  const response = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error('Registration failed. Email may already be in use.');
  return response.json();
}

export async function get_orders() {
  const response = await fetch(`${BASE_URL}/orders/`, {
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Failed to fetch orders');
  return response.json();
}

export async function get_order(id) {
  const response = await fetch(`${BASE_URL}/orders/${id}`, {
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Failed to fetch order details');
  return response.json();
}

export async function get_tickets() {
  const response = await fetch(`${BASE_URL}/tickets/`, {
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Failed to fetch tickets');
  return response.json();
}

export async function create_ticket(data) {
  const response = await fetch(`${BASE_URL}/tickets/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth_headers() },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create ticket');
  return response.json();
}

export async function get_tracking(order_id) {
  const response = await fetch(`${BASE_URL}/tracking/${order_id}`, {
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Tracking info not found for this order');
  return response.json();
}

export async function create_order(data) {
  const response = await fetch(`${BASE_URL}/orders/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth_headers() },
    body: JSON.stringify(data),
  });
  if (response.status === 404) {
    const err = new Error('customer_not_found');
    err.status = 404;
    throw err;
  }
  if (!response.ok) throw new Error('Failed to create order');
  return response.json();
}

export async function get_products() {
  const response = await fetch(`${BASE_URL}/products/`, {
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Failed to fetch products');
  return response.json();
}

export async function get_cart() {
  const response = await fetch(`${BASE_URL}/cart/`, {
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Failed to fetch cart');
  return response.json();
}

export async function add_to_cart(product_id, quantity = 1) {
  const response = await fetch(`${BASE_URL}/cart/items/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth_headers() },
    body: JSON.stringify({ product_id, quantity }),
  });
  if (!response.ok) throw new Error('Failed to add item to cart');
  return response.json();
}

export async function remove_from_cart(product_id) {
  const response = await fetch(`${BASE_URL}/cart/items/${product_id}`, {
    method: 'DELETE',
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Failed to remove item from cart');
}

export async function checkout_cart() {
  const response = await fetch(`${BASE_URL}/cart/checkout/`, {
    method: 'POST',
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Checkout failed. Please check stock availability.');
  return response.json();
}

export async function get_profile() {
  const response = await fetch(`${BASE_URL}/customer_profile/`, {
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Failed to fetch profile');
  return response.json();
}

export async function forgot_password(email) {
  const response = await fetch(`${BASE_URL}/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  if (!response.ok) throw new Error('No account found with that email');
  return response.json();
}

export async function reset_password(token, new_password) {
  const response = await fetch(`${BASE_URL}/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password }),
  });
  if (!response.ok) throw new Error('Invalid or expired reset token');
  return response.json();
}

export async function get_notifications() {
  const response = await fetch(`${BASE_URL}/notifications/`, {
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Failed to fetch notifications');
  return response.json();
}

export async function mark_notification_read(notif_id) {
  const response = await fetch(`${BASE_URL}/notifications/${notif_id}/read`, {
    method: 'PUT',
    headers: auth_headers(),
  });
  if (!response.ok) throw new Error('Failed to mark notification as read');
  return response.json();
}

export async function create_tracking(data) {
  const response = await fetch(`${BASE_URL}/tracking/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth_headers() },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create tracking entry');
  return response.json();
}
