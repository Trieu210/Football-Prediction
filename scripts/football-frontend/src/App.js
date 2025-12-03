import React, { useState } from "react";
import { Route, Routes } from "react-router-dom";
import "./App.css";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import PageHeader from "./PageHeader";
import LeaguePage from "./page/LeaguePage";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen((prev) => !prev);
  const closeSidebar = () => setSidebarOpen(false);

  return (
    <div
      className="app-root"
      style={{ background: "#020617", minHeight: "100vh", color: "#e5e7eb" }}
    >
      <Navbar onToggleSidebar={toggleSidebar} />

      <div style={{ display: "flex" }}>
        <Sidebar open={sidebarOpen} onClose={closeSidebar} />

        <main style={{ flex: 1, padding: "20px" }}>
          <Routes>
            <Route path="/league/:leagueName" element={<LeaguePage />} />
            {/* you can add more routes here later */}
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
