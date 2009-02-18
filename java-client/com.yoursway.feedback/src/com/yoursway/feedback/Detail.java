package com.yoursway.feedback;

import java.util.Map;

public class Detail {
	
	private final String key;
	private final String value;
	private final Throwable valueCalculationError;

	public Detail(String key, Object value) {
		this.key = key;
		String valueAsString;
		Throwable throwable = null;
		try {
			valueAsString = String.valueOf(value);
		} catch (Throwable e) {
			valueAsString = simpleNameOf(value.getClass());
			throwable = e;
		}
		this.value = valueAsString;
		this.valueCalculationError = throwable;
	}
	
	public void addTo(FeedbackEngine engine, Map<String, String> data, String prefix) {
		data.put(prefix + key, value);
		if (valueCalculationError != null)
			engine.silentRecovery(valueCalculationError, "Exception in toString() while processing another bug report");
	}

	private static String simpleNameOf(Class<?> klass) {
	    String simpleName = klass.getSimpleName();
	    if (simpleName.length() == 0) {
	        String fullName = klass.getName();
	        simpleName = fullName.substring(fullName.lastIndexOf('.') + 1);
	    }
	    return simpleName;
	}

}
