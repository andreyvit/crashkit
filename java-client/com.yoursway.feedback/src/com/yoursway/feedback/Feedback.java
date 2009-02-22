package com.yoursway.feedback;

public class Feedback {
    
    private static FeedbackEngine engine;
    
    public static void bug(Throwable throwable) {
        if (engine == null)
            throwable.printStackTrace(System.err);
        else
            engine.bug(throwable);
    }
    
    static void setDefaultEngine(FeedbackEngine engine) {
        if (engine == null)
            throw new NullPointerException("engine is null");
        Feedback.engine = engine;
    }
    
}
