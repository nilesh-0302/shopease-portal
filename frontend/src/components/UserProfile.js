import { useState, useEffect, useRef } from 'react';
import { get_profile } from '../api';

function UserProfile() {
  const [profile, set_profile] = useState(null);
  const [open, set_open] = useState(false);
  const wrapper_ref = useRef(null);

  useEffect(() => {
    get_profile().then(set_profile).catch(() => {});
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

  const initials = profile?.name
    ? profile.name.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2)
    : profile?.email?.[0]?.toUpperCase() ?? '?';

  return (
    <div className="profile-wrapper" ref={wrapper_ref}>
      <button className="profile-avatar" onClick={() => set_open(!open)} aria-label="Profile">
        {initials}
      </button>

      {open && profile && (
        <div className="profile-panel">
          <div className="profile-panel-top">
            <div className="profile-avatar-lg">{initials}</div>
            <div className="profile-info">
              {profile.name && <p className="profile-name">{profile.name}</p>}
              <p className="profile-email">{profile.email}</p>
              <span className={`profile-role-badge role-${profile.role}`}>{profile.role}</span>
            </div>
          </div>
          <div className="profile-panel-row">
            <span className="profile-detail-label">User ID</span>
            <span className="profile-detail-value">#{profile.id}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserProfile;
