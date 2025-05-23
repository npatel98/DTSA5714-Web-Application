import { useState, useEffect } from "react";
import ExpenseList from "./ExpenseList";
import ExpenseForm from "./ExpenseForm";
import CategoryForm from "./CategoryForm";
import "./App.css";

function App() {
  const [expenses, setExpenses] = useState([]);
  const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [currentExpense, setCurrentExpense] = useState({});

  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    const response = await fetch("http://127.0.0.1:5000/expense/expenses");
    const data = await response.json();
    setExpenses(data.expenses);
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
    console.log("Editing expense:", expense);
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

  return (
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
