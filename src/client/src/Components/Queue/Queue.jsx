import React from 'react';
import { useParams } from "react-router-dom";

export default function Queue() {
    let { station } = useParams();
    return (<h1>queue: {station}</h1>)
}