import { useState } from 'react';
import { login, register, forgot_password, reset_password } from '../api';

function Auth({ on_auth }) {
  const [mode, set_mode] = useState('login'); // 'login' | 'register' | 'forgot' | 'reset'
  const [email, set_email] = useState('');
  const [password, set_password] = useState('');
  const [reset_token, set_reset_token] = useState('');
  const [new_password, set_new_password] = useState('');
  const [submitting, set_submitting] = useState(false);
  const [error, set_error] = useState(null);
  const [reset_email, set_reset_email] = useState('');

  function go_to(next_mode) {
    set_mode(next_mode);
    set_error(null);
  }

  async function handle_submit(e) {
    e.preventDefault();
    set_submitting(true);
    set_error(null);
    try {
      if (mode === 'login') {
        const data = await login(email, password);
        on_auth(data.access_token);
      } else if (mode === 'register') {
        const data = await register(email, password);
        on_auth(data.access_token);
      } else if (mode === 'forgot') {
        await forgot_password(email);
        set_reset_email(email);
        go_to('reset');
      } else if (mode === 'reset') {
        const data = await reset_password(reset_token, new_password);
        on_auth(data.access_token);
      }
    } catch (err) {
      set_error(err.message);
    } finally {
      set_submitting(false);
    }
  }

  const titles = {
    login: 'Welcome back',
    register: 'Create account',
    forgot: 'Reset your password',
    reset: 'Set new password',
  };

  const subtitles = {
    login: 'Sign in to your account',
    register: 'Register to get started',
    forgot: 'Enter your email to receive a reset token',
    reset: `Enter the token sent for ${reset_email}`,
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <span className="brand-icon">🛍</span>
          <span className="brand-name">ShopEase</span>
        </div>

        <h1 className="auth-title">{titles[mode]}</h1>
        <p className="auth-subtitle">{subtitles[mode]}</p>

        <form onSubmit={handle_submit} className="auth-form">

          {(mode === 'login' || mode === 'register' || mode === 'forgot') && (
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                className="form-input"
                type="email"
                value={email}
                onChange={(e) => set_email(e.target.value)}
                placeholder="you@example.com"
                required
                autoFocus
              />
            </div>
          )}

          {(mode === 'login' || mode === 'register') && (
            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                className="form-input"
                type="password"
                value={password}
                onChange={(e) => set_password(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
          )}

          {mode === 'reset' && (
            <>
              <div className="form-group">
                <label className="form-label">Reset Token</label>
                <input
                  className="form-input"
                  type="text"
                  value={reset_token}
                  onChange={(e) => set_reset_token(e.target.value)}
                  placeholder="Paste your reset token"
                  required
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label className="form-label">New Password</label>
                <input
                  className="form-input"
                  type="password"
                  value={new_password}
                  onChange={(e) => set_new_password(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
            </>
          )}

          {mode === 'login' && (
            <div className="auth-forgot-row">
              <button type="button" className="auth-switch-btn" onClick={() => go_to('forgot')}>
                Forgot password?
              </button>
            </div>
          )}

          {error && <div className="error-state">{error}</div>}

          <button className="primary-btn auth-submit-btn" type="submit" disabled={submitting}>
            {submitting ? '…' : {
              login: 'Sign In',
              register: 'Create Account',
              forgot: 'Send Reset Token',
              reset: 'Set New Password',
            }[mode]}
          </button>
        </form>

        {(mode === 'login' || mode === 'register') && (
          <p className="auth-switch">
            {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button className="auth-switch-btn" onClick={() => go_to(mode === 'login' ? 'register' : 'login')}>
              {mode === 'login' ? 'Register' : 'Sign In'}
            </button>
          </p>
        )}

        {(mode === 'forgot' || mode === 'reset') && (
          <p className="auth-switch">
            <button className="auth-switch-btn" onClick={() => go_to('login')}>
              ← Back to Sign In
            </button>
          </p>
        )}
      </div>
    </div>
  );
}

export default Auth;
