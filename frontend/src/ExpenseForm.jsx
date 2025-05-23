import { useState, useEffect } from "react";

const ExpenseForm = ({ existingExpense = {}, updateCallback }) => {
  const [date, setDate] = useState(existingExpense.Date || "");
  const [category, setCategory] = useState(existingExpense.Category || "");
  const [amount, setAmount] = useState(existingExpense.Amount || "");
  const [description, setDescription] = useState(
    existingExpense.Description || ""
  );
  const [categories, setCategories] = useState({});

  const updating = Object.entries(existingExpense).length !== 0;

  const fetchCategories = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/category/categories");
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

  useEffect(() => {
    fetchCategories();
  }, [existingExpense]);

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

    const data = {
      date: new Date(date).toISOString().split("T")[0],
      categoryId: parseInt(category) + 1,
      amount,
      description,
    };
    const url =
      "http://127.0.0.1:5000/expense/" +
      (updating ? `update_expense/${existingExpense.id}` : "create_expense");
    const options = {
      method: updating ? "PATCH" : "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    };
    const response = await fetch(url, options);
    if (response.status !== 201 && response.status !== 200) {
      const data = await response.json();
      alert(data.error);
    } else {
      updateCallback();
    }
  };

  return (
    <form onSubmit={onSubmit}>
      <div>
        <label htmlFor="Date">Date:</label>
        <input
          type="date"
          id="date"
          value={date ? new Date(date).toISOString().split("T")[0] : date}
          onChange={(e) => setDate(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="category">Category:</label>
        <select
          id="category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
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
        />
      </div>
      <div>
        <label htmlFor="description">Description:</label>
        <input
          type="text"
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
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
