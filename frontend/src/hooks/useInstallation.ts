import { useState, useEffect, useCallback } from "react";
import { wsClient, WebSocketEvent } from "../api/websocket";
import { api } from "../api/client";

export interface LogLine {
  id: string;
  timestamp: string;
  type: string;
  message: string;
}

export function useInstallation() {
  const [isInstalling, setIsInstalling] = useState<boolean>(false);
  const [currentPackage, setCurrentPackage] = useState<string | null>(null);
  const [progressPercent, setProgressPercent] = useState<number>(0);
  const [currentStage, setCurrentStage] = useState<string>("idle");
  const [logs, setLogs] = useState<LogLine[]>([]);

  useEffect(() => {
    const unsubscribe = wsClient.subscribe((event: WebSocketEvent) => {
      const now = new Date().toLocaleTimeString();

      if (event.event_type.startsWith("Installation") || event.event_type.startsWith("Download")) {
        setLogs((prev) => [
          ...prev,
          {
            id: Math.random().toString(36).substr(2, 9),
            timestamp: now,
            type: event.event_type,
            message: event.message,
          },
        ]);
      }

      if (event.event_type === "InstallationStarted") {
        setIsInstalling(true);
        setCurrentPackage(event.payload.package_id);
        setProgressPercent(0);
        setCurrentStage("starting");
      } else if (event.event_type === "DownloadProgressUpdated") {
        setProgressPercent(event.payload.progress_percent * 0.4); // Download is 0-40% of total
        setCurrentStage("downloading");
      } else if (event.event_type === "InstallationStepCompleted") {
        setProgressPercent((prev) => Math.min(100, prev + 25));
        setCurrentStage(event.payload.stage);
      } else if (event.event_type === "InstallationCompleted") {
        setProgressPercent(100);
        setCurrentStage("completed");
        setTimeout(() => setIsInstalling(false), 2000);
      } else if (event.event_type === "InstallationFailed") {
        setCurrentStage("failed");
        setIsInstalling(false);
      }
    });

    return () => unsubscribe();
  }, []);

  const installStack = useCallback(async (packageIds: string[]) => {
    try {
      setIsInstalling(true);
      setLogs([]);
      setProgressPercent(5);
      setCurrentStage("queued");
      await api.installPackages(packageIds);
    } catch (err) {
      setIsInstalling(false);
      throw err;
    }
  }, []);

  return {
    isInstalling,
    currentPackage,
    progressPercent,
    currentStage,
    logs,
    installStack,
  };
}
