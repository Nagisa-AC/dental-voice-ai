/**
 * TypeScript Type Definitions
 * 
 * Comprehensive type definitions for the Healthcare Voice AI application.
 * Replaces all 'any' types with proper TypeScript interfaces.
 */

// ============================================================================
// API TYPES
// ============================================================================

export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  request_id?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

// ============================================================================
// AUTHENTICATION TYPES
// ============================================================================

export interface User {
  user_id: string;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  tenant_id?: string;
  created_at: string;
  updated_at: string;
}

export type UserRole = 'admin' | 'user' | 'clinic_admin' | 'clinic_user';

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

// ============================================================================
// CLINIC TYPES
// ============================================================================

export interface Clinic {
  id: string;
  tenant_id: string;
  name: string;
  industry_type: HealthcareIndustry;
  status: ClinicStatus;
  phone: string;
  email: string;
  address: string;
  website?: string;
  business_hours?: BusinessHours;
  services?: string[];
  policies?: Record<string, unknown>;
  vapi_assistant_id?: string;
  assistant_config?: AssistantConfig;
  faq_content?: string;
  faq_filename?: string;
  admin_notes?: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
}

export type HealthcareIndustry = 
  | 'dental' 
  | 'medical' 
  | 'veterinary' 
  | 'mental_health' 
  | 'physical_therapy' 
  | 'chiropractic' 
  | 'optometry' 
  | 'dermatology' 
  | 'cardiology' 
  | 'orthopedics';

export type ClinicStatus = 'pending' | 'approved' | 'rejected' | 'suspended';

export interface BusinessHours {
  monday?: DayHours;
  tuesday?: DayHours;
  wednesday?: DayHours;
  thursday?: DayHours;
  friday?: DayHours;
  saturday?: DayHours;
  sunday?: DayHours;
}

export interface DayHours {
  open: string; // HH:MM format
  close: string; // HH:MM format
  closed?: boolean;
}

export interface ClinicFormData {
  name: string;
  industry_type: HealthcareIndustry;
  phone: string;
  email: string;
  address: string;
  website?: string;
  business_hours?: BusinessHours;
  services?: string[];
  policies?: Record<string, unknown>;
}

// ============================================================================
// ASSISTANT TYPES
// ============================================================================

export interface Assistant {
  id: string;
  clinic_id: string;
  name: string;
  description?: string;
  vapi_assistant_id: string;
  config: AssistantConfig;
  status: AssistantStatus;
  created_at: string;
  updated_at: string;
}

export type AssistantStatus = 'active' | 'inactive' | 'training' | 'error';

export interface AssistantConfig {
  voice?: VoiceConfig;
  behavior?: BehaviorConfig;
  knowledge?: KnowledgeConfig;
  integrations?: IntegrationConfig;
}

export interface VoiceConfig {
  provider: 'elevenlabs' | 'azure' | 'aws' | 'google';
  voice_id: string;
  model?: string;
  stability?: number;
  similarity_boost?: number;
  style?: number;
  use_speaker_boost?: boolean;
}

export interface BehaviorConfig {
  first_message?: string;
  background_sound?: string;
  end_call_message?: string;
  end_call_phrases?: string[];
  silence_timeout_seconds?: number;
  max_duration_seconds?: number;
  voicemail_message?: string;
  voicemail_detection_llm?: boolean;
  recording_enabled?: boolean;
  transcription_enabled?: boolean;
  interruption_threshold?: number;
  backchanneling_enabled?: boolean;
  fillers_enabled?: boolean;
  sentiment_analysis?: boolean;
  language?: string;
  start_timeout_seconds?: number;
  connection_timeout_seconds?: number;
  end_call_timeout_seconds?: number;
  max_retries?: number;
  retry_delay_seconds?: number;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stop_sequences?: string[];
}

export interface KnowledgeConfig {
  faq_content?: string;
  custom_instructions?: string;
  context_window?: number;
  memory_enabled?: boolean;
  memory_retention_hours?: number;
}

export interface IntegrationConfig {
  calendar?: CalendarIntegration;
  crm?: CRMIntegration;
  notifications?: NotificationConfig;
}

export interface CalendarIntegration {
  provider: 'google' | 'outlook' | 'calendly';
  enabled: boolean;
  calendar_id?: string;
  timezone?: string;
  buffer_time_minutes?: number;
}

export interface CRMIntegration {
  provider: 'salesforce' | 'hubspot' | 'pipedrive';
  enabled: boolean;
  api_key?: string;
  base_url?: string;
}

export interface NotificationConfig {
  email_enabled: boolean;
  sms_enabled: boolean;
  webhook_enabled: boolean;
  webhook_url?: string;
}

// ============================================================================
// WEBHOOK TYPES
// ============================================================================

export interface WebhookEvent {
  event_type: WebhookEventType;
  timestamp: string;
  data: Record<string, unknown>;
  webhook_id?: string;
  tenant_id?: string;
}

export type WebhookEventType = 
  | 'call_started'
  | 'call_ended'
  | 'call_answered'
  | 'call_voicemail'
  | 'call_recording_ready'
  | 'call_transcript_ready'
  | 'call_analysis_ready'
  | 'assistant_created'
  | 'assistant_updated'
  | 'assistant_deleted'
  | 'clinic_created'
  | 'clinic_updated'
  | 'clinic_deleted';

