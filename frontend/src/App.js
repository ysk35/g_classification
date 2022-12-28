import React from 'react'
import './es/css/App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Login from './components/Login';
import SignUp from './components/SignUp';
import Judge from './components/Judge';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path='/login' element={<Login />} />
                <Route path='/signup' element={<SignUp />} />
                <Route path='/Judge' element={<Judge />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App;