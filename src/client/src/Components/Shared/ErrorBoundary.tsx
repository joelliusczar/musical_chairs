import React from "react";


type ErrorBoundaryProps = {
	setErrorInfo: (info: any) => any,
	children: React.ReactNode
};

type ErrorBoundaryState = {
	error: any,
	errorInfo: any
};

export default class ErrorBoundary extends React.Component<
	ErrorBoundaryProps,ErrorBoundaryState>
{
	constructor(props: ErrorBoundaryProps) {
		super(props);
		this.state = { error: null, errorInfo: null};
	}

	componentDidCatch(error: any, errorInfo: any) {
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
