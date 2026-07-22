import { useState, useEffect, useCallback } from 'react';
import { get_products, get_cart, add_to_cart, remove_from_cart, checkout_cart } from '../api';

function ProductCard({ product, cart_qty, on_add, on_decrease, is_customer, busy }) {
  const out_of_stock = product.stock === 0;
  const in_cart = cart_qty > 0;
  const price = (product.price / 100).toFixed(2);

  return (
    <div className={`product-card${out_of_stock ? ' out-of-stock' : ''}`}>
      <span className="product-category-tag">{product.category}</span>
      <h3 className="product-name">{product.name}</h3>
      {product.description && (
        <p className="product-desc">{product.description}</p>
      )}
      <div className="product-footer">
        <div className="product-price-row">
          <span className="product-price">₹{price}</span>
          <span className={`product-stock ${out_of_stock ? 'stock-out' : product.stock <= 5 ? 'stock-low' : 'stock-ok'}`}>
            {out_of_stock ? 'Out of stock' : product.stock <= 5 ? `Only ${product.stock} left` : `${product.stock} in stock`}
          </span>
        </div>
        {is_customer && (
          out_of_stock ? (
            <button className="cart-action-btn disabled" disabled>Out of Stock</button>
          ) : in_cart ? (
            <div className="cart-qty-row">
              <button className="qty-decrease-btn" onClick={on_decrease} disabled={busy || cart_qty <= 1} title="Decrease quantity">−</button>
              <span className="qty-label">In cart: {cart_qty}</span>
              <button className="qty-add-btn" onClick={on_add} disabled={busy || cart_qty >= product.stock}>+</button>
            </div>
          ) : (
            <button className="cart-action-btn add-btn" onClick={on_add} disabled={busy}>
              {busy ? 'Adding…' : 'Add to Cart'}
            </button>
          )
        )}
      </div>
    </div>
  );
}

function OrderSuccessModal({ order_id, on_close }) {
  return (
    <>
      <div className="modal-backdrop" onClick={on_close} />
      <div className="modal-box" role="dialog" aria-modal="true">
        <div className="modal-check-icon">&#10003;</div>
        <h2 className="modal-title">Order Placed!</h2>
        <p className="modal-order-id">Order {order_id} confirmed</p>
        <p className="modal-track-msg">You can track your order in the next 30–50 mins</p>
        <button className="primary-btn modal-ok-btn" onClick={on_close}>Got it</button>
      </div>
    </>
  );
}

function CartPanel({ cart, on_remove, on_checkout, on_close, checking_out, checkout_error }) {
  const item_count = cart.items.reduce((sum, i) => sum + i.quantity, 0);

  return (
    <>
      <div className="cart-backdrop" onClick={on_close} />
      <div className="cart-panel">
        <div className="cart-panel-header">
          <span className="cart-panel-title">Your Cart</span>
          {item_count > 0 && <span className="cart-item-count">{item_count} item{item_count !== 1 ? 's' : ''}</span>}
          <button className="cart-close-btn" onClick={on_close}>✕</button>
        </div>

        {cart.items.length === 0 ? (
          <div className="cart-empty">Your cart is empty</div>
        ) : (
          <>
            <ul className="cart-items-list">
              {cart.items.map((item) => (
                <li key={item.id} className="cart-item">
                  <div className="cart-item-info">
                    <p className="cart-item-name">{item.product_name}</p>
                    <p className="cart-item-meta">
                      ₹{(item.unit_price / 100).toFixed(2)} × {item.quantity}
                    </p>
                  </div>
                  <div className="cart-item-right">
                    <span className="cart-item-subtotal">₹{(item.subtotal / 100).toFixed(2)}</span>
                    <button
                      className="cart-remove-btn"
                      onClick={() => on_remove(item.product_id)}
                      title="Remove item"
                    >
                      🗑
                    </button>
                  </div>
                </li>
              ))}
            </ul>

            <div className="cart-panel-footer">
              <div className="cart-total-row">
                <span className="cart-total-label">Total</span>
                <span className="cart-total-amount">₹{(cart.total / 100).toFixed(2)}</span>
              </div>
              {checkout_error && <div className="error-state" style={{ marginBottom: 12 }}>{checkout_error}</div>}
              <button
                className="primary-btn checkout-btn"
                onClick={on_checkout}
                disabled={checking_out}
              >
                {checking_out ? 'Placing Order…' : 'Checkout'}
              </button>
            </div>
          </>
        )}
      </div>
    </>
  );
}

