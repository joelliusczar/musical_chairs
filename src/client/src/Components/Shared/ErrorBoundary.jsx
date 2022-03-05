import React from "react";
import PropTypes from "prop-types";

export default class ErrorBoundary extends React.Component {
	constructor(props) {
		super(props);
		this.state = { error: null, errorInfo: null};
	}

	componentDidCatch(error, errorInfo) {
		this.setState({
			error,
			errorInfo,
		});

		this.props.setErrorInfo && this.props.setErrorInfo({...this.state});
	}

	render() {
		if(this.state.errorInfo) {
			return null;
		}
		return this.props.children;
	}
}

ErrorBoundary.propTypes = {
	setErrorInfo: PropTypes.func,
	children: PropTypes.arrayOf(PropTypes.node),
};