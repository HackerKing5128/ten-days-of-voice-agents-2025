export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Orion Wellness',
  pageTitle: 'Orion - Health & Wellness Companion',
  pageDescription: 'Your supportive voice companion for daily wellness check-ins',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#2C7A7B',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#38B2AC',
  startButtonText: 'Begin Check-in',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
