import { useState, useEffect } from 'react'

function App() {
  const [tableData, setTableData] = useState([]);
  const [previewText, setPreviewText] = useState('');

  // Get table data at mount 
  useEffect(() => {
    fetch('http://127.0.0.1:5000/list')
      .then(response => response.json())
      .then(data => setTableData(data['files']))
      .catch(error => console.error(error));
  }, []);

  // Preview get api, triggered by onClick
  const handlePreviewClick = (filename) => {
    fetch(`http://127.0.0.1:5000/preview?name=${filename}`)
      .then(response => response.json())
      .then(data => setPreviewText(data.content))
      .catch(error => console.error(error));
  };

  return (
    <>
      <div>
        <h2>島嶼大學各科系面試資料</h2>
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th>Department</th>
              <th>Title</th>
              <th>Preview</th>
              <th>File URL</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map(item => (
              <tr key={item.id}>
                <td>{item.year}</td>
                <td>{item.department}</td>
                <td>{item.title}</td>
                <td>
                <button onClick={() => handlePreviewClick(item.filename)}>
                    預覽
                  </button>
                </td>
                <td><a href={item.fileurl}>點我下載</a></td>
                {/* <td><a href='http://www.example.com/'>click to redirect</a></td> */}
              </tr>
            ))}
          </tbody>
        </table>

        {/* 顯示文章內容預覽的地方 */}
        <br></br>
        {previewText && (
          <div>
            <h2>Archive Preview:</h2>
            <pre>{previewText}</pre>
          </div>
        )}
      </div>
    </>
  )
}

export default App
