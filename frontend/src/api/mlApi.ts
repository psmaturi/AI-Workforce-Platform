import client from './client';
import type {
  SkillGapResult,
  ReadinessResult,
  TrainingRecommendation,
  SkillRisk,
  ForecastResult,
  FutureDemandResult,
} from '../types';

export const getSkillGap = async (employeeId: number, targetRoleId: number): Promise<SkillGapResult> => {
  const { data } = await client.get<SkillGapResult>(`/ml/employee/${employeeId}/skill-gap`, {
    params: { target_role_id: targetRoleId },
  });
  return data;
};

export const getReadiness = async (employeeId: number, targetRoleId: number): Promise<ReadinessResult> => {
  const { data } = await client.get<ReadinessResult>(`/ml/employee/${employeeId}/readiness`, {
    params: { target_role_id: targetRoleId },
  });
  return data;
};

export const getTrainingRecommendations = async (
  employeeId: number,
  targetRoleId: number
): Promise<TrainingRecommendation[]> => {
  const { data } = await client.get<TrainingRecommendation[]>(`/ml/employee/${employeeId}/recommendations`, {
    params: { target_role_id: targetRoleId },
  });
  return data;
};

export const getWorkforceRisks = async (departmentId: number): Promise<SkillRisk[]> => {
  const { data } = await client.get<SkillRisk[]>('/ml/workforce/risks', {
    params: { department_id: departmentId },
  });
  return data;
};

export const getWorkforceForecast = async (params: {
  year: number;
  department_id: number;
  role_id: number;
  current_headcount: number;
  attrition_rate: number;
}): Promise<ForecastResult> => {
  const { data } = await client.get<ForecastResult>('/ml/workforce/forecast', { params });
  return data;
};

export const getFutureDemand = async (params: {
  department_id: number;
  current_demand: number;
  hiring_demand: number;
  industry_trend: number;
}): Promise<FutureDemandResult> => {
  const { data } = await client.get<FutureDemandResult>('/ml/skills/future-demand', { params });
  return data;
};

export const getManagerDashboard = async (managerId: number): Promise<any> => {
  const { data } = await client.get<any>(`/ml/manager/${managerId}/dashboard`);
  return data;
};

export const getHRDashboard = async (): Promise<any> => {
  const { data } = await client.get<any>('/ml/hr/dashboard');
  return data;
};
