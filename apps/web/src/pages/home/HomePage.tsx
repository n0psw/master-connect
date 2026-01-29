import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { ArrowRight, CheckCircle2, Star, Users, Award, Shield, BookOpen, Instagram, ExternalLink, ChevronLeft, ChevronRight, MapPin, GraduationCap } from 'lucide-react'
import { useQuery } from 'react-query'
import { useState, useRef, useEffect } from 'react'

import { Button } from '@/shared/ui/button'
import { mentorsApi } from '@/shared/api/mentors'
import { getImageUrl } from '@/shared/utils/imageUtils'
import type { MentorCard } from '@/shared/types/mentors'

const trustPoints = [
  {
    icon: Award,
    title: 'Опыт в образовании',
    description: 'Мы давно работаем в сфере IELTS и SAT подготовки в Казахстане, знаем специфику поступления и требования университетов.'
  },
  {
    icon: Users,
    title: 'Профессиональные консультанты',
    description: 'Наши менторы — это эксперты с реальным опытом поступления и обучения в топовых университетах мира.'
  },
  {
    icon: Shield,
    title: 'Прозрачность и надежность',
    description: 'Честные цены, понятный процесс консультаций, гарантия качества и поддержка на каждом этапе.'
  },
  {
    icon: BookOpen,
    title: 'Фокус на результате',
    description: 'Мы предоставляем консультации по поступлению, которые дают конкретные ответы и четкий план действий.'
  }
]

interface InstagramPost {
  url: string
  postId: string
  imageSrc: string
}

