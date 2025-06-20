import { useState } from "react";
import "../styles/Auth.css";

const AuthForm = ({ mode = "login", onSuccess }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const isLogin = mode === "login";
  const endpoint = isLogin ? "login" : "register";
  const title = isLogin ? "Sign In" : "Register";

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/auth/${endpoint}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        if (isLogin) {
          localStorage.setItem("accessToken", data.access_token);
          localStorage.setItem("refreshToken", data.refresh_token);
          localStorage.setItem("user", JSON.stringify(data.user));
          onSuccess(data.user);
        } else {
          onSuccess();
        }
      } else {
        setError(data.message);
      }
    } catch (error) {
      setError(`Failed to connect to server: ${error.message}`);
    }
  };

  return (
    <div className="auth-form">
      <h2>{title}</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="input-label">
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="input-label">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">{title}</button>
      </form>
    </div>
  );
};

export default AuthForm;
