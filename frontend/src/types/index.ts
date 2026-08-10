// Shared TypeScript interfaces for the AI Workforce Intelligence Platform

// ─── Auth ────────────────────────────────────────────────────────────────────
export type UserRole = 'employee' | 'manager' | 'hr';

export interface AuthUser {
  id: number;
  name: string;
  email: string;
  employeeNumber: string;
  role: UserRole;
  department: string;
  jobTitle: string;
  grade: number;
}

// ─── Chat ─────────────────────────────────────────────────────────────────────
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
}

// ─── ML / Skill Gap ──────────────────────────────────────────────────────────
export interface SkillGapResult {
  coverage_percentage: number;
  gap_percentage: number;
  missing_skills: MissingSkill[];
  upgrade_needed: UpgradeSkill[];
  met_requirements: number;
  total_requirements: number;
}

export interface MissingSkill {
  skill: string;
  required: number;
  current: number;
  gap: number;
}

export interface UpgradeSkill {
  skill: string;
  required: number;
  current: number;
  gap: number;
}

// ─── Readiness ────────────────────────────────────────────────────────────────
export interface ReadinessResult {
  readiness_score: number;
  classification: 'Not Ready' | 'Developing' | 'Nearly Ready' | 'Ready';
  breakdown: {
    skill_points: number;
    experience_points: number;
    performance_points: number;
    training_points: number;
  };
}

// ─── Training Recommendations ─────────────────────────────────────────────────
export interface TrainingRecommendation {
  course_id: number;
  title: string;
  target_skill: string;
  overall_score: number;
  explanation: string;
}

// ─── Workforce Risks ─────────────────────────────────────────────────────────
export interface SkillRisk {
  department: string;
  skill: string;
  risk_type: string;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
  explanation: string;
}

// ─── Workforce Forecast ──────────────────────────────────────────────────────
export interface ForecastResult {
  required_headcount: number;
}

// ─── Future Demand ────────────────────────────────────────────────────────────
export interface FutureDemandResult {
  demand_category: 'Low' | 'Medium' | 'High' | 'Critical';
}

// ─── Health ───────────────────────────────────────────────────────────────────
export interface HealthStatus {
  status: string;
  version?: string;
}