const InstagramPostCard = ({ post }: { post: InstagramPost }) => {
  return (
    <a
      href={post.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group relative aspect-square rounded-lg overflow-hidden border border-gray-200 hover:border-primary/50 hover:shadow-xl transition-all bg-gray-100"
    >
      <img src={post.imageSrc} alt="Instagram пост" className="w-full h-full object-cover" />
      <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="bg-white/90 backdrop-blur-sm rounded-full p-2 shadow-lg">
          <ExternalLink className="h-4 w-4 text-gray-900" />
        </div>
      </div>
      <div className="absolute bottom-3 left-3 opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="bg-white/90 backdrop-blur-sm rounded-full px-3 py-1.5 flex items-center gap-1.5">
          <Instagram className="h-4 w-4 text-gray-900" />
          <span className="text-xs font-medium text-gray-900">Смотреть пост</span>
        </div>
      </div>
    </a>
  )
}

const MentorCardComponent = ({ mentor }: { mentor: MentorCard }) => {
  const prices = [mentor.price_30, mentor.price_60].filter((p): p is number => p !== null && p !== undefined)
  const minPrice = prices.length > 0 ? Math.min(...prices) : null
  const rating = Number(mentor.rating_avg) || 0
  const avatarUrl = getImageUrl(mentor.avatar_url)
  const university = mentor.university
  const mainLanguages = mentor.languages?.slice(0, 2) || []

  return (
    <Link to={`/mentors/${mentor.user_id}`} className="block">
      <div className="group rounded-2xl border border-gray-200 bg-white p-6 transition-all hover:border-primary/30 hover:shadow-lg">
        <div className="flex items-start gap-4 mb-4">
          <div className="relative h-16 w-16 rounded-xl bg-gray-100 overflow-hidden flex-shrink-0">
            {avatarUrl ? (
              <img src={avatarUrl} alt={mentor.name || 'Ментор'} className="h-full w-full object-cover" />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-2xl font-semibold text-primary">
                {(mentor.name || 'М')[0].toUpperCase()}
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary transition-colors">
              {mentor.name || 'Ментор'}
            </h3>
            {mentor.headline && (
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">{mentor.headline}</p>
            )}
          </div>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center gap-2 flex-wrap">
            {university && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-gradient-to-r from-primary/10 to-indigo-500/10 text-primary border border-primary/20">
                <GraduationCap className="h-3 w-3 mr-1" />
                {university}
              </span>
            )}
            {mainLanguages.length > 0 && (
              <div className="flex gap-1.5">
                {mainLanguages.map((lang) => (
                  <span key={lang} className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-gray-700">
                    {lang}
                  </span>
                ))}
              </div>
            )}
            {rating > 0 && (
              <div className="flex items-center gap-1 text-sm text-gray-600 ml-auto">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                <span className="font-medium">{rating.toFixed(1)}</span>
              </div>
            )}
          </div>
          
          {mentor.bio && (
            <p className="text-sm text-gray-600 line-clamp-2">{mentor.bio}</p>
          )}
          
          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <div>
              <div className="text-xs text-gray-500">Стоимость</div>
              <div className="text-base font-semibold text-gray-900">
                {minPrice !== null ? `от ${minPrice.toLocaleString()} ₸` : 'По запросу'}
              </div>
            </div>
            <Button variant="outline" size="sm" className="h-9">
              Подробнее
            </Button>
          </div>
        </div>
      </div>
    </Link>
  )
}

const MentorSliderCard = ({ mentor }: { mentor: MentorCard }) => {
  const prices = [mentor.price_30, mentor.price_60].filter((p): p is number => p !== null && p !== undefined)
  const minPrice = prices.length > 0 ? Math.min(...prices) : null
  const rating = Number(mentor.rating_avg) || 0
  const avatarUrl = getImageUrl(mentor.avatar_url)
  const location = [mentor.city, mentor.country].filter(Boolean).join(', ')
  const mainLanguages = mentor.languages?.slice(0, 2) || []
  const university = mentor.university

  return (
    <Link to={`/mentors/${mentor.user_id}`} className="block h-full">
      <div className="group rounded-3xl bg-gradient-to-br from-white via-white to-indigo-50/60 p-7 md:p-8 h-full flex flex-col gap-5 shadow-[0_24px_60px_rgba(15,23,42,0.2)] transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_32px_80px_rgba(15,23,42,0.25)]">
        <div className="flex items-start gap-5">
          <div className="relative h-28 w-28 rounded-3xl bg-gradient-to-br from-primary/15 via-indigo-500/10 to-blue-500/10 overflow-hidden flex-shrink-0 ring-4 ring-white shadow-lg">
            {avatarUrl ? (
              <img src={avatarUrl} alt={mentor.name || 'Ментор'} className="h-full w-full object-cover" />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-3xl font-semibold text-primary">
                {(mentor.name || 'М')[0].toUpperCase()}
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0 space-y-2">
            <div className="flex items-start justify-between gap-2">
              <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary transition-colors">
                {mentor.name || 'Ментор'}
              </h3>
              {rating > 0 && (
                <div className="inline-flex items-center gap-1.5 rounded-full bg-yellow-50 px-3 py-1.5">
                  <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm font-bold text-gray-900">{rating.toFixed(1)}</span>
                </div>
              )}
            </div>
            {location && (
              <div className="text-sm text-gray-500 truncate flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" />
                {location}
              </div>
            )}
            {mentor.headline && (
              <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">{mentor.headline}</p>
            )}
          </div>
        </div>

        <div className="space-y-4 flex-1">
          {university && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-gradient-to-r from-primary/10 to-indigo-500/10 text-primary border border-primary/20">
                <GraduationCap className="h-3.5 w-3.5 mr-1.5" />
                {university}
              </span>
            </div>
          )}
          {mainLanguages.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {mainLanguages.map((lang) => (
                <span
                  key={lang}
                  className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-gray-700"
                >
                  {lang}
                </span>
              ))}
            </div>
          )}
          {mentor.bio && (
            <p className="text-sm text-gray-700 line-clamp-3 leading-relaxed">
              {mentor.bio}
            </p>
          )}
        </div>

        <div className="pt-5 border-t border-gray-100 mt-auto flex items-center justify-between">
          <div>
            <div className="text-xs text-gray-500 mb-1">Стоимость консультации</div>
            <div className="text-xl font-bold text-gray-900">
              {minPrice !== null ? `от ${minPrice.toLocaleString()} ₸` : 'По запросу'}
            </div>
          </div>
          <div className="inline-flex items-center justify-center rounded-full bg-primary text-white h-12 w-12 group-hover:translate-x-1 group-hover:scale-110 transition-all shadow-lg">
            <ArrowRight className="h-5 w-5" />
          </div>
        </div>
      </div>
    </Link>
  )
}

const MentorSlider = ({ mentors }: { mentors: MentorCard[] }) => {
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    setCurrentIndex(0)
  }, [mentors])

  if (mentors.length === 0) return null

  const showArrows = mentors.length > 1
  const currentMentor = mentors[Math.min(currentIndex, mentors.length - 1)]

  const goTo = (direction: 'left' | 'right') => {
    if (!showArrows) return
    setCurrentIndex((prev) => {
      if (direction === 'left') {
        return prev === 0 ? mentors.length - 1 : prev - 1
      }
      return prev === mentors.length - 1 ? 0 : prev + 1
    })
  }

  return (
    <div className="relative flex items-center justify-center">
      {showArrows && (
        <button
          onClick={() => goTo('left')}
          className="absolute -left-4 top-1/2 -translate-y-1/2 z-10 bg-white/90 backdrop-blur-sm rounded-full p-2 shadow-lg border border-gray-200 hover:bg-gray-50 transition-all"
          aria-label="Предыдущий консультант"
        >
          <ChevronLeft className="h-5 w-5 text-gray-700" />
        </button>
      )}
      <div className="w-full max-w-md md:max-w-lg lg:max-w-xl transition-transform duration-300">
        <MentorSliderCard mentor={currentMentor} />
      </div>
      {showArrows && (
        <button
          onClick={() => goTo('right')}
          className="absolute -right-4 top-1/2 -translate-y-1/2 z-10 bg-white/90 backdrop-blur-sm rounded-full p-2 shadow-lg border border-gray-200 hover:bg-gray-50 transition-all"
          aria-label="Следующий консультант"
        >
          <ChevronRight className="h-5 w-5 text-gray-700" />
        </button>
      )}
    </div>
  )
}

