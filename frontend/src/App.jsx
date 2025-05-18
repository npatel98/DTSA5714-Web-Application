import { useState, useEffect } from 'react'
import ExpenseList from './ExpenseList'
import './App.css'

function App() {
  const [expenses, setExpenses] = useState([])

  useEffect(() => {
    fetchExpenses()
  }, [])

  const fetchExpenses = async () => {
    const response = await fetch("http://127.0.0.1:5000/expense/expenses")
    const data = await response.json()
    setExpenses(data.expenses)
    console.log(data.expenses)
  }

  return <ExpenseList expenses={expenses} />
}

export default App
