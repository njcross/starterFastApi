import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import "./variables.css";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
      </nav>

      <div className="container">
        <Routes>
          <Route index element={<Home />} />
          <Route path="about" element={<About />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
