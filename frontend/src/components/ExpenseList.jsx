import React from "react";
import "../styles/ExpenseList.css";

const ExpenseList = ({ expenses, updateExpense, updateCallback }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const month = String(date.getUTCMonth() + 1).padStart(2, "0");
    const day = String(date.getUTCDate()).padStart(2, "0");
    const year = date.getUTCFullYear();
    return `${month}-${day}-${year}`;
  };

  const onDelete = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this expense?"
    );
    if (!confirmDelete) {
      return;
    }

    try {
      const token = localStorage.getItem("accessToken");
      const userData = JSON.parse(localStorage.getItem("user"));

      if (!userData || !userData.id) {
        throw new Error("User not authenticated");
      }

      const options = {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      };

      const url = `http://127.0.0.1:5000/expense/${userData.id}/expenses/${id}`;
      const response = await fetch(url, options);
      if (response.ok) {
        updateCallback();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to delete expense");
      }
    } catch (error) {
      console.error("Error deleting expense:", error);
      alert(`Error deleting expense: ${error.message}`);
    }
  };

  return (
    <div>
      <h2>Expense Log</h2>
      <table className="expense-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Category</th>
            <th>Amount</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map((expense) => (
            <tr key={expense.id}>
              <td>{formatDate(expense.Date)}</td>
              <td>{expense.Category}</td>
              <td>
                {expense.Amount < 0
                  ? `$(${Math.abs(expense.Amount).toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })})`
                  : `$${expense.Amount.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}`}
              </td>
              <td>{expense.Description}</td>
              <td>
                <button onClick={() => updateExpense(expense)}>Update</button>
                <button onClick={() => onDelete(expense.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ExpenseList;
