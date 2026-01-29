import { useMemo, useState } from 'react'
import { useSearchParams, Link, useLocation } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import {
  Search,
  Filter,
  Star,
  MapPin,
  Clock,
  X,
  SlidersHorizontal,
  LayoutGrid,
  List,
  ArrowRight,
  Users,
  Sparkles,
  ShieldCheck,
  Info,
  HelpCircle
} from 'lucide-react'
import { useQuery } from 'react-query'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Card, CardContent } from '@/shared/ui/card'
import { mentorsApi } from '@/shared/api/mentors'
import type { MentorSearchParams, MentorCard } from '@/shared/types/mentors'
import { getImageUrl } from '@/shared/utils/imageUtils'

const segments = [
  { label: 'Лучшие', value: 'rating_desc' },
  { label: 'Доступные', value: 'price_asc' },
  { label: 'По алфавиту', value: 'name_asc' }
]

export const MentorsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const location = useLocation()
  const [showFilters, setShowFilters] = useState(false)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  const basePath = location.pathname.includes('/student/') ? '/student/mentors' : '/mentors'

  const searchQuery = searchParams.get('search') || ''
  const currentPage = parseInt(searchParams.get('page') || '1')
  const selectedSubjects = searchParams.get('subjects')?.split(',').filter(Boolean) || []
  const selectedCountries = searchParams.get('countries')?.split(',').filter(Boolean) || []
  const priceMin = searchParams.get('price_min') ? parseInt(searchParams.get('price_min')!) : undefined
  const priceMax = searchParams.get('price_max') ? parseInt(searchParams.get('price_max')!) : undefined
  const ratingMin = searchParams.get('rating_min') ? parseFloat(searchParams.get('rating_min')!) : undefined
  const sortBy = searchParams.get('sort') || 'rating_desc'

  const searchFilters: MentorSearchParams = {
    search: searchQuery || undefined,
    page: currentPage,
    page_size: 12,
    sort: sortBy as any,
    subjects: selectedSubjects.length > 0 ? selectedSubjects : undefined,
    countries: selectedCountries.length > 0 ? selectedCountries : undefined,
    price_min: priceMin,
    price_max: priceMax,
    rating_min: ratingMin
  }

  const { data: mentorsData, isLoading, error } = useQuery(
    ['mentors', searchFilters],
    () => mentorsApi.getMentors(searchFilters),
    {
      keepPreviousData: true,
      refetchOnMount: true,
      refetchOnWindowFocus: true,
      staleTime: 30 * 1000,
      cacheTime: 60 * 1000,
      onError: (error: any) => {
        toast.error('Ошибка при загрузке менторов: ' + (error?.detail || error?.message))
      }
    }
  )


  const { data: popularSubjects } = useQuery(
    ['popular-subjects'],
    () => mentorsApi.getPopularSubjects(),
    { staleTime: 5 * 60 * 1000 }
  )

  const updateSearchParams = (newParams: Record<string, string | undefined>) => {
    const params = new URLSearchParams(searchParams)
    Object.entries(newParams).forEach(([key, value]) => {
      if (value) {
        params.set(key, value)
      } else {
        params.delete(key)
      }
    })
    if (!newParams.page) {
      params.delete('page')
    }
    setSearchParams(params)
  }

  const handleSearch = (query: string) => {
    updateSearchParams({ search: query || undefined })
  }

  const handlePageChange = (page: number) => {
    updateSearchParams({ page: page.toString() })
  }

  const handleFilterChange = (key: string, value: string | string[] | undefined) => {
    if (Array.isArray(value)) {
      updateSearchParams({ [key]: value.length > 0 ? value.join(',') : undefined })
    } else {
      updateSearchParams({ [key]: value })
    }
  }

  const clearFilters = () => {
    setSearchParams(new URLSearchParams({ search: searchQuery }))
  }

  const activeFilters = useMemo(() => {
    const chips: Array<{ label: string; key: string; value?: string }> = []
    selectedSubjects.forEach((subject) => chips.push({ label: subject, key: 'subjects', value: subject }))
    selectedCountries.forEach((country) => chips.push({ label: country, key: 'countries', value: country }))
    if (priceMin) chips.push({ label: `от ${priceMin.toLocaleString()} ₸`, key: 'price_min' })
    if (priceMax) chips.push({ label: `до ${priceMax.toLocaleString()} ₸`, key: 'price_max' })
    if (ratingMin) chips.push({ label: `${ratingMin}+ ⭐`, key: 'rating_min' })
    return chips
  }, [selectedSubjects, selectedCountries, priceMin, priceMax, ratingMin])

  const hasActiveFilters = activeFilters.length > 0

  const currentSegment = segments.find((item) => item.value === sortBy) ?? segments[0]

  return (
    <div className="relative left-[-24px] w-[calc(100%+48px)] lg:left-[-24px] lg:w-[calc(100%+48px)] -mb-6">
      <Helmet>
        <title>Каталог консультантов — MasterConnect</title>
        <meta
          name="description"
          content="Выберите консультанта по поступлению из проверенных экспертов. Мы давно работаем в сфере IELTS и SAT подготовки в Казахстане. Одноразовые консультации с реальным опытом."
        />
      </Helmet>

      <div className="fixed inset-0 pointer-events-none z-0 hidden sm:block">
        <div className="absolute top-20 right-10 w-96 h-96 bg-gradient-to-br from-blue-400/15 to-cyan-400/15 rounded-full blur-3xl" />
        <div className="absolute top-1/3 left-20 w-80 h-80 bg-gradient-to-br from-indigo-400/12 to-purple-400/12 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-1/4 w-72 h-72 bg-gradient-to-br from-violet-400/10 to-fuchsia-400/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/3 w-64 h-64 bg-gradient-to-br from-cyan-400/10 to-blue-400/10 rounded-full blur-2xl" />
      </div>

      <div className="bg-white pb-8 sm:pb-12 lg:pb-16 relative">
        <div className="border-b border-gray-100 bg-white">
          <div className="container-wide px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-4 sm:space-y-6">
            <div className="max-w-4xl space-y-3 sm:space-y-4 mb-4 sm:mb-6">
              <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Каталог консультантов</h1>
              <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 sm:p-6 space-y-2 sm:space-y-3">
                <h2 className="text-lg font-semibold text-gray-900">О платформе</h2>
                <p className="text-gray-600">
                  Мы давно работаем в сфере IELTS и SAT подготовки в Казахстане. Наш опыт в образовательной сфере помогает нам подбирать проверенных консультантов с реальным опытом поступления.
                </p>
                <p className="text-gray-600">
                  Наши консультанты проводят одноразовые консультации по поступлению, помогая студентам получить конкретные ответы на вопросы и составить четкий план действий. Каждый консультант проходит проверку образования, достижений и опыта.
                </p>
                <p className="text-gray-600">
                  Вы можете доверять подбору консультантов на нашей платформе — мы проверяем каждого эксперта и гарантируем качество консультаций.
                </p>
              </div>
            </div>
            
            <div className="space-y-3">
              <p className="text-base text-gray-600">
                Используйте фильтры по направлению, бюджету и языку, чтобы найти консультанта, который поможет с поступлением.
              </p>

            <div className="flex flex-col gap-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-[#667085]" />
                  <Input
                    placeholder="Поиск по имени, университету или направлению..."
                    defaultValue={searchQuery}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleSearch(e.currentTarget.value)
                      }
                    }}
                    className="h-14 rounded-full border border-gray-200 bg-white pl-12 text-base"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <div className="hidden lg:flex items-center gap-2 rounded-full border border-gray-200 bg-white px-2 py-2">
                    {segments.map((segment) => (
                      <button
                        key={segment.value}
                        onClick={() => updateSearchParams({ sort: segment.value })}
                        className={`rounded-full px-5 py-2 text-sm font-semibold transition ${
                          currentSegment.value === segment.value
                            ? 'bg-primary text-white'
                            : 'text-gray-600 hover:bg-gray-100'
                        }`}
                      >
                        {segment.label}
                      </button>
                    ))}
                  </div>
                  <Button
                    variant="outline"
                    className="h-12 rounded-full border-gray-200 px-5"
                    onClick={() => setShowFilters(true)}
                  >
                    <SlidersHorizontal className="h-4 w-4" />
                    Фильтры
                    {hasActiveFilters && <span className="ml-2 rounded-full bg-primary px-2 py-0.5 text-xs text-white">{activeFilters.length}</span>}
                  </Button>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {activeFilters.map((chip) => (
                  <button
                    key={`${chip.key}-${chip.value ?? 'value'}`}
                    onClick={() => {
                      if (chip.value) {
                        const list = new URLSearchParams(searchParams).get(chip.key)?.split(',').filter(Boolean) || []
                        const updated = list.filter((item) => item !== chip.value)
                        handleFilterChange(chip.key, updated)
                      } else {
                        handleFilterChange(chip.key, undefined)
                      }
                    }}
                    className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm text-gray-600 border border-gray-200"
                  >
                    {chip.label}
                    <X className="h-3 w-3" />
                  </button>
                ))}
                {hasActiveFilters && (
                  <button onClick={clearFilters} className="text-sm font-semibold text-primary underline-offset-4 hover:underline">
                    Сбросить все
                  </button>
                )}
              </div>
            </div>
            </div>
          </div>
        </div>

        <div className="container-wide px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
          <div className="grid gap-8 lg:grid-cols-[320px_1fr]">
            <aside className="hidden lg:block">
              <FiltersPanel
                popularSubjects={popularSubjects}
                selectedSubjects={selectedSubjects}
                priceMin={priceMin}
                priceMax={priceMax}
                ratingMin={ratingMin}
                onChange={handleFilterChange}
                onReset={clearFilters}
              />
            </aside>

            <div className="space-y-10">
              <div className="rounded-xl border border-gray-200 bg-white px-6 py-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div className="flex items-center gap-3">
                  <Users className="h-6 w-6 text-primary" />
                  <div>
                    <div className="text-sm font-semibold text-[#101828]">
                      {mentorsData ? `Найдено ${mentorsData.total} наставников` : 'Загружаем каталог'}
                    </div>
                    <div className="text-xs text-[#475467]">
                      {mentorsData && mentorsData.total_pages ? `Страница ${currentPage} из ${mentorsData.total_pages}` : mentorsData ? `Страница ${currentPage}` : 'Подбираем лучшие совпадения'}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <select
                    value={sortBy}
                    onChange={(e) => updateSearchParams({ sort: e.target.value })}
                    className="h-11 rounded-full border border-[rgba(16,24,40,0.12)] bg-white px-4 text-sm text-[#475467]"
                  >
                    <option value="rating_desc">По рейтингу</option>
                    <option value="price_asc">Сначала дешевле</option>
                    <option value="price_desc">Сначала дороже</option>
                    <option value="name_asc">По имени (А-Я)</option>
                    <option value="name_desc">По имени (Я-А)</option>
                  </select>
                  <div className="flex items-center gap-2 rounded-full border border-[rgba(16,24,40,0.12)] bg-white p-1">
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`flex items-center justify-center rounded-full px-3 py-2 ${
                        viewMode === 'grid' ? 'bg-[rgba(28,63,227,0.12)] text-primary' : 'text-[#475467]'
                      }`}
                    >
                      <LayoutGrid className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`flex items-center justify-center rounded-full px-3 py-2 ${
                        viewMode === 'list' ? 'bg-[rgba(28,63,227,0.12)] text-primary' : 'text-[#475467]'
                      }`}
                    >
                      <List className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>

              {isLoading ? (
                <div className={`grid gap-6 ${viewMode === 'grid' ? 'md:grid-cols-2 xl:grid-cols-3' : ''}`}>
                  {Array.from({ length: 6 }).map((_, i) => (
                    <div
                      key={i}
                      className="animate-pulse rounded-[24px] border border-[rgba(16,24,40,0.08)] bg-white p-6 shadow-[0_20px_60px_-48px_rgba(16,24,40,0.4)]"
                    >
                      <div className="h-6 w-24 rounded-full bg-[rgba(16,24,40,0.08)]" />
                      <div className="mt-4 h-4 w-36 rounded bg-[rgba(16,24,40,0.08)]" />
                      <div className="mt-6 h-32 rounded-[20px] bg-[rgba(16,24,40,0.06)]" />
                    </div>
                  ))}
                </div>
              ) : error ? (
                <div className="rounded-[24px] border border-red-200 bg-red-50 px-8 py-10 text-center text-red-600">
                  Не удалось загрузить наставников. Попробуйте обновить страницу.
                </div>
              ) : !mentorsData?.mentors.length ? (
                <div className="rounded-[24px] border border-[rgba(16,24,40,0.1)] bg-white px-10 py-16 text-center shadow-[0_20px_60px_-48px_rgba(16,24,40,0.45)]">
                  <Sparkles className="mx-auto h-10 w-10 text-primary" />
                  <h2 className="mt-6 text-2xl font-semibold text-[#101828]">Мы пока не нашли совпадений</h2>
                  <p className="mt-3 text-sm text-[#475467]">
                    Попробуйте изменить фильтры или напишите нашей команде — подберем наставника вручную.
                  </p>
                  <div className="mt-6 flex justify-center gap-3">
                    <Button variant="outline" onClick={clearFilters}>
                      Сбросить фильтры
                    </Button>
                    <Button variant="gradient" asChild>
                      <Link to="/support">Связаться с поддержкой</Link>
                    </Button>
                  </div>
                </div>
              ) : (
                <>
                  <div className={`grid gap-6 ${viewMode === 'grid' ? 'md:grid-cols-2 xl:grid-cols-3' : ''}`}>
                    {mentorsData.mentors.map((mentor) => (
                      <MentorCardComponent key={mentor.user_id} mentor={mentor} basePath={basePath} viewMode={viewMode} />
                    ))}
                  </div>

                  {mentorsData.total_pages && mentorsData.total_pages > 1 && (
                    <div className="flex justify-center">
                      <div className="inline-flex items-center gap-2 rounded-full border border-[rgba(16,24,40,0.12)] bg-white px-2 py-2 shadow-sm">
                        <Button
                          variant="outline"
                          size="sm"
                          className="rounded-full px-4"
                          disabled={currentPage <= 1}
                          onClick={() => handlePageChange(currentPage - 1)}
                        >
                          Назад
                        </Button>
                        {Array.from({ length: mentorsData.total_pages || 1 }).slice(0, 5).map((_, index) => {
                          const page = index + 1
                          return (
                            <button
                              key={page}
                              onClick={() => handlePageChange(page)}
                              className={`h-10 w-10 rounded-full text-sm font-semibold ${
                                currentPage === page
                                  ? 'bg-gradient-to-r from-[#1c3fe3] to-[#7a5cff] text-white'
                                  : 'text-[#475467] hover:bg-[rgba(28,63,227,0.08)]'
                              }`}
                            >
                              {page}
                            </button>
                          )
                        })}
                        <Button
                          variant="outline"
                          size="sm"
                          className="rounded-full px-4"
                          disabled={!mentorsData.total_pages || currentPage >= mentorsData.total_pages}
                          onClick={() => handlePageChange(currentPage + 1)}
                        >
                          Далее
                        </Button>
                      </div>
                    </div>
                  )}
                </>
              )}

              <div className="rounded-xl border border-gray-200 bg-white px-8 py-10">
                <div className="flex items-center gap-3 text-primary font-semibold text-sm uppercase tracking-[0.3em]">
                  <HelpCircle className="h-4 w-4" />
                  FAQ
                </div>
                <h3 className="mt-3 text-2xl font-semibold text-[#101828]">Популярные вопросы</h3>
                <div className="mt-6 space-y-4">
                  {[
                    {
                      question: 'Как выбрать наставника, если я подаюсь в несколько стран?',
                      answer: 'Выберите несколько направлений в фильтрах или оставьте запрос через форму — отправим персональную подборку.'
                    },
                    {
                      question: 'Что входит в консультацию?',
                      answer: 'Подготовка стратегии поступления, проверка документов и эссе, репетиция интервью и контроль дедлайнов.'
                    },
                    {
                      question: 'Можно ли вернуть средства?',
                      answer: 'Да, при первой консультации. Если формат не подошел — оформим возврат или предложим другого наставника.'
                    }
                  ].map((item) => (
                    <details key={item.question} className="group rounded-2xl border border-[rgba(16,24,40,0.08)] bg-white/80 px-5 py-4">
                      <summary className="flex cursor-pointer items-center justify-between text-sm font-semibold text-[#101828]">
                        {item.question}
                        <ArrowRight className="h-4 w-4 text-primary transition group-open:rotate-90" />
                      </summary>
                      <p className="mt-3 text-sm text-[#475467]">{item.answer}</p>
                    </details>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showFilters && (
        <div className="fixed inset-0 z-50 flex flex-col bg-black/40 backdrop-blur-sm lg:hidden" onClick={() => setShowFilters(false)}>
          <div className="mt-auto bg-white rounded-t-3xl p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <div className="text-base font-semibold text-[#101828]">Фильтры</div>
              <button onClick={() => setShowFilters(false)} className="rounded-full border border-[rgba(16,24,40,0.12)] p-2">
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="mt-6">
              <FiltersPanel
                popularSubjects={popularSubjects}
                selectedSubjects={selectedSubjects}
                priceMin={priceMin}
                priceMax={priceMax}
                ratingMin={ratingMin}
                onChange={handleFilterChange}
                onReset={() => {
                  clearFilters()
                  setShowFilters(false)
                }}
              />
            </div>
            <div className="mt-6 flex gap-3">
              <Button variant="outline" className="h-11 flex-1" onClick={() => setShowFilters(false)}>
                Закрыть
              </Button>
              <Button variant="gradient" className="h-11 flex-1" onClick={() => setShowFilters(false)}>
                Применить
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

type FiltersPanelProps = {
  popularSubjects?: { subject: string; count: number }[]
  selectedSubjects: string[]
  priceMin?: number
  priceMax?: number
  ratingMin?: number
  onChange: (key: string, value: string | string[] | undefined) => void
  onReset: () => void
}

const FiltersPanel = ({
  popularSubjects,
  selectedSubjects,
  priceMin,
  priceMax,
  ratingMin,
  onChange,
  onReset
}: FiltersPanelProps) => {
  return (
    <div className="space-y-6 rounded-[24px] border border-[rgba(16,24,40,0.1)] bg-white p-6 shadow-[0_30px_80px_-60px_rgba(16,24,40,0.45)]">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[#101828]">Фильтры</h3>
        <button className="text-sm font-semibold text-primary underline-offset-4 hover:underline" onClick={onReset}>
          Сбросить
        </button>
      </div>
      <div className="space-y-5">
        <div className="space-y-3">
          <div className="text-sm font-semibold text-[#101828]">Направления</div>
        <div className="grid grid-cols-2 gap-2">
            {(Array.isArray(popularSubjects) ? popularSubjects : []).slice(0, 8).map((item) => {
              const active = selectedSubjects.includes(item.subject)
              return (
                <button
                  key={item.subject}
                  onClick={() => {
                    const next = active
                      ? selectedSubjects.filter((s) => s !== item.subject)
                      : [...selectedSubjects, item.subject]
                    onChange('subjects', next)
                  }}
                  className={`rounded-xl border px-4 py-3 text-xs font-semibold text-left transition ${
                    active
                      ? 'border-transparent bg-[rgba(28,63,227,0.1)] text-primary'
                      : 'border-[rgba(16,24,40,0.08)] text-[#475467] hover:border-primary/30'
                  }`}
                >
                  {item.subject}
                </button>
              )
            })}
          </div>
        </div>
        <div className="space-y-3">
          <div className="text-sm font-semibold text-[#101828]">Стоимость консультации</div>
          <div className="grid grid-cols-2 gap-3">
            <Input
              type="number"
              placeholder="Минимум"
              value={priceMin || ''}
              onChange={(e) => onChange('price_min', e.target.value || undefined)}
              className="h-11 rounded-xl border-[rgba(16,24,40,0.12)]"
            />
            <Input
              type="number"
              placeholder="Максимум"
              value={priceMax || ''}
              onChange={(e) => onChange('price_max', e.target.value || undefined)}
              className="h-11 rounded-xl border-[rgba(16,24,40,0.12)]"
            />
          </div>
        </div>
        <div className="space-y-3">
          <div className="text-sm font-semibold text-[#101828]">Минимальный рейтинг</div>
          <select
            value={ratingMin || ''}
            onChange={(e) => onChange('rating_min', e.target.value || undefined)}
            className="h-11 w-full rounded-xl border border-[rgba(16,24,40,0.12)] bg-white px-4 text-sm text-[#475467]"
          >
            <option value="">Любой</option>
            <option value="4">4.0+</option>
            <option value="4.5">4.5+</option>
            <option value="4.8">4.8+</option>
          </select>
        </div>
      </div>
    </div>
  )
}

function MentorCardComponent({
  mentor,
  basePath,
  viewMode
}: {
  mentor: MentorCard
  basePath: string
  viewMode: 'grid' | 'list'
}) {
  const priceOptions = [mentor.price_30, mentor.price_60].filter(Boolean) as number[]
  const minPrice = priceOptions.length > 0 ? Math.min(...priceOptions) : null
  const rating = Number(mentor.rating_avg) || 0
  const ratingCount = mentor.rating_count || 0
  const hasSlots = (mentor as any)?.available_slots?.length > 0
  
  const cardClasses =
    'group rounded-2xl border border-[rgba(16,24,40,0.08)] bg-white transition-all duration-300 hover:border-primary/30 hover:shadow-lg'

  if (viewMode === 'list') {
    return (
      <Link to={`${basePath}/${mentor.user_id}`} className="block">
        <div className={`${cardClasses} p-6 md:flex md:items-center md:gap-6`}>
          <div className="flex items-start gap-4 flex-shrink-0">
            <div className="relative h-24 w-24 rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 overflow-hidden">
              {getImageUrl(mentor.avatar_url) ? (
                <img 
                  src={getImageUrl(mentor.avatar_url)!} 
                  alt={mentor.name || 'Ментор'} 
                  className="h-full w-full object-cover" 
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center text-3xl font-bold text-primary">
                  {(mentor.name || 'М')[0].toUpperCase()}
                </div>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-bold text-[#101828] group-hover:text-primary transition-colors">
                    {mentor.name || 'Ментор'}
                  </h3>
                  {mentor.headline && (
                    <p className="text-sm text-[#475467] mt-1">{mentor.headline}</p>
                  )}
                </div>
                <div className="flex items-center gap-1.5 rounded-lg bg-[rgba(28,63,227,0.08)] px-3 py-1.5 flex-shrink-0">
                  <Star className="h-4 w-4 fill-primary text-primary" />
                  <span className="text-sm font-semibold text-primary">{rating.toFixed(1)}</span>
                  {ratingCount > 0 && (
                    <span className="text-xs text-[#475467]">({ratingCount})</span>
                  )}
                </div>
              </div>
              {(mentor.city || mentor.country) && (
                <div className="flex items-center gap-1.5 text-xs text-[#667085] mb-3">
                  <MapPin className="h-3.5 w-3.5" />
                  <span>{[mentor.city, mentor.country].filter(Boolean).join(', ')}</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-4 mt-4 md:mt-0 md:flex-shrink-0">
            <div className="flex-1 md:flex-none min-w-0">
              <div className="text-xs font-medium text-[#667085] mb-1">Стоимость</div>
              <div className="text-lg font-bold text-[#101828] break-words">
                {minPrice !== null ? `от ${minPrice.toLocaleString()} ₸` : 'По запросу'}
              </div>
              <div className="text-xs text-[#667085]">30/60 мин</div>
            </div>
            <div className="flex flex-col gap-2 w-full md:w-auto md:min-w-[140px]">
              <Button variant="gradient" className="h-10 w-full md:w-auto" size="sm">
                Записаться
              </Button>
              <Button variant="outline" className="h-10 w-full md:w-auto" size="sm">
                Профиль
              </Button>
            </div>
          </div>
        </div>
      </Link>
    )
  }

  return (
    <Link to={`${basePath}/${mentor.user_id}`} className="block h-full">
      <div className={`${cardClasses} p-5 h-full flex flex-col`}>
        {/* Header with avatar and name */}
        <div className="flex items-start gap-3 mb-4">
          <div className="relative h-16 w-16 rounded-xl bg-gradient-to-br from-primary/10 to-primary/5 overflow-hidden flex-shrink-0">
            {getImageUrl(mentor.avatar_url) ? (
              <img 
                src={getImageUrl(mentor.avatar_url)!} 
                alt={mentor.name || 'Ментор'} 
                className="h-full w-full object-cover" 
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-xl font-bold text-primary">
                {(mentor.name || 'М')[0].toUpperCase()}
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-1">
              <h3 className="text-base font-bold text-[#101828] group-hover:text-primary transition-colors">
                {mentor.name || 'Ментор'}
              </h3>
              <div className="flex items-center gap-1 rounded-md bg-[rgba(28,63,227,0.08)] px-2 py-0.5 flex-shrink-0">
                <Star className="h-3.5 w-3.5 fill-primary text-primary" />
                <span className="text-xs font-semibold text-primary">{rating.toFixed(1)}</span>
              </div>
            </div>
            {mentor.headline && (
              <p className="text-xs text-[#667085] mb-1.5">{mentor.headline}</p>
            )}
            {(mentor.city || mentor.country) && (
              <div className="flex items-center gap-1 text-xs text-[#667085]">
                <MapPin className="h-3 w-3" />
                <span>{[mentor.city, mentor.country].filter(Boolean).join(', ')}</span>
              </div>
            )}
          </div>
        </div>


        {/* Info cards */}
        <div className="grid grid-cols-2 gap-2 mb-4">
          <div className="rounded-lg border border-[rgba(28,63,227,0.12)] bg-[rgba(28,63,227,0.03)] p-2.5">
            <div className="flex items-center gap-1.5 mb-1">
              <Clock className="h-3.5 w-3.5 text-primary" />
              <span className="text-xs font-medium text-[#101828]">Доступность</span>
            </div>
            <div className="text-xs text-[#667085]">
              {hasSlots ? 'Есть слоты' : 'По запросу'}
            </div>
          </div>
          <div className="rounded-lg border border-[rgba(255,180,87,0.3)] bg-[rgba(255,180,87,0.05)] p-2.5 min-w-0">
            <div className="text-xs font-medium text-[#101828] mb-1">Стоимость</div>
            <div className="text-sm font-bold text-[#101828] break-words">
              {minPrice !== null ? `от ${minPrice.toLocaleString()} ₸` : 'По запросу'}
            </div>
            <div className="text-[10px] text-[#667085] mt-0.5">30/60 мин</div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2 mt-auto">
          <Button variant="gradient" className="h-9 w-full" size="sm">
            Записаться
          </Button>
          <Button variant="outline" className="h-9 w-full" size="sm">
            Смотреть профиль
          </Button>
        </div>
      </div>
    </Link>
  )
}