export const HomePage = () => {
  const { data: mentorsData, isLoading, error } = useQuery(
    ['mentors', 'homepage'],
    () => mentorsApi.getMentors({ page: 1, page_size: 6, sort: 'rating_desc' }),
    { 
      staleTime: 5 * 60 * 1000,
      retry: 2,
      refetchOnWindowFocus: false
    }
  )

  const displayedMentors = mentorsData?.mentors?.slice(0, 6) || []

  return (
    <>
      <Helmet>
        <title>MasterConnect — консультации по поступлению</title>
        <meta
          name="description"
          content="Одноразовые консультации по поступлению от экспертов с опытом IELTS и SAT подготовки в Казахстане. Профессиональная помощь в выборе университета и подготовке документов."
        />
      </Helmet>

      <div className="flex flex-col min-h-screen bg-white relative">
        <div className="fixed inset-0 pointer-events-none z-0 hidden sm:block">
          <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute top-40 right-20 w-96 h-96 bg-gradient-to-br from-indigo-400/15 to-purple-400/15 rounded-full blur-3xl" />
          <div className="absolute bottom-20 left-1/4 w-80 h-80 bg-gradient-to-br from-violet-400/10 to-fuchsia-400/10 rounded-full blur-3xl" />
          <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-gradient-to-br from-cyan-400/15 to-blue-400/15 rounded-full blur-2xl animate-pulse delay-1000" />
        </div>
        <section className="relative border-b border-gray-100 overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(99,102,241,0.1),transparent_50%)]" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(59,130,246,0.08),transparent_50%)]" />
          <div className="absolute top-10 right-10 w-32 h-32 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 rounded-full blur-2xl hidden sm:block" />
          <div className="absolute bottom-20 left-20 w-40 h-40 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-2xl hidden sm:block" />
          <div className="absolute top-1/3 left-1/4 w-24 h-24 bg-gradient-to-br from-cyan-500/15 to-blue-500/15 rounded-full blur-xl hidden sm:block" />
          
          <div className="container-wide py-12 sm:py-16 lg:py-24 relative px-4 sm:px-6">
            <div className="grid lg:grid-cols-[1.1fr_1fr] gap-8 lg:gap-12 items-center">
              <div className="space-y-6 sm:space-y-8">
                <div className="space-y-4 sm:space-y-6">
                  <div className="inline-flex items-center gap-2">
                    <div className="h-1 w-8 sm:w-12 bg-gradient-to-r from-primary to-indigo-500" />
                    <span className="text-xs sm:text-sm font-semibold text-primary uppercase tracking-wider">
                      Master Education
                    </span>
                  </div>
                  <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-gray-900 leading-[1.1]">
                    Консультации по{' '}
                    <span className="bg-gradient-to-r from-primary to-indigo-600 bg-clip-text text-transparent">
                      поступлению
                </span>
                    <br />
                    от экспертов
                  </h1>
                  <p className="text-base sm:text-lg md:text-xl text-gray-700 max-w-xl leading-relaxed">
                    Мы давно работаем в сфере IELTS и SAT подготовки в Казахстане. Теперь помогаем с поступлением в зарубежные университеты через профессиональные консультации.
                  </p>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                  <Button variant="gradient" size="lg" className="h-12 sm:h-14 px-6 sm:px-10 text-base sm:text-lg font-semibold w-full sm:w-auto" asChild>
                    <Link to="/mentors">
                      Выбрать консультанта
                      <ArrowRight className="h-4 w-4 sm:h-5 sm:w-5 ml-2" />
                    </Link>
                  </Button>
                  <Button variant="outline" size="lg" className="h-12 sm:h-14 px-6 sm:px-10 text-base sm:text-lg w-full sm:w-auto" asChild>
                    <Link to="/about">О компании</Link>
                  </Button>
                </div>
                
                <div className="grid grid-cols-2 gap-4 sm:gap-6 pt-2 sm:pt-4">
                  <div className="space-y-1">
                    <div className="text-2xl sm:text-3xl font-bold text-primary">4000+</div>
                    <div className="text-xs sm:text-sm text-gray-600">Успешных кейсов</div>
              </div>
                  <div className="space-y-1">
                    <div className="text-2xl sm:text-3xl font-bold text-primary">IELTS & SAT</div>
                    <div className="text-xs sm:text-sm text-gray-600">Подготовка</div>
              </div>
            </div>
          </div>
              
              <div className="hidden lg:block">
                {isLoading ? (
                  <div className="relative">
                    <div className="absolute -inset-4 bg-gradient-to-r from-primary/20 via-indigo-200/30 to-blue-200/20 rounded-3xl blur-2xl opacity-50" />
                    <div className="relative bg-white/80 backdrop-blur-sm rounded-2xl p-12 border border-white/60 shadow-xl text-center">
                      <Users className="h-16 w-16 text-gray-300 mx-auto mb-4 animate-pulse" />
                      <p className="text-gray-500">Загрузка консультантов...</p>
              </div>
            </div>
                ) : error ? (
                  <div className="relative">
                    <div className="absolute -inset-4 bg-gradient-to-r from-primary/20 via-indigo-200/30 to-blue-200/20 rounded-3xl blur-2xl opacity-50" />
                    <div className="relative bg-white/80 backdrop-blur-sm rounded-2xl p-12 border border-white/60 shadow-xl text-center">
                      <Users className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500 mb-2">Не удалось загрузить консультантов</p>
                      <p className="text-sm text-gray-400">Попробуйте обновить страницу</p>
                    </div>
                  </div>
                ) : displayedMentors.length > 0 ? (
                  <div className="relative">
                    <div className="absolute -inset-6 bg-gradient-to-r from-primary/20 via-indigo-200/30 to-blue-200/20 rounded-3xl blur-3xl opacity-60" />
                    <div className="relative bg-white/90 backdrop-blur-md rounded-3xl p-8 border border-white/80 shadow-2xl">
                      <div className="mb-6">
                        <h3 className="text-xl font-bold text-gray-900 mb-2">Наши консультанты</h3>
                        <p className="text-sm text-gray-600">Эксперты с опытом в топовых университетах</p>
                      </div>
                      <MentorSlider mentors={displayedMentors} />
                      </div>
                    </div>
                ) : (
                  <div className="relative">
                    <div className="absolute -inset-4 bg-gradient-to-r from-primary/20 via-indigo-200/30 to-blue-200/20 rounded-3xl blur-2xl opacity-50" />
                    <div className="relative bg-white/80 backdrop-blur-sm rounded-2xl p-12 border border-white/60 shadow-xl text-center">
                      <Users className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">Консультанты пока не добавлены</p>
                  </div>
                </div>
                )}
              </div>
            </div>
          </div>
        </section>

        <section className="container-wide py-12 sm:py-16 lg:py-20 relative px-4 sm:px-6">
          <div className="absolute top-10 right-20 w-48 h-48 bg-gradient-to-br from-indigo-400/10 to-purple-400/10 rounded-full blur-3xl hidden sm:block" />
          <div className="absolute bottom-10 left-10 w-56 h-56 bg-gradient-to-br from-blue-400/10 to-cyan-400/10 rounded-full blur-3xl hidden sm:block" />
          <div className="max-w-4xl mx-auto space-y-6 sm:space-y-8 relative z-10">
            <div className="text-center space-y-3 sm:space-y-4">
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">О компании</h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Master Education — мы обучили более 4000 стуеднтов. Являемся одними из лидеров на рынке подготовки к IELTS и SAT в Казахстане. У нас есть успешные кейсы по поступлению в топовые университеты мира. 
              </p>
              </div>
            <div className="grid md:grid-cols-2 gap-6 pt-8">
              <div className="space-y-3">
                <h3 className="text-xl font-semibold text-gray-900">Наши направления</h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span>Подготовка к SAT & IELTS</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span>Поступление в зарубежные университеты</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span>Консультации по поступлению</span>
                  </li>
                </ul>
            </div>
              <div className="space-y-3">
                <h3 className="text-xl font-semibold text-gray-900">Наш подход</h3>
                <p className="text-gray-600">
                  Мы работаем по системе, а не по мотивации. Доводим до точного результата, а не оставляем учиться самим. Каждый студент получает персональную поддержку и четкий план действий.
                </p>
                    </div>
                  </div>
                </div>
        </section>

        <section className="bg-gray-50 py-12 sm:py-16 lg:py-20 relative overflow-hidden px-4 sm:px-6">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-gradient-to-br from-violet-400/8 to-fuchsia-400/8 rounded-full blur-3xl hidden sm:block" />
          <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-gradient-to-br from-indigo-400/8 to-purple-400/8 rounded-full blur-3xl hidden sm:block" />
          <div className="container-wide relative z-10">
            <div className="max-w-5xl mx-auto">
              <div className="text-center space-y-3 sm:space-y-4 mb-8 sm:mb-12">
                <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Наши партнёры</h2>
                <p className="text-lg text-gray-600">
                  Мы сотрудничаем с ведущими образовательными организациями и программами
                </p>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 md:gap-6">
                {[
                  { 
                    name: 'IDP IELTS', 
                    description: 'IDP IELTS',
                    image: '/partners/idpielts.png',
                    url: 'https://www.idp.com',
                    alt: 'IDP IELTS'
                  },
                  { 
                    name: 'NIS Alumni', 
                    description: 'NIS Alumni',
                    image: '/partners/alumni.png',
                    url: 'https://nis.edu.kz',
                    alt: 'NIS Alumni'
                  },
                  { 
                    name: 'Hyperion', 
                    description: 'Hyperion',
                    image: '/partners/hyperion.webp',
                    url: '#',
                    alt: 'Hyperion'
                  },
                  { 
                    name: 'МДК', 
                    description: 'Молодёжное движение корейцев Казахстана',
                    image: '/partners/mdk.png',
                    url: '#',
                    alt: 'Молодёжное движение корейцев Казахстана'
                  },
                  { 
                    name: 'NOVA MUN', 
                    description: 'NOVA MUN',
                    image: '/partners/mun.webp',
                    url: 'https://www.instagram.com/novamun.kz/',
                    alt: 'NOVA MUN'
                  }
                ].map((partner) => (
                  <a
                    key={partner.name}
                    href={partner.url}
                    target={partner.url !== '#' ? '_blank' : undefined}
                    rel={partner.url !== '#' ? 'noopener noreferrer' : undefined}
                    className="group flex flex-col items-center justify-center p-4 md:p-6 rounded-xl border border-gray-200 bg-white hover:border-primary/40 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 aspect-square min-h-[120px]"
                  >
                    <div className="relative w-full flex-1 flex items-center justify-center mb-2">
                      <img
                        src={partner.image}
                        alt={partner.alt}
                        className="max-w-[90%] max-h-[70px] md:max-h-[80px] object-contain w-auto h-auto opacity-70 group-hover:opacity-100 transition-opacity duration-300"
                        loading="lazy"
                        decoding="async"
                        width="120"
                        height="80"
                      />
                    </div>
                    {partner.description && (
                      <div className="text-[10px] md:text-xs text-gray-500 text-center leading-tight mt-auto pt-2">
                        {partner.description}
                      </div>
                    )}
                  </a>
                ))}
              </div>
            </div>
          </div>
        </section>

        {displayedMentors.length > 0 && (
          <section className="bg-gray-50 py-12 sm:py-16 lg:py-20 relative overflow-hidden px-4 sm:px-6">
            <div className="absolute top-10 left-10 w-80 h-80 bg-gradient-to-br from-indigo-400/10 to-purple-400/10 rounded-full blur-3xl hidden sm:block" />
            <div className="absolute bottom-10 right-20 w-72 h-72 bg-gradient-to-br from-blue-400/10 to-cyan-400/10 rounded-full blur-3xl hidden sm:block" />
            <div className="container-wide relative">
              <div className="text-center space-y-3 sm:space-y-4 mb-8 sm:mb-12">
                <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Наши консультанты</h2>
                <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto px-4 sm:px-0">
                  Профессиональные эксперты с опытом поступления и работы в топовых университетах. Каждый консультант прошел проверку и имеет реальные достижения.
              </p>
            </div>
              <div className="grid gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-3">
                {displayedMentors.map((mentor) => (
                  <MentorCardComponent key={mentor.user_id} mentor={mentor} />
                ))}
              </div>
              <div className="text-center mt-12">
                <Button variant="outline" size="lg" asChild>
              <Link to="/mentors">
                    Смотреть всех консультантов
                    <ArrowRight className="h-5 w-5 ml-2" />
              </Link>
            </Button>
          </div>
          </div>
        </section>
        )}

        <section className="container-wide py-12 sm:py-16 lg:py-20 px-4 sm:px-6">
          <div className="max-w-4xl mx-auto space-y-8 sm:space-y-12">
            <div className="text-center space-y-3 sm:space-y-4">
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Почему нам доверяют</h2>
              <p className="text-base sm:text-lg text-gray-600">
                Мы строим доверие через профессионализм, прозрачность и реальный опыт
                </p>
              </div>
            <div className="grid md:grid-cols-2 gap-8">
              {trustPoints.map((point) => {
                const Icon = point.icon
                return (
                  <div key={point.title} className="space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                        <Icon className="h-6 w-6 text-primary" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900">{point.title}</h3>
                  </div>
                    <p className="text-gray-600">{point.description}</p>
              </div>
                )
              })}
            </div>
          </div>
        </section>

        <section className="container-wide py-12 sm:py-16 lg:py-20 px-4 sm:px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center space-y-3 sm:space-y-4 mb-8 sm:mb-12">
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Следите за нами в Instagram</h2>
              <p className="text-base sm:text-lg text-gray-600">
                Реальные кейсы, истории поступления и советы от наших экспертов
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6 sm:gap-8">
              <div className="rounded-2xl border border-gray-200 bg-white p-4 sm:p-6 md:p-8 space-y-4 sm:space-y-6">
                <div className="flex items-center gap-4">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500">
                    <img
                      src="/masteredlogo-ico.ico"
                      alt="Master Education Logo"
                      className="h-10 w-10" // Slightly bigger to match logo's real size proportions
                    />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">@master.education</h3>
                    <p className="text-sm text-gray-600">Более 4000+ довольных клиентов</p>
                  </div>
                </div>
                <p className="text-gray-600">
                  В нашем Instagram вы найдете реальные истории поступления, отзывы студентов, советы по подготовке к IELTS и SAT, а также информацию о наших партнёрствах и мероприятиях.
                </p>
                <a
                  href="https://www.instagram.com/master.education/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 px-6 py-3 text-white font-semibold hover:opacity-90 transition-opacity w-full justify-center"
                >
                  <Instagram className="h-5 w-5" />
                  Подписаться в Instagram
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>

              <div className="rounded-2xl border border-gray-200 bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 p-8 space-y-6">
                <h3 className="text-xl font-bold text-gray-900">Что вы найдёте в нашем Instagram:</h3>
                <ul className="space-y-3">
                  {[
                    'Реальные истории поступления студентов',
                    'Советы по подготовке к IELTS и SAT',
                    'Информацию о партнёрствах и мероприятиях',
                    'Отзывы и результаты наших студентов',
                    'Актуальные новости и обновления'
                  ].map((item, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
                <div className="pt-4 border-t border-gray-200">
                  <p className="text-sm text-gray-600 mb-4">Недавние посты:</p>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {[
                      { url: 'https://www.instagram.com/p/DHnfWBTio8M/', postId: 'DHnfWBTio8M', imageSrc: '/inst/1.jpg' }, 
                      { url: 'https://www.instagram.com/p/DTVVMCNCNpi/', postId: 'DTVVMCNCNpi', imageSrc: '/inst/2.jpg' },
                      { url: 'https://www.instagram.com/p/DSxKz8CDFCE/', postId: 'DSxKz8CDFCE', imageSrc: '/inst/3.jpg' }
                    ].map((post) => (
                      <InstagramPostCard key={post.postId} post={post} />
                    ))}
              </div>
                  <a
                    href="https://www.instagram.com/master.education/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-primary hover:underline mt-4"
                  >
                    Смотреть все посты
                    <ExternalLink className="h-3 w-3" />
                  </a>
            </div>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-gray-50 py-12 sm:py-16 lg:py-20 relative overflow-hidden px-4 sm:px-6">
          <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-blue-400/8 to-indigo-400/8 rounded-full blur-3xl hidden sm:block" />
          <div className="absolute bottom-0 right-0 w-80 h-80 bg-gradient-to-br from-purple-400/8 to-violet-400/8 rounded-full blur-3xl hidden sm:block" />
          <div className="container-wide relative">
            <div className="max-w-3xl mx-auto text-center space-y-6 sm:space-y-8">
              <div className="space-y-3 sm:space-y-4">
                <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Готовы начать?</h2>
                <p className="text-base sm:text-lg text-gray-600">
                  Выберите консультанта и получите персональную консультацию по поступлению уже сегодня
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
                <Button variant="gradient" size="lg" className="h-12 px-6 sm:px-8 w-full sm:w-auto" asChild>
                  <Link to="/mentors">
                    Выбрать консультанта
                    <ArrowRight className="h-4 w-4 sm:h-5 sm:w-5 ml-2" />
                  </Link>
                </Button>
                <Button variant="outline" size="lg" className="h-12 px-6 sm:px-8 w-full sm:w-auto" asChild>
                  <Link to="/faq">Частые вопросы</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </>
  )
}
