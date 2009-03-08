package com.yoursway.feedback;

import com.yoursway.feedback.internal.ServerConnection;
import com.yoursway.feedback.internal.FeedbackProductImpl;
import com.yoursway.feedback.internal.model.Repository;

public class FeedbackProductFactory {
    
    private final String userFriendlyProductName;
    private final String feedbackServiceAccountName;
    private final String feedbackServiceProductName;
    private final String developerFriendlyProductVersion;
    private boolean useByDefault = false;
    
    public FeedbackProductFactory(String userFriendlyProductName, String developerFriendlyProductVersion,
            String feedbackServiceAccountName, String feedbackServiceProductName) {
        if (userFriendlyProductName == null)
            throw new NullPointerException("userFriendlyProductName is null");
        if (developerFriendlyProductVersion == null)
            throw new NullPointerException("developerFriendlyProductVersion is null");
        if (feedbackServiceAccountName == null)
            throw new NullPointerException("feedbackServiceAccountName is null");
        if (feedbackServiceProductName == null)
            throw new NullPointerException("feedbackServiceProductName is null");
        this.userFriendlyProductName = userFriendlyProductName;
        this.developerFriendlyProductVersion = developerFriendlyProductVersion;
        this.feedbackServiceAccountName = feedbackServiceAccountName;
        this.feedbackServiceProductName = feedbackServiceProductName;
    }
    
    public FeedbackProductFactory useByDefault() {
        useByDefault = true;
        return this;
    }
    
    public FeedbackProduct create() {
        FeedbackProductImpl engine = new FeedbackProductImpl(userFriendlyProductName,
                developerFriendlyProductVersion, new Repository(userFriendlyProductName),
                new ServerConnection(feedbackServiceAccountName, feedbackServiceProductName));
        if (useByDefault)
            Feedback.setDefaultProduct(engine);
        return engine;
    }
    
}
