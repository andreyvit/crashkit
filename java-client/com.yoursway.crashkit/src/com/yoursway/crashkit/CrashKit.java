package com.yoursway.crashkit;

import java.lang.Thread.UncaughtExceptionHandler;

import com.yoursway.crashkit.internal.CrashKitImpl;
import com.yoursway.crashkit.internal.ServerConnection;
import com.yoursway.crashkit.internal.model.Repository;
import com.yoursway.crashkit.internal.model.Severity;

public abstract class CrashKit {
    
    private static CrashKit applicationKit;
    
    public static void bug(Throwable throwable) {
        if (applicationKit == null)
            throwable.printStackTrace(System.err);
        else
            applicationKit.report(Severity.NORMAL, throwable);
    }
    
    public static void major(Throwable throwable) {
        if (applicationKit == null)
            throwable.printStackTrace(System.err);
        else
            applicationKit.report(Severity.MAJOR, throwable);
    }
    
    public static CrashKit connectApplication(String userFriendlyProductName,
            String developerFriendlyProductVersion, String feedbackServiceAccountName,
            String feedbackServiceProductName, String[] claimedPackages) {
        CrashKit kit = new CrashKitImpl(userFriendlyProductName, developerFriendlyProductVersion,
                claimedPackages, new Repository(userFriendlyProductName), new ServerConnection(
                        feedbackServiceAccountName, feedbackServiceProductName));
        applicationKit = kit;
        Thread.setDefaultUncaughtExceptionHandler(new UncaughtExceptionHandler() {
            public void uncaughtException(Thread t, Throwable e) {
                major(e);
            }
        });
        return kit;
    }
    
    protected abstract void report(Severity severity, Throwable cause);
    
}
