import React from 'react'
import { useState, useCallback, useEffect } from 'react'
import { useLocation } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import '../es/css/Judge.css';

function Modal({show, setShow, ans,type}) {
  const closeModal = () => {
      setShow(false)
  }

  if (show) {
    return (
      <div id="overlay">
        <div id="content" onClick={(e) => e.stopPropagation()}>
          <p>種類：{type}</p>
          <p>ゴミ出し日：{ans}</p>
          <button className="modal-close" onClick={closeModal}>✖︎閉じる</button>
        </div>
      </div >
    )
  } else {
    return null;
  }
}

function Judge() {
  const [image, setImage] = useState();
  const [area, setArea] = useState();
  const URL = 'http://localhost:8000/posts';
  const [show, setShow] = useState(false);
  const [ans, setAns] = useState();
  const [type, setType] = useState();
  const [regions, setRegions] = useState([])
  const location = useLocation();
  const is_login = location.state['is_login'];
  const user_area = location.state['user_area'];

  const getRegions = async () => {
    const response = await fetch('http://localhost:8000/regions', {method: 'POST'});
    const data = await response.json();
    setRegions(data["regions"]);
  }

  useEffect(() => {
    setArea(user_area);
    getRegions();
  }, []);
  const rows = regions.map((region, index) => {
    if(index == area){
      return <option value={index} selected>{region}</option>
    }else{
      return <option value={index}>{region}</option>
    }
  });

  const Submit = async() => {
    const formdata = new FormData()
    formdata.append('area', JSON.stringify({'name': area}))
    formdata.append('upload_file', image)
    const requestOptions = {
      method:"POST",
      body: formdata,
    }

    const response = await fetch(URL,requestOptions)
    const data = await response.json()
    setShow(true)
    setAns(data["ans"])
    setType(data['type'])
  }
  const handleSubmit = (e) => {
    e.preventDefault()
    Submit()
  }
  const handleChangeArea = (event) => {
    setArea(event.currentTarget.value);
  };

  const onDrop = useCallback((acceptedFiles) => {
      if(!acceptedFiles) return
      const img = acceptedFiles[0]
      setImage(img)
  }, []);

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  return (
    <div className="container">
      <form onSubmit={handleSubmit}>
        <h1 className="title">ゴミわける−ん</h1>
        <div className="drop-box" {...getRootProps()}>
          <input id="img" type="file" accept="image/*,.png,.jpg,.jpeg,.gif" {...getInputProps()} />
          <p className='d-label'>撮影</p>
        </div>
        <label>お住まいの市町村</label>
        <select
            className="form-input form-select"
            onChange={(event) => handleChangeArea(event)}

          >
            {rows}
        </select>

        <br/>
        <button className="form-btn" type="submit">送信</button>
      </form>

      <Modal show={show} setShow={setShow} ans={ans} type={type}/>
    </div>
  )
}

export default Judge;