import { useState, useEffect, useCallback } from "react";
import { api, HealthSummary, SystemInfo } from "../api/client";

export function useSystemHealth() {
  const [health, setHealth] = useState<HealthSummary | null>(null);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchHealth = useCallback(async () => {
    try {
      setLoading(true);
      const [hData, sysData] = await Promise.all([
        api.getHealthSummary(),
        api.getSystemInfo(),
      ]);
      setHealth(hData);
      setSystemInfo(sysData);
    } catch (e) {
      console.error("Failed to fetch system health:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  const repairPackage = async (packageId: string) => {
    await api.repairPackage(packageId);
    await fetchHealth();
  };

  return {
    health,
    systemInfo,
    loading,
    refetch: fetchHealth,
    repairPackage,
  };
}