export interface CallData {
  call_id: string;
  assistant_id: string;
  customer_phone: string;
  customer_name?: string;
  start_time: string;
  end_time?: string;
  duration_seconds?: number;
  status: CallStatus;
  recording_url?: string;
  transcript?: string;
  analysis?: CallAnalysis;
  cost?: number;
  currency?: string;
}

export type CallStatus = 
  | 'queued'
  | 'ringing'
  | 'in_progress'
  | 'completed'
  | 'failed'
  | 'busy'
  | 'no_answer'
  | 'voicemail';

export interface CallAnalysis {
  sentiment: 'positive' | 'neutral' | 'negative';
  intent: string;
  entities: Record<string, unknown>;
  summary: string;
  action_items: string[];
  follow_up_required: boolean;
  satisfaction_score?: number;
}

// ============================================================================
// FORM TYPES
// ============================================================================

export interface FormField {
  name: string;
  label: string;
  type: FormFieldType;
  required: boolean;
  placeholder?: string;
  helpText?: string;
  validation?: ValidationRule;
  options?: FormFieldOption[];
}

export type FormFieldType = 
  | 'text'
  | 'email'
  | 'password'
  | 'number'
  | 'tel'
  | 'url'
  | 'textarea'
  | 'select'
  | 'multiselect'
  | 'checkbox'
  | 'radio'
  | 'date'
  | 'time'
  | 'datetime'
  | 'file';

export interface FormFieldOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  min?: number;
  max?: number;
  custom?: (value: unknown) => string | null;
}

export interface FormState<T = Record<string, unknown>> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isSubmitting: boolean;
  isValid: boolean;
}

// ============================================================================
// UI COMPONENT TYPES
// ============================================================================

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  label: string;
  placeholder?: string;
  value?: string;
  error?: string;
  helpText?: string;
  required?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  variant?: 'default' | 'filled' | 'outlined';
  size?: 'small' | 'medium' | 'large';
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  onChange?: (value: string) => void;
  onBlur?: () => void;
  onFocus?: () => void;
  className?: string;
}

export interface CardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'small' | 'medium' | 'large';
  className?: string;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large' | 'full';
  closable?: boolean;
  className?: string;
}

export interface TableColumn<T = unknown> {
  key: keyof T;
  title: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: unknown, record: T) => React.ReactNode;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
}

export interface TableProps<T = unknown> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  pagination?: PaginationProps;
  sorting?: SortingProps;
  filtering?: FilteringProps;
  selection?: SelectionProps<T>;
  className?: string;
}

export interface PaginationProps {
  current: number;
  pageSize: number;
  total: number;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: boolean;
  onChange: (page: number, pageSize: number) => void;
}

export interface SortingProps {
  field?: string;
  order?: 'asc' | 'desc';
  onChange: (field: string, order: 'asc' | 'desc') => void;
}

export interface FilteringProps {
  filters: Record<string, unknown>;
  onChange: (filters: Record<string, unknown>) => void;
}

export interface SelectionProps<T = unknown> {
  selectedRows: T[];
  onChange: (selectedRows: T[]) => void;
  type?: 'checkbox' | 'radio';
}

// ============================================================================
// LAYOUT TYPES
// ============================================================================

export interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}

export interface NavigationItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  path?: string;
  children?: NavigationItem[];
  disabled?: boolean;
  badge?: string | number;
}

export interface SidebarProps {
  items: NavigationItem[];
  collapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
  className?: string;
}

export interface HeaderProps {
  title?: string;
  user?: User;
  onLogout?: () => void;
  className?: string;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type Required<T, K extends keyof T> = T & { [P in K]-?: T[P] };

export type NonNullable<T> = T extends null | undefined ? never : T;

export type ValueOf<T> = T[keyof T];

export type KeysOfType<T, U> = {
  [K in keyof T]: T[K] extends U ? K : never;
}[keyof T];

// ============================================================================
// EVENT TYPES
// ============================================================================

export interface CustomEvent<T = unknown> {
  type: string;
  payload: T;
  timestamp: string;
  source?: string;
}

export interface KeyboardEvent {
  key: string;
  code: string;
  ctrlKey: boolean;
  shiftKey: boolean;
  altKey: boolean;
  metaKey: boolean;
  preventDefault: () => void;
  stopPropagation: () => void;
}

export interface MouseEvent {
  clientX: number;
  clientY: number;
  button: number;
  ctrlKey: boolean;
  shiftKey: boolean;
  altKey: boolean;
  metaKey: boolean;
  preventDefault: () => void;
  stopPropagation: () => void;
}

// ============================================================================
// CONFIGURATION TYPES
// ============================================================================

export interface AppConfig {
  apiBaseUrl: string;
  environment: 'development' | 'staging' | 'production';
  version: string;
  features: FeatureFlags;
  limits: AppLimits;
}

export interface FeatureFlags {
  enableAnalytics: boolean;
  enableErrorReporting: boolean;
  enablePerformanceMonitoring: boolean;
  enableDarkMode: boolean;
  enableNotifications: boolean;
}

export interface AppLimits {
  maxFileSize: number;
  maxUploads: number;
  sessionTimeout: number;
  rateLimit: number;
}

// ============================================================================
// ERROR TYPES
// ============================================================================

export interface ErrorInfo {
  componentStack: string;
  errorBoundary?: string;
  errorBoundaryStack?: string;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

export interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
}

