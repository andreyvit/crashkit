package com.yoursway.feedback.internal;

import org.json.JSONArray;
import org.json.JSONObject;

public class ExceptionInfo {
    
    private final String name;
    private final String message;
    private final StackTraceElement[] stackTrace;
    
    public ExceptionInfo(String name, String message, StackTraceElement[] stackTrace) {
        if (name == null)
            throw new NullPointerException("name is null");
        if (stackTrace == null)
            throw new NullPointerException("stackTrace is null");
        this.name = name;
        this.message = message;
        this.stackTrace = stackTrace;
    }
    
    public JSONObject encodeAsJson() {
        JSONObject obj = new JSONObject();
        obj.put("name", name);
        if (message == null)
            obj.put("message", "");
        else
            obj.put("message", message);
        JSONArray locations = new JSONArray();
        for (StackTraceElement el : stackTrace)
            locations.put(encode(el));
        obj.put("locations", locations);
        return obj;
    }
    
    private JSONObject encode(StackTraceElement el) {
        JSONObject obj = new JSONObject();
        String classAndPackage = el.getClassName();
        int pos = classAndPackage.lastIndexOf('.');
        String className = (pos >= 0 ? classAndPackage.substring(pos + 1) : classAndPackage);
        String packageName = (pos >= 0 ? classAndPackage.substring(0, pos) : "");
        obj.put("package", packageName);
        obj.put("class", className);
        obj.put("method", el.getMethodName());
        obj.put("line", el.getLineNumber());
        return obj;
    }
    
}
