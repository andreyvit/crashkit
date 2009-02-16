package com.yoursway.feedback;

import java.util.Map;

public class Detail {
	
	private final String key;
	private final String value;

	public Detail(String key, Object value) {
		this.key = key;
		this.value = value.toString();
	}
	
	public void addTo(Map<String, String> data, String prefix) {
		data.put(prefix + key, value);
	}

}
