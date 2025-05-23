import { useState, useEffect } from "react";

const CategoryForm = ({ updateCallback }) => {
  const [name, setName] = useState("");
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    const response = await fetch("http://127.0.0.1:5000/category/categories");
    if (response.ok) {
      const data = await response.json();
      setCategories(data.categories);
    } else {
      alert("Failed to fetch categories");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = {
      Category: name,
    };
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
      setCategories((prevCategories) => [...prevCategories, newCategory]); // Update the table
      updateCallback();
    } else {
      alert("Failed to add category");
    }
  };

  return (
    <div>
      <table border="1">
        <thead>
          <tr>
            <th>Categories</th>
          </tr>
        </thead>
        <tbody>
          {Object.values(categories).map((categoryObj, index) => (
            <tr key={index}>
              <td>{categoryObj.Category}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Form to add a new category */}
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
    </div>
  );
};

export default CategoryForm;
