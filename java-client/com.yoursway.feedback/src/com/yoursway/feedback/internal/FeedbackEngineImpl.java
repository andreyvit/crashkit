package com.yoursway.feedback.internal;

import java.io.IOException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TimeZone;

import com.yoursway.feedback.Detail;
import com.yoursway.feedback.FeedbackEngine;
import com.yoursway.feedback.exceptions.NullReportedExceptionFailure;

public class FeedbackEngineImpl implements FeedbackEngine {
    
    private final FeedbackStorage storage;
    private final FeedbackCommunicator communicator;
    private final ClientInfoManager clientInfoManager;
    private final String productName;
    private final String productVersion;
    
    public FeedbackEngineImpl(String productName, String productVersion, FeedbackStorage storage,
            FeedbackCommunicator communicator) {
        if (productName == null)
            throw new NullPointerException("productName is null");
        if (productVersion == null)
            throw new NullPointerException("productVersion is null");
        if (storage == null)
            throw new NullPointerException("storage is null");
        if (communicator == null)
            throw new NullPointerException("communicator is null");
        this.productName = productName;
        this.productVersion = productVersion;
        this.storage = storage;
        this.communicator = communicator;
        this.clientInfoManager = new ClientInfoManager(storage, communicator);
        new FeedbackPostingThread().start();
    }
    
    private void report(Severity severity, Throwable cause) {
        if (cause == null)
            cause = new NullReportedExceptionFailure();
        Map<String, String> info = encodeExceptionInfo(severity, cause);
        Map<String, String> data = collectData(cause);
        Map<String, String> env = collectEnvironmentInfo();
        List<ExceptionInfo> exceptions = collectExceptions(cause);
        storage.addReport(info, exceptions, data, env);
        synchronized (this) {
            notifyAll();
        }
    }
    
    private Map<String, String> encodeExceptionInfo(Severity severity, Throwable cause) {
        Map<String, String> data = new HashMap<String, String>();
        data.put("severity", severity.apiName);
        data.put("count", "1");
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
        dateFormat.setCalendar(Calendar.getInstance(TimeZone.getTimeZone("GMT")));
        data.put("date", dateFormat.format(new Date()));
        return data;
    }
    
    @SuppressWarnings("unchecked")
    private Map<String, String> collectData(Throwable cause) {
        Map<String, String> data = new HashMap<String, String>();
        for (Throwable throwable = cause; throwable != null; throwable = throwable.getCause()) {
            try {
                Method method = throwable.getClass().getMethod("feedbackDetails");
                if (!Modifier.isStatic(method.getModifiers())
                        && Map.class.isAssignableFrom(method.getReturnType())) {
                    Map<String, Object> map = (Map<String, Object>) method.invoke(throwable);
                    if (map != null) {
                        for (Map.Entry<String, Object> entry : map.entrySet())
                            new Detail(entry.getKey(), entry.getValue()).addTo(this, data);
                    }
                }
            } catch (Throwable e) {
            }
        }
        return data;
    }
    
    private List<ExceptionInfo> collectExceptions(Throwable cause) {
        List<ExceptionInfo> result = new ArrayList<ExceptionInfo>();
        processException(cause, null, result);
        return result;
    }
    
    private void processException(Throwable throwable, Throwable wrapper, List<ExceptionInfo> result) {
        Throwable cause = throwable.getCause();
        if (cause != null)
            processException(cause, throwable, result);
        result.add(encode(throwable, wrapper));
    }
    
    private ExceptionInfo encode(Throwable throwable, Throwable wrapper) {
        StackTraceElement[] ours = throwable.getStackTrace();
        int lastOurs = ours.length - 1;
        if (wrapper != null) {
            StackTraceElement[] theirs = wrapper.getStackTrace();
            int lastTheirs = theirs.length - 1;
            while (lastOurs >= 0 && lastTheirs >= 0 && ours[lastOurs].equals(theirs[lastTheirs])) {
                lastOurs--;
                lastTheirs--;
            }
        }
        
        StackTraceElement[] trace = new StackTraceElement[lastOurs + 1];
        System.arraycopy(ours, 0, trace, 0, lastOurs + 1);
        ExceptionInfo info = new ExceptionInfo(simpleNameOf(throwable.getClass()), throwable.getMessage(),
                trace);
        return info;
    }
    
    private Map<String, String> collectEnvironmentInfo() {
        Map<String, String> data = new HashMap<String, String>();
        putSystemProperty(data, "java_version", "java.version");
        data.put("product_name", productName);
        data.put("product_version", productVersion);
        putSystemProperty(data, "os_name", "os.name");
        putSystemProperty(data, "os_version", "os.version");
        putSystemProperty(data, "os_arch", "os.arch");
        putSystemProperty(data, "eclipse_build_id", "eclipse.buildId");
        putSystemProperty(data, "eclipse_product", "eclipse.product");
        putSystemProperty(data, "osgi_nl", "osgi.nl");
        putSystemProperty(data, "osgi_os", "osgi.os");
        putSystemProperty(data, "osgi_ws", "osgi.ws");
        data.put("cpu_count", Integer.toString(Runtime.getRuntime().availableProcessors()));
        return data;
    }
    
    private void putSystemProperty(Map<String, String> data, String key, String property) {
        String value = System.getProperty(property);
        if (value != null && value.length() > 0)
            data.put(key, value);
    }
    
    public void major(Throwable cause) {
        if (cause != null)
            report(Severity.MAJOR, cause);
    }
    
    public void bug(Throwable cause) {
        if (cause != null)
            report(Severity.NORMAL, cause);
    }
    
    class FeedbackPostingThread extends Thread {
        
        long lastFailureTimeOrMin = Long.MIN_VALUE;
        
        long lastEmptyQueueTimeOrMin = Long.MIN_VALUE;
        
        public FeedbackPostingThread() {
            setName(productName + " Bug Reporter");
            setDaemon(true);
        }
        
        @Override
        public void run() {
            Object master = FeedbackEngineImpl.this;
            while (true) {
                long now = System.currentTimeMillis();
                long minCheckTime = lastFailureTimeOrMin + 5000;
                if (now > minCheckTime) {
                    try {
                        PersistentReport report = storage.obtainReportToSend();
                        if (report == null) {
                            lastEmptyQueueTimeOrMin = now;
                            System.out.println("No bug reports to send.");
                        } else {
                            lastEmptyQueueTimeOrMin = Long.MIN_VALUE;
                            try {
                                try {
                                    communicator.sendReport(clientInfoManager.get(), "[" + report.read()
                                            + "]");
                                    System.out.println("Report sent!");
                                    report.delete();
                                    lastFailureTimeOrMin = Long.MIN_VALUE;
                                } catch (DesignatedCommunicationFailure e) {
                                    handleDesignatedFailure(e);
                                }
                            } catch (IOException e) {
                                report.requeue();
                                System.out.println("Failed sending bug report: " + e.getMessage());
                                lastFailureTimeOrMin = now;
                            }
                        }
                    } catch (Throwable e) {
                        e.printStackTrace(System.err);
                    }
                }
                long nextCheck = Math.max(lastFailureTimeOrMin + 5000, Math.max(now,
                    lastEmptyQueueTimeOrMin + 60000));
                long delay = nextCheck - now;
                if (delay > 0)
                    synchronized (master) {
                        try {
                            master.wait(delay);
                        } catch (InterruptedException e) {
                        }
                    }
            }
        }
        
    }
    
    public void handleDesignatedFailure(DesignatedCommunicationFailure e) {
        if (e.is("invalid-client-id"))
            clientInfoManager.reset();
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
