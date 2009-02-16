package com.yoursway.feedback.internal;

import java.io.File;
import java.io.IOException;
import java.util.Map;

public class PersistentReport {
	
	private final File file;
	private final FeedbackStorage storage;

	public PersistentReport(File file, FeedbackStorage storage) {
		if (file == null)
			throw new NullPointerException("file is null");
		if (storage == null)
			throw new NullPointerException("storage is null");
		this.file = file;
		this.storage = storage;
	}
	
	public Map<String, String> read() throws IOException {
		return RequestString.decode(YsFileUtils.readAsString(file));
	}
	
	public void delete() {
		file.delete();
	}

	public void requeue() {
		storage.requeue(file);
	}
	
}
