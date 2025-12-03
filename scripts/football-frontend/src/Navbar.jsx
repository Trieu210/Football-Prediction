// src/Navbar.jsx
import React from "react";

const Navbar = ({ onToggleSidebar }) => {
  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 1000,
        background: "#020617",
        borderBottom: "1px solid #111827",
        padding: "12px 18px",
      }}
    >
      <div
        className="d-flex align-items-center justify-content-between"
        style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}
      >
        {/* Left: logo / title */}
        <div style={{ fontWeight: 700, fontSize: "1.1rem", color: "#e5e7eb" }}>
          Football Dashboard
        </div>

        {/* Right: hamburger button */}
        <button
          type="button"
          onClick={onToggleSidebar}
          style={{
            border: "none",
            background: "transparent",
            padding: 0,
            cursor: "pointer",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: "4px",
          }}
          aria-label="Toggle sidebar"
        >
          <span
            style={{
              width: "20px",
              height: "2px",
              background: "#e5e7eb",
              borderRadius: "999px",
            }}
          />
          <span
            style={{
              width: "20px",
              height: "2px",
              background: "#e5e7eb",
              borderRadius: "999px",
            }}
          />
          <span
            style={{
              width: "20px",
              height: "2px",
              background: "#e5e7eb",
              borderRadius: "999px",
            }}
          />
        </button>
      </div>
    </header>
  );
};

export default Navbar;
