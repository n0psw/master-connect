import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { ArrowRight, Sparkles, ShieldCheck, GraduationCap, CalendarClock, Quote, Play, CheckCircle2, ArrowUpRight } from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { Card, CardContent } from '@/shared/ui/card'

const heroStats = [
  { label: 'Студентов поступили', value: '2 000+', icon: Sparkles },
  { label: 'Проверенных наставников', value: '500+', icon: ShieldCheck },
  { label: 'Средний рейтинг', value: '4.9/5', icon: GraduationCap }
]

const universities = ['Harvard', 'Oxford', 'MIT', 'NYU', 'Cambridge', 'ETH Zürich']

const journeyStages = [
  {
    title: 'Диагностика целей',
    description: 'Анализируем цели, уровень подготовки и сроки, формируем стратегию поступления.',
    bullets: ['Онлайн-встреча с наставником', 'Разбор сильных и слабых сторон'],
    accent: 'bg-[rgba(28,63,227,0.08)] border border-[rgba(28,63,227,0.16)]'
  },
  {
    title: 'План поступления',
    description: 'Составляем индивидуальный роадмап с дедлайнами и чек-листами.',
    bullets: ['Подбор программ и университетов', 'Календарь подготовки и заданий'],
    accent: 'bg-[rgba(122,92,255,0.08)] border border-[rgba(122,92,255,0.16)]'
  },
  {
    title: 'Поддержка до зачисления',
    description: 'Работаем над документами, помогаем с эссе, интервью и стипендиями.',
    bullets: ['Редакция эссе и портфолио', 'Подготовка к интервью и мотивационным письмам'],
    accent: 'bg-[rgba(255,180,87,0.08)] border border-[rgba(255,180,87,0.16)]'
  }
]

const testimonials = [
  {
    name: 'Айжан Садыкова',
    university: 'University of Cambridge',
    quote:
      'Благодаря наставнику из MasterConnect я прошла весь путь поступления без стресса. Мы вместе выстроили стратегию, подготовили эссе и портфолио.',
    rating: '5.0'
  },
  {
    name: 'Илья Папаев',
    university: 'MIT',
    quote:
      'Наставник помог подготовиться к собеседованиям и прокачал мотивационное письмо. Получил оффер из мечты и стипендию.',
    rating: '4.9'
  },
  {
    name: 'Анель Мухамеджан',
    university: 'NYU',
    quote:
      'Очень ценно, что каждый созвон был конкретным. Я получала обратную связь по проектам и понимала, что делать дальше.',
    rating: '5.0'
  }
]

const spotlightMentors = [
  {
    name: 'Дария Салимова',
    headline: 'Brown University • Международные отношения',
    languages: ['Русский', 'English'],
    price: 'от 18 000 ₸',
    availability: 'Свободны слоты на этой неделе'
  },
  {
    name: 'Нурлан Айдар',
    headline: 'ETH Zürich • Инженерия',
    languages: ['Русский', 'Deutsch', 'English'],
    price: 'от 22 000 ₸',
    availability: 'Доступны вечерние консультации'
  },
  {
    name: 'Мария Чжан',
    headline: 'University of Toronto • Data Science',
    languages: ['Русский', 'English', '中文'],
    price: 'от 19 500 ₸',
    availability: 'Есть групповая сессия'
  }
]

const timeline = [
  {
    title: 'Подбор наставника',
    copy: 'Находим идеального специалиста под ваши цели и университеты.',
    order: '01'
  },
  {
    title: 'План и контроль точек',
    copy: 'Фиксируем дорожную карту, назначаем чекпоинты и обратную связь.',
    order: '02'
  },
  {
    title: 'Проработка заявок',
    copy: 'Работаем над эссе, портфолио, мотивацией и собеседованиями.',
    order: '03'
  },
  {
    title: 'Оффер и зачисление',
    copy: 'Разбираем предложения, помогаем с визой и переездом.',
    order: '04'
  }
]

