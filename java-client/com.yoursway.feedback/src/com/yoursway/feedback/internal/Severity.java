package com.yoursway.feedback.internal;

public enum Severity {
    
    NORMAL("normal"),

    MAJOR("major"),

    ;
    
    final String apiName;
    
    private Severity(String apiName) {
        this.apiName = apiName;
    }
    
}
