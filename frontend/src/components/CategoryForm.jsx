import { useState, useEffect } from "react";
import AuthService from "../services/AuthService";

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

    const data = {
      Category: name,
    };

    const url = updating
      ? `${import.meta.env.VITE_API_URL}/category/${userId}/categories/${
          existingCategory.id
        }`
      : `${import.meta.env.VITE_API_URL}/category/${userId}/categories`;

    try {
      const response = await AuthService.fetchWithAuth(url, {
        method: updating ? "PATCH" : "POST",
        body: JSON.stringify(data),
      });

      if (response.ok) {
        // Reset form if adding new category
        if (!updating) {
          setName("");
        }
        // Fetch updated categories list
        const categoriesResponse = await AuthService.fetchWithAuth(
          `${import.meta.env.VITE_API_URL}/category/${userId}/categories`
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
