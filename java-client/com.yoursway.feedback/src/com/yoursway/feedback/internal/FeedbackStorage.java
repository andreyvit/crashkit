package com.yoursway.feedback.internal;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class FeedbackStorage {
    
    private final File settingsFile;
    private final File reportsFolder;
    private final File inProgressReportsFolder;
    
    public FeedbackStorage(String friendlyProductName) {
        if (friendlyProductName == null)
            throw new NullPointerException("friendlyProductName is null");
        File baseFolder = new File(OS.current.applicationDataFolder(friendlyProductName), "Feedback");
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
            Map<String, String> data = RequestString.decode(YsFileUtils.readAsString(settingsFile));
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
    
    public void addReport(Map<String, String> info, List<ExceptionInfo> exceptions, Map<String, String> data,
            Map<String, String> env, String role) {
        String hash = YsDigest.sha1(RequestString.encode(info) + "|" + RequestString.encode(data) + "|"
                + RequestString.encode(env));
        JSONObject json = encodeInfo(info, exceptions, data, env);
        json.put("role", role);
        json.put("hash", hash);
        merge(json);
    }
    
    private JSONObject encodeInfo(Map<String, String> info, List<ExceptionInfo> exceptions,
            Map<String, String> data, Map<String, String> env) throws JSONException {
        JSONObject obj = encode(info);
        obj.put("data", encode(data));
        obj.put("env", encode(env));
        JSONArray exc = new JSONArray();
        for (ExceptionInfo ex : exceptions)
            exc.put(ex.encodeAsJson());
        obj.put("exceptions", exc);
        obj.put("userActionOrScreenNameOrBackgroundProcess", "");
        return obj;
    }
    
    private JSONObject encode(Map<String, String> data) throws JSONException {
        JSONObject obj = new JSONObject();
        for (Map.Entry<String, String> entry : data.entrySet())
            obj.put(entry.getKey(), entry.getValue());
        return obj;
    }
    
    private synchronized void merge(JSONObject obj) {
        File file = new File(reportsFolder, obj.get("hash") + ".json");
        try {
            file.getParentFile().mkdirs();
            if (!file.createNewFile()) {
                JSONObject existing = new JSONObject(YsFileUtils.readAsString(file));
                obj.put("count", Integer.toString(Integer.parseInt(existing.getString("count"))
                        + Integer.parseInt(obj.getString("count"))));
            }
        } catch (NumberFormatException e) {
        } catch (IOException e) {
        }
        try {
            YsFileUtils.writeString(file, obj.toString());
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
            JSONObject data = new JSONObject(YsFileUtils.readAsString(source));
            merge(data);
        } catch (IOException e) {
        }
        source.delete();
    }
    
    public void deleteClientInfo() {
        settingsFile.delete();
    }
    
}
