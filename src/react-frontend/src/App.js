import logo from './logo.svg';
import './App.css';
import {BrowserRouter as Router, Routes,Route } from 'react-router-dom'
import Recommender from './components/recommender';


function App() {
  
  return (
    <div className="App">
      <header className="App-header">
      <Router>
        <Routes>
          <Route path = "/" element = {<Recommender/>}/>
        </Routes>
      </Router>


      </header>
    </div>
  );
}

export default App;
