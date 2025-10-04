import React, { createContext, useContext, useState, useEffect } from "react";

interface User {
  id: number;
  email: string;
  role_id?: number;
}

interface UserContextType {
  currentUser: User | null;
  logout: () => Promise<void>;
}

export const UserContext = createContext<UserContextType>({
  currentUser: null,
  logout: async () => {},
});

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_ORIGIN}/api/auth/me`, {
      credentials: "include",
    })
      .then(res => res.json())
      .then(data => setCurrentUser(data.user))
      .catch(() => setCurrentUser(null));
  }, []);

  const logout = async () => {
    await fetch(`${import.meta.env.VITE_API_ORIGIN}/api/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    setCurrentUser(null);
  };

  return (
    <UserContext.Provider value={{ currentUser, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);

