import React, { useState } from "react";
import "./styles/global.css";
import { Sidebar, NavTab } from "./components/common/Sidebar";
import { Header } from "./components/common/Header";
import { LandingPage } from "./pages/LandingPage";
import { CustomBundlePage } from "./pages/CustomBundlePage";
import { WelcomePage } from "./pages/WelcomePage";
import { CatalogPage } from "./pages/CatalogPage";
import { InstalledPage } from "./pages/InstalledPage";
import { HealthPage } from "./pages/HealthPage";
import { ProfilesPage } from "./pages/ProfilesPage";
import { ProgressDrawer } from "./components/installation/ProgressDrawer";
import { useInstallation } from "./hooks/useInstallation";
import { useSystemHealth } from "./hooks/useSystemHealth";
import { api } from "./api/client";

export const App: React.FC = () => {
  const [viewMode, setViewMode] = useState<"landing" | "custom" | "app">("landing");
  const [activeTab, setActiveTab] = useState<NavTab>("welcome");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const { isInstalling, currentPackage, progressPercent, currentStage, logs, installStack } =
    useInstallation();
  const { health, refetch: refetchHealth } = useSystemHealth();

  const handleInstallSingle = async (packageId: string) => {
    await installStack([packageId]);
  };

  const handleUninstall = async (packageId: string) => {
    await api.uninstallPackage(packageId);
    refetchHealth();
  };

  if (viewMode === "landing") {
    return (
      <LandingPage
        onOpenApp={() => setViewMode("app")}
        onOpenCustomBuilder={() => setViewMode("custom")}
      />
    );
  }

  if (viewMode === "custom") {
    return <CustomBundlePage onBackToLanding={() => setViewMode("landing")} />;
  }

  return (
    <div className="app-container">
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        installedCount={health?.total_installed}
      />

      <div className="main-content">
        <Header
          healthScore={health?.score}
          healthStatus={health?.status}
          searchQuery={searchQuery}
          onSearchChange={(q) => {
            setSearchQuery(q);
            if (q && activeTab !== "catalog") setActiveTab("catalog");
          }}
          onRefresh={refetchHealth}
        />

        {activeTab === "welcome" && (
          <WelcomePage onInstallStack={installStack} isInstalling={isInstalling} />
        )}
        {activeTab === "catalog" && (
          <CatalogPage onInstall={handleInstallSingle} onUninstall={handleUninstall} />
        )}
        {activeTab === "installed" && (
          <InstalledPage onInstall={handleInstallSingle} onUninstall={handleUninstall} />
        )}
        {activeTab === "health" && <HealthPage />}
        {activeTab === "profiles" && <ProfilesPage />}
      </div>

      <ProgressDrawer
        isOpen={isInstalling}
        packageName={currentPackage}
        progressPercent={progressPercent}
        stage={currentStage}
        logs={logs}
      />
    </div>
  );
};

export default App;
