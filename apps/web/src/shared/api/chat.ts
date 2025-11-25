import { api } from './client'

import type {
  ChatDialogsResponse,
  ChatMessagesResponse,
  ChatMessageCreate,
  ChatMessage,
} from '@/shared/types/chat'

export const chatApi = {
  async getDialogs(): Promise<ChatDialogsResponse> {
    const response = await api.get<ChatDialogsResponse>('/chat/dialogs')
    return response.data
  },

  async getDialogMessages(dialogId: string): Promise<ChatMessagesResponse> {
    const response = await api.get<ChatMessagesResponse>(`/chat/dialogs/${dialogId}/messages`)
    return response.data
  },

  async sendMessage(dialogId: string, payload: ChatMessageCreate): Promise<ChatMessage> {
    const response = await api.post<ChatMessage>(`/chat/dialogs/${dialogId}/messages`, payload)
    return response.data
  },
}



