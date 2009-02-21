package com.yoursway.feedback;

public interface FeedbackEngine {
    
    public void bug(Throwable cause);
    
    public void major(Throwable cause);
    
}
