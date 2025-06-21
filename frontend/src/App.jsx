import { useState, useEffect } from "react";
import AuthService from "./services/AuthService";
import ExpenseList from "./components/ExpenseList";
import ExpenseForm from "./components/ExpenseForm";
import CategoryList from "./components/CategoryList";
import CategoryForm from "./components/CategoryForm";
import AuthForm from "./components/AuthForm";
import "./styles/App.css";

function App() {
  const [expenses, setExpenses] = useState([]);
  const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [currentExpense, setCurrentExpense] = useState({});
  const [currentCategory, setCurrentCategory] = useState({});
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [user, setUser] = useState(null);
  const [activeView, setActiveView] = useState("expenses");
  const [categories, setCategories] = useState([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const token = localStorage.getItem("accessToken");
    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
      fetchExpenses();
      fetchCategories();
    }

    const handleClickOutside = (event) => {
      if (!event.target.closest(".settings-dropdown")) {
        setIsSettingsOpen(false);
      }
    };

    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  const fetchCategories = async () => {
    try {
      const userData = JSON.parse(localStorage.getItem("user"));
      if (!userData || !userData.id) {
        throw new Error("User not authenticated");
      }
      const response = await AuthService.fetchWithAuth(
        `${import.meta.env.VITE_API_URL}/category/${userData.id}/categories`
      );
      if (response.ok) {
        const data = await response.json();
        setCategories(data.categories);
      } else {
        console.error("Failed to fetch categories");
      }
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  const fetchExpenses = async () => {
    try {
      const userData = JSON.parse(localStorage.getItem("user"));
      if (!userData || !userData.id) {
        throw new Error("User not authenticated");
      }
      const response = await AuthService.fetchWithAuth(
        `${import.meta.env.VITE_API_URL}/expense/${userData.id}/expenses`
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
    AuthService.logout();
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
    setCurrentCategory({});
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

  const openEditCategoryModal = (category) => {
    if (isCategoryModalOpen) return;
    setCurrentCategory(category);
    setIsCategoryModalOpen(true);
  };

  const onCategoryUpdate = () => {
    closeCategoryModal();
    fetchCategories();
  };

  if (!isAuthenticated) {
    return (
      <div className="auth-container">
        <AuthForm
          mode={showRegister ? "register" : "login"}
          onSuccess={
            showRegister ? () => setShowRegister(false) : handleLoginSuccess
          }
        />
        <button onClick={() => setShowRegister(!showRegister)}>
          {showRegister
            ? "Already have an account? Login"
            : "Need an account? Register"}
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="welcome-header">
        <span>Welcome, {user.username}!</span>
        <div className="nav-buttons">
          <button
            className={activeView === "expenses" ? "active" : ""}
            onClick={() => {
              setActiveView("expenses");
              fetchExpenses();
            }}
          >
            Expenses
          </button>
          <button
            className={activeView === "categories" ? "active" : ""}
            onClick={() => {
              setActiveView("categories");
              fetchCategories();
            }}
          >
            Categories
          </button>
        </div>
        <div className="settings-dropdown">
          <button
            className="settings-button"
            onClick={() => setIsSettingsOpen(!isSettingsOpen)}
          >
            Settings
          </button>
          {isSettingsOpen && (
            <div className="dropdown-menu">
              <button onClick={handleLogout}>Logout</button>
            </div>
          )}
        </div>
      </div>

      {activeView === "expenses" ? (
        <>
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
        </>
      ) : (
        <>
          <CategoryList
            categories={categories}
            updateCategory={openEditCategoryModal}
            updateCallback={onCategoryUpdate}
          />
          <button onClick={openCategoryModal}>Create New Category</button>
          {isCategoryModalOpen && (
            <div className="modal">
              <div className="modal-content">
                <span className="close" onClick={closeCategoryModal}>
                  &times;
                </span>
                <CategoryForm
                  existingCategory={currentCategory}
                  updateCallback={onCategoryUpdate}
                />
              </div>
            </div>
          )}
        </>
      )}
    </>
  );
}

export default App;
