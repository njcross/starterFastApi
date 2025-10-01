import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import { UserProvider, useUser } from "./contexts/UserContext"

function AppContent() {
  const { currentUser, logout } = useUser();

  return (
    <>
      <nav style={{ display: "flex", gap: 12, padding: 12 }}>
        <Link to="/">Home</Link>
        {!currentUser && <Link to="/login">Login</Link>}
        {currentUser && (
          <>
            <span>Welcome, {currentUser.email}</span>
            <button onClick={logout}>Logout</button>
          </>
        )}
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <UserProvider>
        <AppContent />
      </UserProvider>
    </BrowserRouter>
  );
}
