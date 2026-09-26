import React from "react";
import { useAuth } from "@/contexts/SimpleAuthContext";

interface AdminBypassProps {
  children: React.ReactNode;
  feature: "try" | "detection";
  fallbackComponent?: React.ComponentType<{ children?: React.ReactNode }>;
}

/** Signed-in users see the page; others hit the fallback (sign-in). No status banner. */
export const AdminBypass: React.FC<AdminBypassProps> = ({
  children,
  fallbackComponent: FallbackComponent,
}) => {
  const { user, isAuthenticated } = useAuth();

  if (isAuthenticated && user) {
    return <>{children}</>;
  }

  if (FallbackComponent) {
    return <FallbackComponent>{children}</FallbackComponent>;
  }

  return <>{children}</>;
};
