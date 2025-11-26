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
  companyName: 'Razorpay',
  pageTitle: 'Talk to Zoya | Razorpay SDR',
  pageDescription: 'Chat with Zoya, your AI Sales Development Representative from Razorpay',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/razorpay-logo.svg',
  accent: '#0066FF',
  logoDark: '/razorpay-logo-dark.svg',
  accentDark: '#3D8BFF',
  startButtonText: 'Talk to Zoya',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