export const HomePage = () => {
  return (
    <>
      <Helmet>
        <title>MasterConnect — наставники для поступления мечты</title>
        <meta
          name="description"
          content="Персональные консультации от студентов и выпускников топовых университетов. Индивидуальная стратегия и поддержка до зачисления."
        />
      </Helmet>

      <div className="flex flex-col min-h-screen bg-gradient-to-b from-[#f5f6ff] via-white to-white">
        <section className="gradient-bg">
          <div className="container-wide py-24 lg:py-32">
            <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-16 items-center">
              <div className="space-y-10">
                <span className="inline-flex items-center gap-2 rounded-full bg-white/80 px-4 py-2 text-sm font-medium text-primary shadow-[0_12px_30px_-20px_rgba(28,63,227,0.6)]">
                  <Sparkles className="h-4 w-4" />
                  Наставничество уровня мировых университетов
                </span>
                <div className="space-y-6">
                  <h1 className="text-4xl sm:text-5xl lg:text-[64px] leading-tight font-extrabold text-[#101828]">
                    Найди наставника и поступи в университет мечты
                  </h1>
                  <p className="text-lg sm:text-xl text-[#475467] max-w-xl">
                    Подберем ментора, который прошел твой путь и подготовит стратегию с эссе, интервью, стипендиями и таймингом подачи.
                  </p>
                </div>
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button variant="gradient" size="lg" className="h-14 px-8 text-base" asChild>
                    <Link to="/mentors">
                      Подобрать наставника
                      <ArrowRight className="h-5 w-5" />
                    </Link>
                  </Button>
                  <Button variant="outline" size="lg" className="h-14 px-8 text-base border-[rgba(16,24,40,0.12)]" asChild>
                    <Link to="/about">Бесплатная консультация</Link>
                  </Button>
                </div>
                <div className="grid gap-4 sm:grid-cols-3">
                  {heroStats.map((item) => (
                    <Card key={item.label} className="border-none bg-white/70 backdrop-blur shadow-[0_18px_45px_-30px_rgba(28,63,227,0.6)]">
                      <CardContent className="p-5 flex flex-col gap-2">
                        <div className="flex items-center gap-2 text-sm text-[#475467]">
                          <item.icon className="h-4 w-4 text-primary" />
                          {item.label}
                        </div>
                        <div className="text-2xl font-bold text-[#101828]">{item.value}</div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
              <div className="relative">
                <div className="absolute inset-0 rounded-[32px] bg-gradient-to-tr from-[#1c3fe3]/25 via-[#7a5cff]/20 to-transparent blur-3xl" />
                <div className="relative rounded-[32px] bg-white shadow-[0_40px_80px_-40px_rgba(28,63,227,0.45)] p-8 space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-semibold uppercase tracking-wide text-[#475467]">Трекинг поступления</div>
                    <CalendarClock className="h-6 w-6 text-primary" />
                  </div>
                  <div className="space-y-4">
                    {timeline.slice(0, 3).map((step) => (
                      <div key={step.title} className="rounded-2xl border border-[rgba(28,63,227,0.12)] bg-[rgba(28,63,227,0.04)] px-5 py-4">
                        <div className="text-xs font-semibold text-primary uppercase tracking-wide">{step.order}</div>
                        <div className="mt-2 text-base font-semibold text-[#101828]">{step.title}</div>
                        <p className="text-sm text-[#475467]">{step.copy}</p>
                      </div>
                    ))}
                  </div>
                  <Button variant="gradient" className="w-full h-12" asChild>
                    <Link to="/register">Присоединиться</Link>
                  </Button>
                </div>
              </div>
            </div>
            <div className="mt-16">
              <p className="text-sm uppercase tracking-[0.2em] text-[#475467] mb-4">Наши наставники учатся и преподают в</p>
              <div className="flex flex-wrap gap-6 lg:gap-10 text-[#101828] text-base font-semibold opacity-80">
                {universities.map((name) => (
                  <span key={name} className="rounded-full bg-white/70 px-4 py-2 shadow-[0_10px_30px_-24px_rgba(16,24,40,0.4)]">
                    {name}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="container-wide py-16 lg:py-20">
          <div className="rounded-[28px] border border-[rgba(16,24,40,0.08)] bg-white shadow-[0_32px_80px_-48px_rgba(16,24,40,0.45)] px-8 md:px-14 py-12">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-10">
              <div className="space-y-4 max-w-2xl">
                <span className="text-sm uppercase tracking-[0.25em] text-[#475467]">Как устроено наставничество</span>
                <h2 className="text-3xl sm:text-4xl font-bold text-[#101828]">Путь студента с нами</h2>
                <p className="text-lg text-[#475467]">
                  Работаем в формате спринтов, созваниваемся каждую неделю, проверяем задания и фиксируем прогресс в личном кабинете.
                </p>
              </div>
              <div className="flex gap-4 overflow-x-auto pb-2">
                {['Диагностика', 'Стратегия', 'Документы', 'Интервью', 'Зачисление'].map((chip) => (
                  <span
                    key={chip}
                    className="whitespace-nowrap rounded-full border border-[rgba(28,63,227,0.15)] bg-[rgba(28,63,227,0.06)] px-4 py-2 text-sm text-[#1c3fe3]"
                  >
                    {chip}
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-12 space-y-10">
              {journeyStages.map((stage, index) => (
                <div
                  key={stage.title}
                  className={`rounded-[24px] ${stage.accent} px-8 py-10 grid lg:grid-cols-[1.2fr_0.8fr] gap-10 items-center`}
                >
                  <div className="space-y-5">
                    <div className="inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-xs font-semibold text-primary shadow-sm">
                      Этап {index + 1}
                    </div>
                    <h3 className="text-2xl font-bold text-[#101828]">{stage.title}</h3>
                    <p className="text-base text-[#475467]">{stage.description}</p>
                    <ul className="space-y-2">
                      {stage.bullets.map((bullet) => (
                        <li key={bullet} className="flex items-start gap-3 text-sm text-[#344054]">
                          <CheckCircle2 className="h-4 w-4 text-primary mt-1 shrink-0" />
                          {bullet}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="relative">
                    <div className="absolute inset-0 rounded-[28px] bg-gradient-to-br from-white/80 to-white/20 blur-xl" />
                    <div className="relative rounded-[28px] border border-[rgba(255,255,255,0.45)] bg-white/80 backdrop-blur p-6 shadow-[0_30px_60px_-48px_rgba(16,24,40,0.5)] space-y-4">
                      <div className="flex items-center justify-between text-sm text-[#475467]">
                        <span>Активности наставника</span>
                        <ArrowUpRight className="h-4 w-4 text-primary" />
                      </div>
                      <div className="space-y-3">
                        {['Совместный план', 'Чек-листы', 'Обратная связь в 48 часов', 'Подготовка к интервью'].map((task) => (
                          <div key={task} className="flex items-center gap-3 rounded-2xl border border-[rgba(28,63,227,0.08)] bg-white px-4 py-3 text-sm text-[#344054]">
                            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[rgba(28,63,227,0.08)] text-primary">✓</span>
                            {task}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="bg-[#0f1c3c] text-white">
          <div className="container-wide py-20 space-y-12">
            <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
              <div>
                <span className="uppercase tracking-[0.3em] text-white/60 text-sm">Истории поступления</span>
                <h2 className="mt-4 text-3xl lg:text-4xl font-bold">Результаты студентов MasterConnect</h2>
              </div>
              <Link to="/mentors" className="inline-flex items-center gap-2 rounded-full border border-white/25 px-5 py-2 text-sm font-semibold text-white/90 hover:text-white">
                Читать все истории
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {testimonials.map((item) => (
                <div key={item.name} className="rounded-[24px] border border-white/12 bg-white/5 px-6 py-8 space-y-5 backdrop-blur">
                  <Quote className="h-6 w-6 text-[#7a5cff]" />
                  <p className="text-base leading-relaxed text-white/80">{item.quote}</p>
                  <div>
                    <div className="text-lg font-semibold">{item.name}</div>
                    <div className="text-sm text-white/60">{item.university}</div>
                    <div className="mt-2 inline-flex items-center gap-1 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold">
                      Рейтинг {item.rating}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="container-wide py-20">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-10">
            <div className="space-y-4 max-w-xl">
              <span className="uppercase tracking-[0.28em] text-[#475467] text-sm">Лучшие наставники недели</span>
              <h2 className="text-3xl sm:text-4xl font-bold text-[#101828]">Наставники, которые готовы подключиться</h2>
              <p className="text-lg text-[#475467]">
                Собеседуем каждого наставника и берем в команду только 12% претендентов. Смотрите видео-презентацию перед выбором.
              </p>
            </div>
            <Button variant="gradient" className="h-12 px-6" asChild>
              <Link to="/mentors">
                Смотреть всех наставников
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>
          <div className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {spotlightMentors.map((mentor) => (
              <div key={mentor.name} className="group rounded-[28px] border border-[rgba(16,24,40,0.1)] bg-white p-6 shadow-[0_30px_70px_-50px_rgba(16,24,40,0.5)] transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_40px_100px_-60px_rgba(28,63,227,0.6)]">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-xl font-semibold text-[#101828]">{mentor.name}</div>
                    <div className="text-sm text-[#475467]">{mentor.headline}</div>
                  </div>
                  <button className="flex h-10 w-10 items-center justify-center rounded-full border border-[rgba(28,63,227,0.12)] text-primary">
                    <Play className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-6 flex flex-wrap gap-2 text-xs font-medium text-[#475467]">
                  {mentor.languages.map((lang) => (
                    <span key={lang} className="rounded-full bg-[rgba(28,63,227,0.08)] px-3 py-1 text-primary">
                      {lang}
                    </span>
                  ))}
                </div>
                <div className="mt-6 flex items-center justify-between">
                  <div>
                    <div className="text-sm text-[#475467]">Стоимость</div>
                    <div className="text-lg font-semibold text-[#101828]">{mentor.price}</div>
                  </div>
                  <div className="rounded-full bg-[rgba(34,197,94,0.12)] px-4 py-1 text-xs font-semibold text-[#067647]">{mentor.availability}</div>
                </div>
                <div className="mt-8 flex gap-3">
                  <Button variant="gradient" className="flex-1 h-11" asChild>
                    <Link to="/mentors">Записаться</Link>
                  </Button>
                  <Button variant="outline" className="flex-1 h-11 border-[rgba(16,24,40,0.1)]" asChild>
                    <Link to="/mentors">Открыть профиль</Link>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-[rgba(28,63,227,0.06)]">
          <div className="container-wide py-20">
            <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] items-center">
              <div className="space-y-4">
                <span className="uppercase tracking-[0.28em] text-[#475467] text-sm">Пошаговый план</span>
                <h2 className="text-3xl sm:text-4xl font-bold text-[#101828]">Работаем до оффера, а не до часа</h2>
                <p className="text-lg text-[#475467]">
                  От первой встречи до переезда сопровождаем каждый шаг. В календаре отображаются дедлайны, а наставник комментирует каждый документ.
                </p>
              </div>
              <div className="grid gap-6 md:grid-cols-2">
                {timeline.map((step) => (
                  <div key={step.title} className="rounded-[20px] border border-[rgba(28,63,227,0.12)] bg-white px-6 py-6 shadow-[0_20px_60px_-48px_rgba(16,24,40,0.4)]">
                    <div className="text-xs font-semibold uppercase tracking-[0.3em] text-primary">{step.order}</div>
                    <div className="mt-3 text-lg font-semibold text-[#101828]">{step.title}</div>
                    <p className="mt-2 text-sm text-[#475467]">{step.copy}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="container-wide py-20">
          <div className="rounded-[32px] border border-[rgba(28,63,227,0.12)] bg-white shadow-[0_50px_120px_-60px_rgba(28,63,227,0.5)] px-10 py-12 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-10">
            <div className="space-y-4 max-w-xl">
              <span className="uppercase tracking-[0.3em] text-primary text-sm">Гайд по поступлению</span>
              <h2 className="text-3xl font-bold text-[#101828]">Скачай чек-лист подготовки и начни с правильного шага</h2>
              <p className="text-lg text-[#475467]">
                Собрали практические советы от менторов и студентов, которые получили оффер в 2024. Узнай, как распределить сроки и избежать ошибок.
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="email"
                  placeholder="Твой email"
                  className="h-12 w-full rounded-full border border-[rgba(16,24,40,0.12)] bg-white px-6 text-sm outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                />
                <Button variant="gradient" className="h-12 px-6">Получить гайд</Button>
              </div>
              <span className="text-xs text-[#475467]">Отправляем раз в месяц. Можно отписаться в любой момент.</span>
            </div>
            <div className="relative">
              <div className="absolute inset-0 rounded-[32px] bg-gradient-to-br from-[#1c3fe3]/25 to-transparent blur-2xl" />
              <div className="relative rounded-[28px] border border-[rgba(28,63,227,0.12)] bg-[rgba(28,63,227,0.06)] px-10 py-12 text-center text-[#101828]">
                <div className="text-6xl font-extrabold text-gradient">95%</div>
                <p className="mt-4 text-sm text-[#475467]">студентов рекомендуют MasterConnect друзьям</p>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-[#0f1c3c]">
          <div className="container-wide py-20 text-white">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-10">
              <div className="space-y-4 max-w-xl">
                <span className="uppercase tracking-[0.3em] text-white/60 text-sm">Готовы начать</span>
                <h2 className="text-3xl sm:text-4xl font-bold">Начни путь к офферу уже сегодня</h2>
                <p className="text-lg text-white/70">
                  Создай профиль, получи подборку наставников и назначь бесплатный вводный созвон.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button variant="gradient" className="h-12 px-6" asChild>
                  <Link to="/mentors">Подобрать наставника</Link>
                </Button>
                <Button variant="outline" className="h-12 px-6 border-white/40 text-white hover:bg-white hover:text-[#0f1c3c]" asChild>
                  <Link to="/register">Создать аккаунт</Link>
                </Button>
              </div>
            </div>
            <div className="mt-10 flex flex-wrap gap-4 text-xs text-white/60">
              {['Безопасная оплата', 'Поддержка 7/7', 'Документы проверяют эксперты', 'Персональная стратегия'].map((item) => (
                <span key={item} className="rounded-full border border-white/20 px-4 py-2">{item}</span>
              ))}
            </div>
          </div>
        </section>
      </div>
    </>
  )
}
