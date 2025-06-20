import React from "react";
import AuthService from "../services/AuthService";
import "../styles/CategoryList.css";

const CategoryList = ({ categories, updateCategory, updateCallback }) => {
  const onDelete = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this category?"
    );
    if (!confirmDelete) {
      return;
    }

    try {
      const userData = JSON.parse(localStorage.getItem("user"));
      if (!userData || !userData.id) {
        throw new Error("User not authenticated");
      }

      const url = `${import.meta.env.VITE_API_URL}/category/${
        userData.id
      }/categories/${id}`;
      const response = await AuthService.fetchWithAuth(url, {
        method: "DELETE",
      });

      if (response.ok) {
        updateCallback();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to delete category");
      }
    } catch (error) {
      console.error("Error deleting category:", error);
      alert(`Error deleting category: ${error.message}`);
    }
  };

  const sortedCategories = [...categories].sort(
    (a, b) => new Date(a.createdAt) - new Date(b.createdAt)
  );

  return (
    <div>
      <h2>Categories</h2>
      <table className="category-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sortedCategories.map((category) => (
            <tr key={category.id}>
              <td>{category.Category}</td>
              <td>
                <button onClick={() => updateCategory(category)}>Update</button>
                <button onClick={() => onDelete(category.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CategoryList;
