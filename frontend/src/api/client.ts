/**
 * REST API client for DevForge backend endpoints.
 */

export interface Package {
  id: string;
  name: string;
  description: string;
  category: string;
  icon?: string;
  website?: string;
  status: string;
  installed_version?: string;
  latest_version?: string;
  available_versions?: string[];
  health_score: number;
  has_update: boolean;
  is_installed: boolean;
}

export interface SystemInfo {
  os_name: string;
  os_version: string;
  os_build: number;
  architecture: string;
  total_ram_mb: number;
  available_disk_gb: number;
  gpus: Array<{
    vendor: string;
    device_name: string;
    driver_version?: string;
    vram_mb?: number;
    cuda_version?: string;
  }>;
  cpu_cores: number;
}

export interface HealthSummary {
  score: number;
  status: string;
  healthy_count: number;
  degraded_count: number;
  unhealthy_count: number;
  total_installed: number;
}

export interface StackDefinition {
  id: string;
  name: string;
  description: string;
  icon?: string;
  packages: string[];
}

const API_BASE = "/api/v1";

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || `API error (${res.status})`);
  }

  return res.json();
}

export const api = {
  // Packages
  getPackages: (category?: string, search?: string) => {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (search) params.append("search", search);
    const query = params.toString() ? `?${params.toString()}` : "";
    return request<Package[]>(`/packages${query}`);
  },

  getPackageDetail: (packageId: string) => request<Package>(`/packages/${packageId}`),

  // Installations
  installPackages: (packages: string[]) =>
    request<any[]>("/install", {
      method: "POST",
      body: JSON.stringify({ packages, add_to_path: true, all_users: true }),
    }),

  uninstallPackage: (packageId: string) =>
    request<{ package_id: string; success: boolean }>(`/uninstall/${packageId}`, {
      method: "POST",
    }),

  repairPackage: (packageId: string) =>
    request<{ package_id: string; repaired: boolean }>(`/repair/${packageId}`, {
      method: "POST",
    }),

  // System
  getSystemInfo: () => request<SystemInfo>("/system/info"),
  getHealthSummary: () => request<HealthSummary>("/system/health"),

  // Environments
  getStacks: () => request<StackDefinition[]>("/environments/stacks"),
  createSnapshot: (name: string, description: string = "") =>
    request<any>("/environments/snapshot", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    }),
  exportProfile: (profileId: string) =>
    request<{ manifest: string }>("/environments/export", {
      method: "POST",
      body: JSON.stringify({ profile_id: profileId }),
    }),
};
