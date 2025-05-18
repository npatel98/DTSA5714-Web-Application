import React from "react"

const ExpenseList = ({expenses}) => {
    return <div>
        <h2>Expenses</h2>
        <table>
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
                        <td>{expense.Date}</td>
                        <td>{expense.Category}</td>
                        <td>{expense.Amount}</td>
                        <td>{expense.Description}</td>
                        <td>
                            <button>Update</button>
                            <button>Delete</button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
}

export default ExpenseList