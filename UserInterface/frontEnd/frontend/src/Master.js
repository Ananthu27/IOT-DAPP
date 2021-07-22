import React from "react";
import './index.css';


class Master extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        master: [],
        isLoaded: false
      };
    }
  
    componentDidMount() {
      fetch("http://127.0.0.1:5000/flask/Device/Master1")
        .then((res) => res.json())
        .then((result) => {
          this.setState({
            isLoaded: true,
            master: result
          });
        });
    }
  
    render() {
      const { isLoaded, master } = this.state;
  
      if (!isLoaded) {
        return <div>Loading ... </div>;
      } else {
        return (
          <div>
            <div className="App">
            <h1>Device</h1>
              <ul>
                {master.map((device) => (
                  <div className="gro">
                  <h3>{device.exist}</h3>
                      <h3>Device Name:{device.device_name}</h3>
                      <h3>Master: {device.master}</h3>
                      <h3>{device.future_master}</h3>
                      {/* <h3>{device.public_key}</h3> */}
                      <h3>Public Ip:{device.public_ip}</h3> 
                      <h3></h3>                  
                  </div>
                ))}
              </ul>
          </div>
          </div>
        );
      }
    }
  }
  
  export default Master;