function Products({ role }) {
  const [products, set_products] = useState([]);
  const [cart, set_cart] = useState({ items: [], total: 0 });
  const [loading, set_loading] = useState(true);
  const [error, set_error] = useState(null);
  const [cart_open, set_cart_open] = useState(false);
  const [active_category, set_active_category] = useState('All');
  const [busy, set_busy] = useState({});
  const [checking_out, set_checking_out] = useState(false);
  const [checkout_error, set_checkout_error] = useState(null);
  const [order_success, set_order_success] = useState(null);

  const is_customer = role === 'customer';

  const load_cart = useCallback(async () => {
    if (!is_customer) return;
    try {
      const data = await get_cart();
      set_cart(data);
    } catch {}
  }, [is_customer]);

  useEffect(() => {
    async function load() {
      set_loading(true);
      set_error(null);
      try {
        const prods = await get_products();
        set_products(prods);
        if (is_customer) await load_cart();
      } catch (err) {
        set_error(err.message);
      } finally {
        set_loading(false);
      }
    }
    load();
  }, [is_customer, load_cart]);

  const cart_qty_map = Object.fromEntries(
    cart.items.map((i) => [i.product_id, i.quantity])
  );

  const cart_count = cart.items.reduce((sum, i) => sum + i.quantity, 0);

  const categories = ['All', ...Array.from(new Set(products.map((p) => p.category))).sort()];

  const filtered = active_category === 'All'
    ? products
    : products.filter((p) => p.category === active_category);

  async function handle_add(product_id) {
    set_busy((b) => ({ ...b, [product_id]: true }));
    try {
      await add_to_cart(product_id);
      await load_cart();
    } catch {}
    set_busy((b) => ({ ...b, [product_id]: false }));
  }

  async function handle_decrease(product_id) {
    set_busy((b) => ({ ...b, [product_id]: true }));
    try {
      await add_to_cart(product_id, -1);
      await load_cart();
    } catch {}
    set_busy((b) => ({ ...b, [product_id]: false }));
  }

  async function handle_remove(product_id) {
    set_busy((b) => ({ ...b, [product_id]: true }));
    try {
      await remove_from_cart(product_id);
      await load_cart();
    } catch {}
    set_busy((b) => ({ ...b, [product_id]: false }));
  }

  async function handle_checkout() {
    set_checking_out(true);
    set_checkout_error(null);
    try {
      const order = await checkout_cart();
      set_cart({ items: [], total: 0 });
      set_cart_open(false);
      set_order_success(order.id);
    } catch (err) {
      set_checkout_error(err.message);
    } finally {
      set_checking_out(false);
    }
  }

  return (
    <div className="section-container">
      <div className="section-header-row">
        <h1 className="section-heading">Product Catalog</h1>
        {is_customer && (
          <button className="cart-toggle-btn" onClick={() => set_cart_open(true)}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
            </svg>
            Cart
            {cart_count > 0 && <span className="cart-nav-badge">{cart_count}</span>}
          </button>
        )}
      </div>

      {order_success && (
        <OrderSuccessModal
          order_id={order_success}
          on_close={() => set_order_success(null)}
        />
      )}

      {loading && <div className="loading-state">Loading products…</div>}
      {error && <div className="error-state">{error}</div>}

      {!loading && !error && (
        <>
          <div className="category-filters">
            {categories.map((cat) => (
              <button
                key={cat}
                className={`category-btn${active_category === cat ? ' active' : ''}`}
                onClick={() => set_active_category(cat)}
              >
                {cat}
              </button>
            ))}
          </div>

          {filtered.length === 0 ? (
            <div className="empty-state">No products in this category.</div>
          ) : (
            <div className="products-grid">
              {filtered.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  cart_qty={cart_qty_map[product.id] || 0}
                  on_add={() => handle_add(product.id)}
                  on_decrease={() => handle_decrease(product.id)}
                  is_customer={is_customer}
                  busy={!!busy[product.id]}
                />
              ))}
            </div>
          )}
        </>
      )}

      {cart_open && (
        <CartPanel
          cart={cart}
          on_remove={handle_remove}
          on_checkout={handle_checkout}
          on_close={() => { set_cart_open(false); set_checkout_error(null); }}
          checking_out={checking_out}
          checkout_error={checkout_error}
        />
      )}
    </div>
  );
}

export default Products;
