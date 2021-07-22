import React from "react";
import { Timeline } from "antd";
import './index.css';
import "antd/dist/antd.css";
import ReactDOM from 'react-dom';

class Logs extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        logs: [],
        isLoaded: false
      };
    }
  
    componentDidMount() {
      fetch("http://127.0.0.1:5000/flask/Logs/5")
        .then((res) => res.json())
        .then((result) => {
          this.setState({
            isLoaded: true,
            logs: result
          });
        });
    }
  
    render() {
      const { isLoaded, logs } = this.state;
  
      if (!isLoaded) {
        return <div>Loading ... </div>;
      } else {
        return (

          <div className="App">       
             <Timeline mode="alternate">
            <h1>Logs </h1>
                {logs.map((log) => (
                    <Timeline.Item color="green" > 
                       <h3>{log.content}</h3>
                      <h3>{log.dateTime}</h3>
                      {/* <p>{log.level}</p> */}
                    </Timeline.Item>
                ))}
            </Timeline>
          </div>
        );
      }
    }
  }
  
  export default Logs;

 