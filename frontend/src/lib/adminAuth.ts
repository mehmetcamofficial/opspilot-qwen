export const adminAuthCookie = "opspilot-admin-auth";

const localAdminPassword = "opspilot-local-admin";

export function getAdminPassword() {
  return process.env.OPSPILOT_ADMIN_PASSWORD || (process.env.NODE_ENV === "production" ? "" : localAdminPassword);
}

export function getAdminSessionToken() {
  const password = getAdminPassword();
  return process.env.OPSPILOT_ADMIN_SESSION_TOKEN || (password ? `opspilot-admin:${password}` : "");
}

export function isAdminAuthConfigured() {
  return Boolean(getAdminPassword() && getAdminSessionToken());
}

