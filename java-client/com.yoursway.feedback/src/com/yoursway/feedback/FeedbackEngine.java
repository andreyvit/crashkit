package com.yoursway.feedback;

public interface FeedbackEngine {

	public void minorVisualIssue(Throwable optionalCause,
			String userFriendlyDescription,
			String optionalDeveloperFriendlyDescription, Detail... details);

	public void majorUserInitiatedActionIssue(Throwable optionalCause,
			String userFriendlyDescription,
			String optionalDeveloperFriendlyDescription, Detail... details);

	public void majorBackgroundProcessingIssue(Throwable optionalCause,
			String userFriendlyDescription,
			String optionalDeveloperFriendlyDescription, Detail... details);

	public void silentRecovery(Throwable optionalCause,
			String developerFriendlyDescription, Detail... details);

}
