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

  // Player configuration (for Improv Battle)
  playerName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Improv Battle',
  pageTitle: 'IMPROV BATTLE - Voice Improv Game Show',
  pageDescription: 'The wildest voice improv game show on the internet! Hosted by JAX.',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/day10-jax.svg',
  accent: '#cc00ff',
  logoDark: '/day10-jax.svg',
  accentDark: '#00eaff',
  startButtonText: 'Enter the Stage',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,

  // Player configuration
  playerName: undefined,
};
