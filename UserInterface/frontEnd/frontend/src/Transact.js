import React from "react";
import { Card} from 'antd';
import './index.css';
import  ReactDOM  from "react-dom";

class Transact extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      transaction: [],
      isLoaded: false
    };
  }

  componentDidMount() {
    fetch("http://127.0.0.1:5000/flask/Transaction/GroupCreationReceipt")
      .then((res) => res.json())
      .then((result) => {
        this.setState({
          isLoaded: true,
          transaction: result
        });
      });
  }
render() {
  const { isLoaded, transaction } = this.state;

  if (!isLoaded) {
    return <div>Loading ... </div>;
  } else {


  return (
    <div className="App">
      <h1>Transaction Details</h1>
      <div className="groups">
        {transaction &&
          transaction.map((transact, index) => {
            return (
              <div  key={index}>
                {/* <h2>Transaction {index + 1}</h2> */}
                <div >
                  <h3>TransactionIndex: {transact.transactionIndex}</h3>
                  <h3>BlockNumber: {transact.blockNumber}</h3>
                  <h3>From address:{transact.from}</h3>
                  <h3>To address :{transact.to}</h3>
                  <h3> Gasused: {transact.gasUsed}</h3>
                  <h3>CumulativeGasUsed : {transact.cumulativeGasUsed}</h3>
                  <h3>Status: {transact.status}</h3>
                  <div>
                    {transact.logs.map((log, q) => {
                      return (
                        <div className="site-card-wrapper" key={q}>
                          <div className="group">
                            <Card hoverable bordered={false} style={{ width: 600 }}>
                            <h1>Log {q + 0}</h1>
                            <h3>Logindex:{log.logIndex}</h3>
                            <h3>TransactionIndex:{log.transactionIndex}</h3>
                            <h3>BlockNumber:{log.blockNumber}</h3>
                            <h3>Address:{log.address}</h3>
                            {/* <h3>Data:{log.data}</h3> */}
                            <h3>type::{log.type}</h3>
                            </Card>
                        </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}}
}

export default Transact;
ReactDOM.render(
  <Transact/>,
document.getElementById('root')
);