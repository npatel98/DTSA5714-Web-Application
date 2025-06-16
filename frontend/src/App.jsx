import { useState, useEffect } from "react";
import ExpenseList from "./ExpenseList";
import ExpenseForm from "./ExpenseForm";
import CategoryForm from "./CategoryForm";
import LoginForm from "./LoginForm";
import RegisterForm from "./RegisterForm";
import "./App.css";

function App() {
  const [expenses, setExpenses] = useState([]);
  const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [currentExpense, setCurrentExpense] = useState({});
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const token = localStorage.getItem("accessToken");
    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
      fetchExpenses();
    }
  }, []);

  const fetchExpenses = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const userData = JSON.parse(localStorage.getItem("user"));

      if (!userData || !userData.id) {
        throw new Error("User not authenticated");
      }

      const response = await fetch(
        `http://127.0.0.1:5000/expense/${userData.id}/expenses`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setExpenses(data.expenses);
      } else {
        console.error("Failed to fetch expenses");
      }
    } catch (error) {
      console.error("Error fetching expenses:", error);
    }
  };

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
    fetchExpenses();
  };

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("user");
    setIsAuthenticated(false);
    setUser(null);
  };

  const closeExpenseModal = () => {
    setIsExpenseModalOpen(false);
    setCurrentExpense({});
  };

  const openExpenseModal = () => {
    setIsExpenseModalOpen(true);
  };

  const closeCategoryModal = () => {
    setIsCategoryModalOpen(false);
  };

  const openCategoryModal = () => {
    setIsCategoryModalOpen(true);
  };

  const openEditExpenseModal = (expense) => {
    if (isExpenseModalOpen) return;
    setCurrentExpense(expense);
    setIsExpenseModalOpen(true);
  };

  const onExpenseUpdate = () => {
    closeExpenseModal();
    fetchExpenses();
  };

  const onCategoryAdded = () => {
    closeCategoryModal();
  };

  if (!isAuthenticated) {
    return (
      <div className="auth-container">
        {showRegister ? (
          <>
            <RegisterForm onRegisterSuccess={() => setShowRegister(false)} />
            <button onClick={() => setShowRegister(false)}>
              Already have an account? Login
            </button>
          </>
        ) : (
          <>
            <LoginForm onLoginSuccess={handleLoginSuccess} />
            <button onClick={() => setShowRegister(true)}>
              Need an account? Register
            </button>
          </>
        )}
      </div>
    );
  }

  return (
    <>
      <div className="welcome-header">
        <span>Welcome, {user.username}!</span>
        <button onClick={handleLogout}>Logout</button>
      </div>

      <ExpenseList
        expenses={expenses}
        updateExpense={openEditExpenseModal}
        updateCallback={onExpenseUpdate}
      />
      <button onClick={openExpenseModal}>Create New Expense</button>
      {isExpenseModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={closeExpenseModal}>
              &times;
            </span>
            <ExpenseForm
              existingExpense={currentExpense}
              updateCallback={onExpenseUpdate}
            />
          </div>
        </div>
      )}
      <button onClick={openCategoryModal}>Create New Category</button>
      {isCategoryModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={closeCategoryModal}>
              &times;
            </span>
            <CategoryForm updateCallback={onCategoryAdded} />
          </div>
        </div>
      )}
    </>
  );
}

export default App;
