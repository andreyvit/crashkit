package com.yoursway.feedback.internal;

public class ClientInfo {

	private final String id;
	private final String cookie;

	public ClientInfo(String id, String cookie) {
		if (id == null)
			throw new NullPointerException("id is null");
		if (cookie == null)
			throw new NullPointerException("cookie is null");
		this.id = id;
		this.cookie = cookie;
	}

	public String id() {
		return id;
	}

	public String cookie() {
		return cookie;
	}

}
