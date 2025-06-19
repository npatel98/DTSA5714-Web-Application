import { useState, useEffect } from "react";

const CategoryForm = ({ existingCategory = {}, updateCallback }) => {
  const [name, setName] = useState(existingCategory.Category || "");
  const [userId, setUserId] = useState(null);

  const updating = Object.entries(existingCategory).length !== 0;

  useEffect(() => {
    if (existingCategory.Category) {
      setName(existingCategory.Category);
    }
  }, [existingCategory]);

  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem("user"));
    if (userData && userData.id) {
      setUserId(userData.id);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!userId) {
      alert("User not authenticated");
      return;
    }

    const token = localStorage.getItem("accessToken");
    const data = {
      Category: name,
    };
    const url = updating
      ? `http://127.0.0.1:5000/category/${userId}/categories/${existingCategory.id}`
      : `http://127.0.0.1:5000/category/${userId}/categories`;

    const options = {
      method: updating ? "PATCH" : "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    };

    try {
      const response = await fetch(url, options);
      if (response.ok) {
        // Reset form if adding new category
        if (!updating) {
          setName("");
        }
        // Fetch updated categories list
        const categoriesResponse = await fetch(
          `http://127.0.0.1:5000/category/${userId}/categories`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );
        if (categoriesResponse.ok) {
          const categoriesData = await categoriesResponse.json();
          if (updateCallback) {
            updateCallback(categoriesData.categories);
          }
        }
      } else {
        const errorData = await response.json();
        alert(
          errorData.message ||
            `Failed to ${updating ? "update" : "add"} category`
        );
      }
    } catch (error) {
      alert(`Error connecting to server: ${error.message}`);
    }
  };

  if (!userId) {
    return <div>Please log in to manage categories.</div>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Category Name:</label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>
      <button type="submit">
        {updating ? "Update Category" : "Add Category"}
      </button>
    </form>
  );
};

export default CategoryForm;
