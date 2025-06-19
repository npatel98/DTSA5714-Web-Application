import { useState, useEffect } from "react";
import AuthService from "../services/AuthService";

const ExpenseForm = ({ existingExpense = {}, updateCallback }) => {
  const [date, setDate] = useState(existingExpense.Date || "");
  const [category, setCategory] = useState(existingExpense.Category || "");
  const [amount, setAmount] = useState(existingExpense.Amount || "");
  const [description, setDescription] = useState(
    existingExpense.Description || ""
  );
  const [categories, setCategories] = useState({});
  const [userId, setUserId] = useState(null);

  const updating = Object.entries(existingExpense).length !== 0;

  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem("user"));
    if (userData && userData.id) {
      setUserId(userData.id);
      fetchCategories(userData.id);
    }
  }, []);

  const fetchCategories = async (id) => {
    try {
      const url = `http://127.0.1:5000/category/${id}/categories`;
      const response = await AuthService.fetchWithAuth(url);

      if (response.ok) {
        const data = await response.json();
        const categoriesMap = {};

        const sortedCategories = data.categories.sort((a, b) => {
          return new Date(a.createdAt) - new Date(b.createdAt);
        });

        sortedCategories.forEach((category) => {
          categoriesMap[category.id] = {
            Category: category.Category,
            uuid: category.id,
          };
        });
        setCategories(categoriesMap);
      } else {
        console.error("Failed to fetch categories");
      }
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  useEffect(() => {
    if (existingExpense.Category && categories) {
      const categoryId = Object.entries(categories).find(
        ([, categoryObj]) => categoryObj.Category === existingExpense.Category
      )?.[0];
      if (categoryId) {
        setCategory(categoryId);
      }
    }
  }, [existingExpense, categories]);

  const onSubmit = async (e) => {
    e.preventDefault();

    if (!userId) {
      alert("User not authenticated");
      return;
    }

    if (!category) {
      alert("Please select a category.");
      return;
    }

    const data = {
      date: new Date(date).toISOString().split("T")[0],
      categoryId: category,
      amount: parseFloat(amount),
      description,
    };

    const url = updating
      ? `http://127.0.0.1:5000/expense/${userId}/expenses/${existingExpense.id}`
      : `http://127.0.0.1:5000/expense/${userId}/expenses`;

    try {
      const response = await AuthService.fetchWithAuth(url, {
        method: updating ? "PATCH" : "POST",
        body: JSON.stringify(data),
      });

      if (response.ok) {
        updateCallback();
      } else {
        const errorData = await response.json();
        console.error("Server error:", errorData);
        alert(errorData.message || "Failed to save expense");
      }
    } catch (error) {
      console.error("Request error:", error);
      alert(`Error connecting to server: ${error.message}`);
    }
  };

  if (!userId) {
    return <div>Please log in to manage expenses.</div>;
  }

  return (
    <form onSubmit={onSubmit}>
      <div>
        <label htmlFor="Date">Date:</label>
        <input
          type="date"
          id="date"
          value={date ? new Date(date).toISOString().split("T")[0] : date}
          onChange={(e) => setDate(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="category">Category:</label>
        <select
          id="category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          required
        >
          <option value="">Select a category</option>
          {categories &&
            Object.entries(categories).map(([id, categoryObj]) => (
              <option key={id} value={id}>
                {categoryObj.Category}
              </option>
            ))}
        </select>
      </div>
      <div>
        <label htmlFor="amount">Amount:</label>
        <input
          type="text"
          id="amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="description">Description:</label>
        <input
          type="text"
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />
      </div>
      <div>
        <button type="submit">
          {updating ? "Update Expense" : "Create Expense"}
        </button>
      </div>
    </form>
  );
};

export default ExpenseForm;
