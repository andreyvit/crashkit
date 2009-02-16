package com.yoursway.feedback.internal;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

public class FeedbackCommunicator {

	private final String host;

	private final int port;

	private final String productName;

	public FeedbackCommunicator(String accountName, String productName) {
		if (accountName == null)
			throw new NullPointerException("accountName is null");
		if (productName == null)
			throw new NullPointerException("productName is null");

		String host = determineHost(accountName);
		if (host.contains(":")) {
			this.host = host.substring(0, host.lastIndexOf(':'));
			this.port = Integer.parseInt(host
					.substring(host.lastIndexOf(':') + 1));
		} else {
			this.host = host;
			this.port = 80;
		}
		this.productName = productName;
	}

	public ClientInfo obtainNewClientIdAndCookie() throws IOException {
		Map<String, String> result = get(obtainClientInfoUrl());
		String id = result.get("client_id");
		String cookie = result.get("client_cookie");
		if (id == null || cookie == null)
			throw new IOException("Invalid response: missing id and/or cookie");
		return new ClientInfo(id, cookie);
	}

	public void sendReport(ClientInfo clientInfo, Map<String, String> data) throws IOException {
		data = new HashMap<String, String>(data);
		data.put("client_id", clientInfo.id());
		data.put("client_cookie", clientInfo.cookie());
		String payload = RequestString.encode(data);

		System.out.println("Trying to send bug report to " + host + "...");
		URL url = postReportUrl(clientInfo);
		post(url, payload);
	}

	private Map<String, String> get(URL url) throws IOException {
		HttpURLConnection urlConn = (HttpURLConnection) url.openConnection();
		urlConn.setDoInput(true);
		urlConn.setUseCaches(false);
		int code = urlConn.getResponseCode();
		if (code < 200 || code >= 300)
			throw new IOException("Response indicated failure: code " + code);
		InputStream in = urlConn.getInputStream();
		String result = YsFileUtils.readAsString(in);
		in.close();
		return RequestString.decode(result);
	}

	private Map<String, String> post(URL url, String payload)
			throws IOException {
		HttpURLConnection urlConn = (HttpURLConnection) url.openConnection();
		urlConn.setDoInput(true);
		urlConn.setDoOutput(true);
		urlConn.setUseCaches(false);
		urlConn.setRequestProperty("Content-Type",
				"application/x-www-form-urlencoded");
		OutputStream out = urlConn.getOutputStream();
		YsFileUtils.writeString(out, payload);
		out.flush();
		out.close();
		int code = urlConn.getResponseCode();
		if (code < 200 || code >= 300)
			throw new IOException("Response indicated failure: code " + code);
		InputStream in = urlConn.getInputStream();
		String result = YsFileUtils.readAsString(in);
		in.close();
		return RequestString.decode(result);
	}

	private static String determineHost(String accountName) {
		String override = System.getProperty(accountName.replaceAll(
				"[^a-zA-Z0-9.]+", "").toLowerCase()
				+ ".feedback.host");
		if (override != null)
			return override;
		override = System.getenv(accountName.replaceAll("[^a-zA-Z0-9]+", "_")
				.toUpperCase()
				+ "_FEEDBACK_HOST");
		if (override != null && override.trim().length() > 0)
			return override;
		else
			return accountName;
	}

	public URL feedbackPageUrl() {
		try {
			return new URL("http", host, port, "/" + productName + "/feedback/");
		} catch (MalformedURLException e) {
			throw new AssertionError(e);
		}
	}

	public URL postReportUrl(ClientInfo clientInfo) {
		try {
			return new URL("http", host, port, "/" + productName
					+ "/post-report/" + clientInfo.id());
		} catch (MalformedURLException e) {
			throw new AssertionError(e);
		}
	}

	public URL obtainClientInfoUrl() {
		try {
			return new URL("http", host, port, "/" + productName
					+ "/obtain-client-id");
		} catch (MalformedURLException e) {
			throw new AssertionError(e);
		}
	}

}
