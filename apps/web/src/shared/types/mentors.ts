export interface MentorUniversity {
  id: string
  mentor_id: string
  university: string
  degree: string | null
  major: string | null
  year_from: number | null
  year_to: number | null
  country: string | null
  city: string | null
  created_at: string
  updated_at: string
}

export interface MentorBase {
  headline: string | null
  bio: string | null
  price_30: number | null
  price_45: number | null
  price_60: number | null
  languages: string[]
  subjects: string[]
  avatar_url: string | null
}

export interface Mentor extends MentorBase {
  user_id: string
  rating_avg: number
  rating_count: number
  country: string | null
  city: string | null
  created_at: string
  updated_at: string
  
  // Связанные данные
  user: {
    id: string
    email: string
    name: string | null
    timezone: string
    is_active: boolean
  }
  universities: MentorUniversity[]
}

export interface MentorCard {
  user_id: string
  name: string | null
  headline: string | null
  bio: string | null
  avatar_url: string | null
  rating_avg: number
  rating_count: number
  languages: string[]
  subjects: string[]
  price_30: number | null
  price_45: number | null
  price_60: number | null
  country: string | null
  city: string | null
  university: string | null
}

export interface MentorDetail extends Mentor {
  // Дополнительная статистика
  total_consultations: number
  response_rate: number | null
  avg_response_time_hours: number | null
}

export interface MentorFilters {
  languages?: string[]
  subjects?: string[]
  countries?: string[]
  price_min?: number
  price_max?: number
  rating_min?: number
  has_availability?: boolean
}

export type MentorSortOptions = 
  | 'rating_desc'
  | 'rating_asc' 
  | 'price_asc'
  | 'price_desc'
  | 'name_asc'
  | 'name_desc'
  | 'created_desc'
  | 'created_asc'

export interface MentorSearchParams extends MentorFilters {
  search?: string
  sort?: MentorSortOptions
  page?: number
  page_size?: number
}

export interface MentorListResponse {
  mentors: MentorCard[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface PopularLanguages {
  language: string
  count: number
}

export interface PopularSubjects {
  subject: string
  count: number
}

export interface UniversitySuggestion {
  university: string
  count: number
  countries: string[]
}

export interface MentorStats {
  total_mentors: number
  active_mentors: number
  average_rating: number
  total_consultations: number
}

export interface MentorCreateData {
  headline?: string
  bio?: string
  price_30?: number | null
  price_45?: number | null
  price_60?: number | null
  languages?: string[]
  subjects?: string[]
  country?: string
  city?: string
}

export interface MentorUpdateData extends Partial<MentorCreateData> {}
