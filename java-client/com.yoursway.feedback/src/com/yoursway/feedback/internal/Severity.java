package com.yoursway.feedback.internal;

public enum Severity {

	MINOR_VISUAL("minor-visual"),

	MAJOR_USER_ACTION("major-user"),

	MAJOR_BACKGROUND("major-background"),

	SILENT_RECOVERY("silent-recovery"),

	;

	final String apiName;

	private Severity(String apiName) {
		this.apiName = apiName;
	}
	
}
