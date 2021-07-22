import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './table.css';

const URL = 'http://127.0.0.1:5000/flask/GroupTable'

const Table = () => {
    const [group, groupDetails] = React.useState([])

    React.useEffect(() => {
        getData()
    }, [])

    const getData = async () => {

        const response = await axios.get(URL)
        groupDetails(response.data)
    }

 

    const renderHeader = () => {
        let headerElement = ['DEVICE_NAME',  'IP','PORT','TIMESTAMP' ,'MPRECIDENCE','LAST_PING']

        return headerElement.map((key, index) => {
            return <th key={index}>{key.toUpperCase()}</th>
        })
    }

    const renderBody = () => {
        return group && group.map(({ DEVICE_NAME,IP , PORT,TIMESTAMP,MPRECIDENCE,LAST_PING,id}) => {
            return (
                <tr key={id}>
                    
                    <td>{DEVICE_NAME}</td>
                    <td>{IP}</td>
                    <td>{PORT}</td>
                    <td>{TIMESTAMP}</td>
                    <td>{MPRECIDENCE}</td>
                    <td>{LAST_PING}</td>
                </tr>
            )
        })
    }

    return (
        <>
            <h1 id='title'>GROUP TABLE</h1>
            <table id='display'>
                <thead>
                    <tr>{renderHeader()}</tr>
                </thead>
                <tbody>
                    {renderBody()}
                </tbody>
            </table>
        </>
    )
}
export default Table;


