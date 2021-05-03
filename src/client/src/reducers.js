import queueState from './Components/Queue/queue_state';
import { configureStore } from "@reduxjs/toolkit"


const reducer = {
  queueState: queueState
};

export default configureStore({reducer});