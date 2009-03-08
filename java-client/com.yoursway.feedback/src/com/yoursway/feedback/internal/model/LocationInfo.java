package com.yoursway.feedback.internal.model;

import com.yoursway.jyp.BeanEncoding;

public class LocationInfo {
    
    private final String fileName;
    private final String className;
    private final String methodName;
    private final int lineNumber;
    private final String packageName;
    
    public LocationInfo(StackTraceElement element) {
        fileName = element.getFileName();
        String classAndPackage = element.getClassName();
        int pos = classAndPackage.lastIndexOf('.');
        className = (pos >= 0 ? classAndPackage.substring(pos + 1) : classAndPackage);
        packageName = (pos >= 0 ? classAndPackage.substring(0, pos) : "");
        methodName = element.getMethodName();
        lineNumber = element.getLineNumber();
    }
    
    public LocationInfo(@BeanEncoding.Property("file") String fileName,
            @BeanEncoding.Property("package") String packageName,
            @BeanEncoding.Property("klass") String className,
            @BeanEncoding.Property("method") String methodName, @BeanEncoding.Property("line") int lineNumber) {
        this.fileName = fileName;
        this.packageName = packageName;
        this.className = className;
        this.methodName = methodName;
        this.lineNumber = lineNumber;
    }
    
    public String getFile() {
        return fileName;
    }
    
    public String getPackage() {
        return packageName;
    }
    
    @BeanEncoding.Property("class")
    public String getKlass() {
        return className;
    }
    
    public String getMethod() {
        return methodName;
    }
    
    public int getLine() {
        return lineNumber;
    }
    
}
