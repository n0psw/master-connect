export interface ChatDialog {
  id: string
  booking_id: string
  student_id: string
  student_name: string | null
  mentor_id: string
  mentor_name: string | null
  last_message_preview: string | null
  last_message_at: string | null
  unread_count: number
}

export interface ChatDialogsResponse {
  dialogs: ChatDialog[]
}

export interface ChatMessage {
  id: string
  dialog_id: string
  sender_id: string
  text: string | null
  file_url: string | null
  is_read: boolean
  created_at: string
  is_own: boolean
}

export interface ChatMessagesResponse {
  dialog: ChatDialog
  messages: ChatMessage[]
}

export interface ChatMessageCreate {
  text: string
}



