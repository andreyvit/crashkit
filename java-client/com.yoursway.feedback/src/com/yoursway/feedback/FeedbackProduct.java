package com.yoursway.feedback;

public interface FeedbackProduct {
    
    public void bug(Throwable cause);
    
    public void major(Throwable cause);
    
}
