package com.yoursway.feedback;

import com.yoursway.feedback.internal.FeedbackCommunicator;
import com.yoursway.feedback.internal.FeedbackEngineImpl;
import com.yoursway.feedback.internal.FeedbackStorage;

public class FeedbackConfiguration {

	private final String userFriendlyProductName;
	private final String feedbackServiceAccountName;
	private final String feedbackServiceProductName;
	private final String developerFriendlyProductVersion;

	public FeedbackConfiguration(String userFriendlyProductName, String developerFriendlyProductVersion,
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

	public FeedbackEngine create() {
		return new FeedbackEngineImpl(userFriendlyProductName, developerFriendlyProductVersion,
				new FeedbackStorage(userFriendlyProductName),
				new FeedbackCommunicator(feedbackServiceAccountName,
						feedbackServiceProductName));
	}

}
