import { useState, useEffect } from "react";

const CategoryForm = ({ updateCallback }) => {
  const [name, setName] = useState("");
  const [categories, setCategories] = useState([]);
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem("user"));
    if (userData && userData.id) {
      setUserId(userData.id);
      fetchCategories(userData.id);
    }
  }, []);

  const fetchCategories = async (id) => {
    const token = localStorage.getItem("accessToken");
    const url = `http://127.0.0.1:5000/category/${id}/categories`;

    try {
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      if (response.ok) {
        const data = await response.json();
        setCategories(data.categories);
      } else {
        const errorData = await response.json();
        alert(errorData.message || "Failed to fetch categories");
      }
    } catch (error) {
      alert(`Failed to connect to server: ${error.message}`);
    }
  };

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
    const url = `http://127.0.0.1:5000/category/${userId}/categories`;
    const options = {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    };

    try {
      const response = await fetch(url, options);
      if (response.ok) {
        fetchCategories(userId);
        setName("");
        if (updateCallback) updateCallback();
      } else {
        const errorData = await response.json();
        alert(errorData.message || "Failed to add category");
      }
    } catch (error) {
      alert(`Error connecting to server: ${error.message}`);
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
          {Object.values(categories)
            .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
            .map((categoryObj, index) => (
              <tr key={index}>
                <td>{categoryObj.Category}</td>
              </tr>
            ))}
        </tbody>
      </table>

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
