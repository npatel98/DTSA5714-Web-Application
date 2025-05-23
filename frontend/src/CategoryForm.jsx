import { useState } from "react";

const CategoryForm = ({ onCategoryAdded }) => {
  const [name, setName] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = { name };
    const url = "http://127.0.0.1:5000/category/create_category";
    const options = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    };

    const response = await fetch(url, options);
    if (response.ok) {
      const newCategory = await response.json();
      onCategoryAdded(newCategory);
    } else {
      alert("Failed to add category");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Category Name:</label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>
      <button type="submit">Add Category</button>
    </form>
  );
};

export default CategoryForm;
