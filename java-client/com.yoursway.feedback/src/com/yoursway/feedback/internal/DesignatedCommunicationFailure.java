package com.yoursway.feedback.internal;

import java.io.IOException;

public class DesignatedCommunicationFailure extends IOException {

	private static final long serialVersionUID = 1L;
	private final String response;
	
	public DesignatedCommunicationFailure(String response) {
		super(response);
		this.response = response;
	}
	
	public boolean is(String response) {
		return this.response.equalsIgnoreCase(response);
	}
	
}
