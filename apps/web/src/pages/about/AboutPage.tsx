import { Helmet } from 'react-helmet-async'
import { Users, Globe2, Award, Target, Sparkles, ArrowRight, Play } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/shared/ui/button'

const milestones = [
  { year: '2019', title: 'Старт MasterConnect', description: 'Запустили платформу и первую группу наставников из топовых университетов.' },
  { year: '2021', title: '1 000 консультаций', description: 'Провели тысячу консультаций и расширили команду академических менторов.' },
  { year: '2023', title: 'Международное сообщество', description: 'Наставники из 50 стран и партнёрства с университетами и фондами.' },
  { year: '2025', title: 'Новый продукт поступления', description: 'Запустили карьерные лаборатории и готовим студентов к магистратуре и MBA.' }
]

const values = [
  { title: 'Качество результата', description: 'Каждый наставник имеет кейсы поступлений в топовые программы и проходит регулярный аудит.', icon: Award },
  { title: 'Прозрачность', description: 'Открытые профили менторов, доступ к реальным отзывам и понятная стоимость.', icon: Target },
  { title: 'Поддержка', description: 'Личная команда кураторов сопровождает студента и контролирует дедлайны.', icon: Users },
  { title: 'Глобальность', description: 'Менторы из 50+ стран, консультации на русском, английском и других языках.', icon: Globe2 },
  { title: 'Инновации', description: 'Используем формат спринтов, аналитические дашборды и AI-помощника для эссе.', icon: Sparkles },
  { title: 'Сообщество', description: 'Закрытые встречи выпускников и база кейсов поступления с шаблонами документов.', icon: Play }
]

const vettingSteps = [
  'Заявка и проверка достижений',
  'Интервью с академической командой',
  'Онбординг и тренинг по платформе',
  'Пилотные консультации и обратная связь',
  'Регулярный аудит качества и NPS'
]

const leaders = [
  { name: 'Айсулу Касымбек', role: 'CEO и соосновательница', bio: 'Выпускница Harvard Kennedy School, 8 лет помогает студентам из СНГ поступать в зарубежные университеты.' },
  { name: 'Тимур Бектуров', role: 'Head of Mentor Success', bio: 'Выпускник University of Cambridge, курирует отбор и обучение наставников.' },
  { name: 'Мадина Аман', role: 'Product Lead', bio: 'Экс-менеджер в EdTech стартапе, отвечает за цифровой опыт студентов.' },
  { name: 'Игорь Ли', role: 'Head of Admissions Strategy', bio: '10 лет в приёмных комиссиях университетов США и Европы.' }
]

