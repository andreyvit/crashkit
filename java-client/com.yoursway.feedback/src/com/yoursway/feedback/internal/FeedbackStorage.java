package com.yoursway.feedback.internal;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class FeedbackStorage {

	private final File settingsFile;
	private final File reportsFolder;
	private final File inProgressReportsFolder;

	public FeedbackStorage(String friendlyProductName) {
		if (friendlyProductName == null)
			throw new NullPointerException("friendlyProductName is null");
		File baseFolder = new File(OS.current
				.applicationDataFolder(friendlyProductName), "Feedback");
		settingsFile = new File(baseFolder, "settings.dat");
		reportsFolder = new File(baseFolder, "Reports");
		inProgressReportsFolder = new File(baseFolder, "Reports On The Way");
	}

	private void requeueAbandonedFiles() {
		File[] leftoverFiles = inProgressReportsFolder.listFiles();
		if (leftoverFiles == null)
			return;
		long now = System.currentTimeMillis();
		for (File source : leftoverFiles) {
			if (source.lastModified() < now - 10 * 60 * 1000) {
				requeue(source);
			}
		}
	}

	public ClientInfo readClientInfo() {
		try {
			Map<String, String> data = RequestString.decode(YsFileUtils
					.readAsString(settingsFile));
			String clientId = data.get("client_id");
			String clientCookie = data.get("client_cookie");
			if (clientId == null || clientCookie == null)
				return null;
			return new ClientInfo(clientId, clientCookie);
		} catch (IOException e) {
			return null;
		}
	}

	public void writeClientInfo(ClientInfo info) {
		HashMap<String, String> data = new HashMap<String, String>();
		data.put("client_id", info.id());
		data.put("client_cookie", info.cookie());
		settingsFile.getParentFile().mkdirs();
		try {
			YsFileUtils.writeString(settingsFile, RequestString.encode(data));
		} catch (IOException e) {
			// oops, but we can do nothing useful here
		}
	}

	public void addReport(Map<String, String> data) {
		String hash = YsDigest.sha1(RequestString.encode(data));
		int timestamp = (int) (System.currentTimeMillis() / 1000);
		data.put("count", "1");
		data.put("first_occurrence_at", Integer.toString(timestamp));
		data.put("hash", hash);
		data.put("last_occurrence_at", Integer.toString(timestamp));
		merge(data);
	}

	private synchronized void merge(Map<String, String> data) {
		File file = new File(reportsFolder, data.get("hash") + ".report");
		try {
			file.getParentFile().mkdirs();
			if (!file.createNewFile()) {
				Map<String, String> existing = RequestString.decode(YsFileUtils
						.readAsString(file));
				data.put("count", Integer.toString(Integer.parseInt(existing
						.get("count"))
						+ Integer.parseInt(data.get("count"))));
				data.put("first_occurrence_at", Long.toString(Math.min(Long
						.parseLong(existing.get("first_occurrence_at")), Long
						.parseLong(data.get("first_occurrence_at")))));
				data.put("last_occurrence_at", Long.toString(Math.max(Long
						.parseLong(existing.get("last_occurrence_at")), Long
						.parseLong(data.get("last_occurrence_at")))));
			}
		} catch (NumberFormatException e) {
		} catch (IOException e) {
		}
		try {
			YsFileUtils.writeString(file, RequestString.encode(data));
		} catch (IOException e) {
			e.printStackTrace(System.err);
		}
	}

	public synchronized PersistentReport obtainReportToSend() {
		requeueAbandonedFiles();
		File[] files = reportsFolder.listFiles();
		if (files == null || files.length == 0)
			return null;
		for (File source : files) {
			inProgressReportsFolder.mkdirs();
			File target = new File(inProgressReportsFolder, source.getName());
			if (target.exists())
				continue;
			source.setLastModified(System.currentTimeMillis());
			source.renameTo(target);
			return new PersistentReport(target, this);
		}
		return null;
	}

	void requeue(File source) {
		try {
			Map<String, String> data = RequestString.decode(YsFileUtils
					.readAsString(source));
			merge(data);
		} catch (IOException e) {
		}
		source.delete();
	}

	public void deleteClientInfo() {
		settingsFile.delete();
	}

}
