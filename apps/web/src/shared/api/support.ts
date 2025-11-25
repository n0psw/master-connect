import { api } from './client'

export enum TicketStatus {
  OPEN = 'OPEN',
  IN_PROGRESS = 'IN_PROGRESS',
  RESOLVED = 'RESOLVED',
  CLOSED = 'CLOSED',
}

export interface SupportTicket {
  id: string
  user_id: string
  booking_id?: string
  subject: string
  body: string
  status: TicketStatus
  created_at: string
  updated_at: string
  user_name?: string
  user_email?: string
}

export interface TicketCreate {
  subject: string
  body: string
  booking_id?: string
}

export interface TicketUpdate {
  subject?: string
  body?: string
  status?: TicketStatus
}

export interface TicketList {
  tickets: SupportTicket[]
  total: number
  page: number
  page_size: number
}

export interface TicketStatusUpdate {
  status: TicketStatus
}

export interface TicketStats {
  total: number
  open: number
  in_progress: number
  resolved: number
  closed: number
}

export const supportApi = {
  // Пользовательские методы
  async createTicket(data: TicketCreate): Promise<SupportTicket> {
    const response = await api.post<SupportTicket>('/support/tickets', data)
    return response.data
  },

  async getMyTickets(
    page: number = 1,
    pageSize: number = 20,
    status?: TicketStatus
  ): Promise<TicketList> {
    const params: any = { page, page_size: pageSize }
    if (status) {
      params.status = status
    }

    const response = await api.get<TicketList>('/support/tickets', { params })
    return response.data
  },

  async getTicket(ticketId: string): Promise<SupportTicket> {
    const response = await api.get<SupportTicket>(`/support/tickets/${ticketId}`)
    return response.data
  },

  async updateTicket(ticketId: string, data: TicketUpdate): Promise<SupportTicket> {
    const response = await api.put<SupportTicket>(`/support/tickets/${ticketId}`, data)
    return response.data
  },

  // Админские методы
  async getAllTickets(
    page: number = 1,
    pageSize: number = 20,
    status?: TicketStatus
  ): Promise<TicketList> {
    const params: any = { page, page_size: pageSize }
    if (status) {
      params.status = status
    }

    const response = await api.get<TicketList>('/support/admin/tickets', { params })
    return response.data
  },

  async updateTicketStatus(
    ticketId: string,
    status: TicketStatus
  ): Promise<SupportTicket> {
    const response = await api.patch<SupportTicket>(
      `/support/admin/tickets/${ticketId}/status`,
      { status }
    )
    return response.data
  },

  async getTicketStats(): Promise<TicketStats> {
    const response = await api.get<TicketStats>('/support/admin/stats')
    return response.data
  },
}

