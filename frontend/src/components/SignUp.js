import React from 'react'
import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import '../es/css/SignUp.css';

function SignUp(){
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [area, setArea] = useState(0);
  const URL = 'http://localhost:8000/signup'
  const navigate = useNavigate();

  const [regions, setRegions] = useState([])

  const getRegions = async () => {
    const response = await fetch('http://localhost:8000/regions', {method: 'POST'});
    const data = await response.json();
    setRegions(data["regions"]);
  }

  useEffect(() => {
    getRegions();
  }, []);
  const rows = regions.map((region, index) =>
    <option value={index}>{region}</option>
  );

  const Submit = async() => {
    const requestOptions = {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({"email": email, "password": password, "area": area}),
    }
    const response = await fetch(URL, requestOptions)
    const data = await response.json()
    if(data["is_success"]){
      navigate("/login")
    }else{
      if(data["error"] == "exists"){
        alert("このメールアドレスはすでに使用されています。");
      }
    }
  }
  const handleSubmit = (event) => {
    event.preventDefault();
    Submit();
  };
  const handleChangeEmail = (event) => {
    setEmail(event.currentTarget.value);
  };
  const handleChangePassword = (event) => {
    setPassword(event.currentTarget.value);
  };
  const handleChangeArea = (event) => {
    setArea(event.currentTarget.value);
  };

  return (
    <div>
      <h3 className="title">新規登録</h3>
      <form onSubmit={handleSubmit} className="container">
        <div>
          <label>メールアドレス</label>
          <input
            className="form-input"
            name="email"
            type="email"
            placeholder="email"
            onChange={(event) => handleChangeEmail(event)}
          />
        </div>
        <div>
          <label>パスワード</label>
          <input
            className="form-input"
            name="password"
            type="password"
            placeholder="password"
            onChange={(event) => handleChangePassword(event)}
          />
        </div>
        <div>
          <label>お住まいの市町村</label>
          <select
            className="form-input form-select"
            onChange={(event) => handleChangeArea(event)}
          >
            {rows}
          </select>
        </div>
        <div>
          <button className="form-btn">登録</button>
        </div>
        <Link to='/login' className='link-btn'>ログインはこちら</Link>
      </form>
    </div>
  );
}

export default SignUp;