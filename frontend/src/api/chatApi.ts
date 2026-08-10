import client from './client';
import type { ChatRequest, ChatResponse } from '../types';

export const sendChatMessage = async (message: string): Promise<ChatResponse> => {
  const payload: ChatRequest = { message };
  
  const headers: Record<string, string> = {};
  const storedUser = sessionStorage.getItem('wf_user');
  if (storedUser) {
    try {
      const user = JSON.parse(storedUser);
      if (user.id) {
        headers['X-Employee-Id'] = String(user.id);
      }
      if (user.employeeNumber) {
        headers['X-Employee-Number'] = user.employeeNumber;
      }
    } catch (e) {
      console.error('Error parsing user session storage', e);
    }
  }

  const { data } = await client.post<ChatResponse>('/chat', payload, { headers });
  return data;
};
