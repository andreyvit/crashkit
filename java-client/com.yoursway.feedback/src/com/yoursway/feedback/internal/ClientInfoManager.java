package com.yoursway.feedback.internal;

import java.io.IOException;

public class ClientInfoManager {
	
	private final FeedbackStorage storage;
	
	private ClientInfo cachedInfo;

	private final FeedbackCommunicator communicator;
	
	public ClientInfoManager(FeedbackStorage storage, FeedbackCommunicator communicator) {
		if (storage == null)
			throw new NullPointerException("storage is null");
		if (communicator == null)
			throw new NullPointerException("communicator is null");
		this.storage = storage;
		this.communicator = communicator;
	}
	
	public synchronized ClientInfo get() throws IOException {
		if (cachedInfo == null) {
			cachedInfo = storage.readClientInfo();
			if (cachedInfo == null) {
				cachedInfo = communicator.obtainNewClientIdAndCookie();
				storage.writeClientInfo(cachedInfo);
			}
		}
		return cachedInfo;
	}

}
