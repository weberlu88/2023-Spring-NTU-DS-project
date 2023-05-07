import { useState, useEffect } from 'react'

function App() {
  const [tableData, setTableData] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/list_local')
      .then(response => response.json())
      .then(data => setTableData(data['files']))
      .catch(error => console.error(error));
  }, []);

  return (
    <>
      <div>
        <h1>島嶼大學各科系面試資料</h1>
        <table>
          <thead>
            <tr>
              <th>Year</th>
              <th>Department</th>
              <th>Title</th>
              <th>File URL</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map(item => (
              <tr key={item.id}>
                <td>{item.year}</td>
                <td>{item.department}</td>
                <td>{item.title}</td>
                <td><a href={item.fileurl}>點我下載</a></td>
                {/* <td><a href='http://www.example.com/'>click to redirect</a></td> */}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}

export default App