export const AboutPage = () => {
  return (
    <>
      <Helmet>
        <title>О MasterConnect — платформа наставничества для поступления</title>
        <meta
          name="description"
          content="Узнайте, как MasterConnect помогает студентам поступать в ведущие университеты мира: миссия, команда, ценности и подход к наставничеству."
        />
      </Helmet>

      <div className="bg-gradient-to-b from-[#f5f6ff] via-white to-white">
        <section className="gradient-bg">
          <div className="container-wide py-24 lg:py-32 grid gap-16 lg:grid-cols-[1.1fr_0.9fr] items-end">
            <div className="space-y-8">
              <div className="space-y-4">
                <span className="inline-flex items-center gap-2 rounded-full bg-white/70 px-4 py-2 text-xs font-semibold text-primary shadow-sm">
                  Прозрачная подготовка к поступлению
                </span>
                <h1 className="text-4xl sm:text-5xl lg:text-[56px] font-bold text-[#101828] leading-tight">
                  Мы создаём экосистему наставников, которые проводят тебя к университету мечты
                </h1>
                <p className="text-lg text-[#475467] max-w-2xl">
                  MasterConnect — платформа, где студенты получают персонализированную стратегию поступления, поддержку менторов из ведущих университетов и инструменты для контроля прогресса.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-3">
                <Button variant="gradient" size="lg" className="h-12 px-6" asChild>
                  <Link to="/register">Стать студентом</Link>
                </Button>
                <Button variant="outline" size="lg" className="h-12 px-6 border-[rgba(16,24,40,0.12)]" asChild>
                  <Link to="/mentor/apply">Присоединиться как наставник</Link>
                </Button>
              </div>
            </div>
            <div className="rounded-[32px] border border-[rgba(28,63,227,0.12)] bg-white/80 backdrop-blur shadow-[0_30px_80px_-60px_rgba(28,63,227,0.5)] p-8 space-y-6">
              <div className="text-sm uppercase tracking-[0.3em] text-[#475467]">Ключевые показатели</div>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <div className="text-4xl font-bold text-[#101828]">2 000+</div>
                  <p className="text-sm text-[#475467] mt-2">Студентов поступили с поддержкой MasterConnect</p>
                </div>
                <div>
                  <div className="text-4xl font-bold text-[#101828]">95%</div>
                  <p className="text-sm text-[#475467] mt-2">Рекомендуют нас друзьям после первой консультации</p>
                </div>
                <div>
                  <div className="text-4xl font-bold text-[#101828]">50+</div>
                  <p className="text-sm text-[#475467] mt-2">Стран присутствия менторов и студентов</p>
                </div>
                <div>
                  <div className="text-4xl font-bold text-[#101828]">12%</div>
                  <p className="text-sm text-[#475467] mt-2">Процент наставников, прошедших отбор в команду</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="container-wide py-20 space-y-12">
          <div className="grid gap-10 lg:grid-cols-[1fr_1fr] items-center">
            <div className="space-y-5">
              <h2 className="text-3xl sm:text-4xl font-bold text-[#101828]">Наша миссия</h2>
              <p className="text-lg text-[#475467]">
                Мы верим, что каждый студент заслуживает наставника, который уже прошёл путь поступления и готов поделиться опытом. Наша миссия — сделать качественное наставничество доступным и дать студентам уверенность в каждом шаге до оффера.
              </p>
              <div className="rounded-[28px] border border-[rgba(28,63,227,0.12)] bg-[rgba(28,63,227,0.05)] px-6 py-5 text-sm text-[#344054]">
                «MasterConnect — это не просто подбор наставника. Это команда, которая разделяет твою цель, берёт ответственность за результат и помогает принять взвешенные решения.»
              </div>
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-full bg-[rgba(28,63,227,0.08)]" />
                <div>
                  <div className="text-lg font-semibold text-[#101828]">Айсулу Касымбек</div>
                  <div className="text-sm text-[#475467]">Соосновательница MasterConnect</div>
                </div>
              </div>
            </div>
            <div className="space-y-6">
              <h3 className="text-xl font-semibold text-[#101828]">Как работает платформа</h3>
              <div className="grid gap-4">
                {[
                  'Алгоритм подбирает наставников по цели, бюджету и дедлайнам студента.',
                  'Ментор и студент формируют дорожную карту и фиксируют задачи внутри платформы.',
                  'Команда кураторов следит за прогрессом, помогает с документами и дедлайнами.'
                ].map((item) => (
                  <div key={item} className="flex items-start gap-3 rounded-[20px] border border-[rgba(16,24,40,0.08)] bg-white px-5 py-4 text-sm text-[#475467]">
                    <span className="mt-1 h-2 w-2 rounded-full bg-primary" />
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-[36px] border border-[rgba(16,24,40,0.08)] bg-white px-10 py-12 shadow-[0_40px_120px_-80px_rgba(16,24,40,0.55)]">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
              <div>
                <span className="uppercase tracking-[0.3em] text-primary text-sm">Хронология</span>
                <h2 className="mt-4 text-3xl font-bold text-[#101828]">Как развивался MasterConnect</h2>
              </div>
              <Link to="/today" className="inline-flex items-center gap-2 rounded-full border border-[rgba(16,24,40,0.12)] px-5 py-2 text-sm font-semibold text-[#475467] hover:text-primary">
                Узнать о проектах
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
            <div className="mt-10 grid gap-8 lg:grid-cols-4">
              {milestones.map((milestone) => (
                <div key={milestone.year} className="space-y-3">
                  <div className="text-sm font-semibold text-primary uppercase">{milestone.year}</div>
                  <div className="text-xl font-semibold text-[#101828]">{milestone.title}</div>
                  <p className="text-sm text-[#475467]">{milestone.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="bg-[rgba(28,63,227,0.06)] py-20">
          <div className="container-wide space-y-10">
            <div className="space-y-4 text-center">
              <span className="uppercase tracking-[0.3em] text-[#475467] text-sm">Ценности</span>
              <h2 className="text-3xl sm:text-4xl font-bold text-[#101828]">Во что мы верим</h2>
              <p className="text-lg text-[#475467] max-w-3xl mx-auto">
                Мы строим платформу, где сочетается честность, экспертиза и технологичность. Это помогает студентам двигаться вперёд с уверенностью.
              </p>
            </div>
            <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
              {values.map((value) => (
                <div key={value.title} className="rounded-[28px] border border-[rgba(28,63,227,0.1)] bg-white px-6 py-6 shadow-[0_30px_70px_-60px_rgba(16,24,40,0.45)]">
                  <value.icon className="h-6 w-6 text-primary" />
                  <div className="mt-4 text-lg font-semibold text-[#101828]">{value.title}</div>
                  <p className="mt-2 text-sm text-[#475467]">{value.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="container-wide py-20">
          <div className="grid gap-12 lg:grid-cols-[0.9fr_1.1fr] items-start">
            <div className="space-y-6">
              <span className="uppercase tracking-[0.3em] text-[#475467] text-sm">Отбор наставников</span>
              <h2 className="text-3xl font-bold text-[#101828]">Как мы формируем команду</h2>
              <p className="text-lg text-[#475467]">
                Мы тщательно проверяем опыт каждого наставника: дипломы, достижения, референсы и кейсы поступления. Только 12% кандидатов проходят все этапы.
              </p>
              <div className="rounded-[28px] border border-[rgba(28,63,227,0.12)] bg-white px-6 py-6 shadow-[0_30px_70px_-60px_rgba(16,24,40,0.5)] space-y-3">
                {vettingSteps.map((step, index) => (
                  <div key={step} className="flex items-start gap-3 text-sm text-[#475467]">
                    <span className="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-[rgba(28,63,227,0.08)] text-xs font-semibold text-primary">
                      {index + 1}
                    </span>
                    {step}
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-6">
              <div className="rounded-[32px] border border-[rgba(16,24,40,0.08)] bg-white p-8 shadow-[0_40px_120px_-80px_rgba(16,24,40,0.55)]">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                  <div className="space-y-3">
                    <h3 className="text-2xl font-bold text-[#101828]">Команда MasterConnect</h3>
                    <p className="text-sm text-[#475467]">
                      Мы работаем вместе с наставниками, чтобы студенты чувствовали поддержку на каждом этапе.
                    </p>
                  </div>
                  <Button variant="gradient" className="h-11 px-5" asChild>
                    <Link to="/team">Познакомиться с командой</Link>
                  </Button>
                </div>
                <div className="mt-8 grid gap-6 md:grid-cols-2">
                  {leaders.map((leader) => (
                    <div key={leader.name} className="rounded-[24px] border border-[rgba(16,24,40,0.1)] bg-[rgba(28,63,227,0.05)] px-5 py-5">
                      <div className="text-lg font-semibold text-[#101828]">{leader.name}</div>
                      <div className="text-sm text-primary mt-1">{leader.role}</div>
                      <p className="text-sm text-[#475467] mt-3">{leader.bio}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-[#0f1c3c] text-white">
          <div className="container-wide py-20 space-y-10">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
              <div className="space-y-4 max-w-xl">
                <span className="uppercase tracking-[0.3em] text-white/60 text-sm">Партнёры</span>
                <h2 className="text-3xl sm:text-4xl font-bold">С нами работают фонды и университеты</h2>
                <p className="text-lg text-white/70">
                  Мы проводим совместные программы с образовательными фондами, участвуем в университетских ярмарках и делимся аналитикой поступления.
                </p>
              </div>
              <Button variant="outline" className="h-12 px-6 border-white/30 text-white hover:bg-white hover:text-[#0f1c3c]" asChild>
                <Link to="/media-kit">Скачать медиакит</Link>
              </Button>
            </div>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {['Yessenov Foundation', 'Nazarbayev University', 'Bolashaq', 'Global UGRAD'].map((partner) => (
                <div key={partner} className="rounded-[28px] border border-white/12 bg-white/5 px-6 py-6 text-center text-white/80 backdrop-blur">
                  {partner}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="container-wide py-20">
          <div className="rounded-[36px] border border-[rgba(28,63,227,0.1)] bg-white px-12 py-12 shadow-[0_50px_140px_-90px_rgba(28,63,227,0.55)] flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
            <div className="space-y-4 max-w-xl">
              <span className="uppercase tracking-[0.3em] text-primary text-sm">Следующий шаг</span>
              <h2 className="text-3xl sm:text-4xl font-bold text-[#101828]">Присоединяйся к MasterConnect и создаём истории успеха вместе</h2>
              <p className="text-lg text-[#475467]">
                Если ты студент — получишь наставника и команду, которые поведут к офферу. Если наставник — делись опытом и развивайся вместе с нами.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
              <Button variant="gradient" className="h-12 px-6" asChild>
                <Link to="/mentors">Подобрать наставника</Link>
              </Button>
              <Button variant="outline" className="h-12 px-6 border-[rgba(16,24,40,0.12)]" asChild>
                <Link to="/mentor/apply">Стать наставником</Link>
              </Button>
            </div>
          </div>
        </section>
      </div>
    </>
  )
}
