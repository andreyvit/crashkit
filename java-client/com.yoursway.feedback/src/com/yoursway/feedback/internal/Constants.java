package com.yoursway.feedback.internal;

public class Constants {
    
    // non-static so that Eclipse does not issue the stupid "dead code" warnings
    private static final boolean DEBUG = Boolean.parseBoolean("false");
    
    public static final boolean DEBUG_SCHEDULING = DEBUG;
    
    /**
     * The maximum time an exception waits in the queue since the last delivery
     * attempt (or since its initial addition) until a new delivery is
     * attempted.
     */
    public static final long MAXIMUM_WAIT_TIME = (DEBUG ? 10 : 5 * 60) * 1000;
    
    /**
     * Wait this number of milliseconds after a new exception has been recorder
     * before attempting a delivery.
     */
    public static final long NEW_EXCEPTION_DELAY = (DEBUG ? 1 : 5) * 1000;
    
    /**
     * Wait this number of milliseconds after a failed delivery attempt until
     * trying again.
     */
    public static final long FAILED_DELIVERY_RETRY_DELAY = (DEBUG ? 2 : 2 * 60) * 1000;
    
    /**
     * Wait this number of milliseconds after a startup until trying to send the
     * first exception report.
     */
    public static final long STARTUP_DELAY = (DEBUG ? 2 : 60) * 1000;
    
    /**
     * If a report is in “sending in progress” state for this long, put it into
     * a “to be sent” state. This delay is required because multiple instances
     * of the application may be running.
     */
    public static final long REQUEUE_IN_PROGRESS_REPORT_IN = (DEBUG ? 5 : 10 * 60) * 1000;
    
}
