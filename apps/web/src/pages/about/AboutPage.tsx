import { Helmet } from 'react-helmet-async'
import { Award, Target, Users, BookOpen, CheckCircle2, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/shared/ui/button'

const experienceTimeline = [
  {
    period: 'Начало',
    title: 'IELTS и SAT подготовка',
    description: 'Мы начали с подготовки студентов к международным экзаменам IELTS и SAT в Казахстане. Это дало нам глубокое понимание требований зарубежных университетов.'
  },
  {
    period: 'Развитие',
    title: 'Накопление экспертизы',
    description: 'Годы работы в образовательной сфере помогли нам понять специфику поступления, требования к документам и стратегии успешных заявок.'
  },
  {
    period: 'Сейчас',
    title: 'Консультации по поступлению',
    description: 'Теперь мы помогаем студентам с поступлением через одноразовые консультации, делясь накопленным опытом и знаниями.'
  }
]

const values = [
  { title: 'Опыт и экспертиза', description: 'Многолетний опыт в IELTS и SAT подготовке дает нам глубокое понимание процесса поступления.', icon: Award },
  { title: 'Прозрачность', description: 'Честные цены, понятный процесс консультаций, открытые профили консультантов.', icon: Target },
  { title: 'Профессионализм', description: 'Каждый консультант проходит проверку и имеет реальный опыт поступления.', icon: Users },
  { title: 'Фокус на результате', description: 'Одноразовые консультации, которые дают конкретные ответы и четкий план действий.', icon: BookOpen }
]

export const AboutPage = () => {
  return (
    <>
      <Helmet>
        <title>О компании MasterConnect — консультации по поступлению</title>
        <meta
          name="description"
          content="Мы давно работаем в сфере IELTS и SAT подготовки в Казахстане. Теперь помогаем студентам с поступлением через одноразовые консультации от экспертов."
        />
      </Helmet>

      <div className="bg-white relative">
        <div className="fixed inset-0 pointer-events-none z-0 hidden sm:block">
          <div className="absolute top-20 right-10 w-80 h-80 bg-gradient-to-br from-indigo-400/15 to-purple-400/15 rounded-full blur-3xl" />
          <div className="absolute top-1/3 left-20 w-72 h-72 bg-gradient-to-br from-blue-400/12 to-cyan-400/12 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-gradient-to-br from-violet-400/10 to-fuchsia-400/10 rounded-full blur-3xl" />
        </div>
        <section className="border-b border-gray-100 relative">
          <div className="absolute top-10 right-20 w-48 h-48 bg-gradient-to-br from-purple-400/10 to-pink-400/10 rounded-full blur-2xl hidden sm:block" />
          <div className="container-wide py-12 sm:py-16 lg:py-24 relative px-4 sm:px-6">
            <div className="max-w-4xl mx-auto space-y-6 sm:space-y-8">
              <div className="text-center space-y-3 sm:space-y-4">
                <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
                  О компании MasterConnect
                </h1>
                <p className="text-base sm:text-lg md:text-xl text-gray-600 max-w-2xl mx-auto px-4 sm:px-0">
                  Мы давно работаем в сфере IELTS и SAT подготовки в Казахстане. Наш опыт в образовательной сфере помогает студентам делать правильный выбор и готовить сильные заявки в зарубежные университеты.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center px-4 sm:px-0">
                <Button variant="gradient" size="lg" className="h-12 px-6 sm:px-8 w-full sm:w-auto" asChild>
                  <Link to="/mentors">Выбрать консультанта</Link>
                </Button>
                <Button variant="outline" size="lg" className="h-12 px-6 sm:px-8 w-full sm:w-auto" asChild>
                  <Link to="/faq">Частые вопросы</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        <section className="container-wide py-12 sm:py-16 lg:py-20 relative px-4 sm:px-6">
          <div className="absolute top-20 left-10 w-64 h-64 bg-gradient-to-br from-indigo-400/10 to-purple-400/10 rounded-full blur-3xl hidden sm:block" />
          <div className="absolute bottom-20 right-10 w-56 h-56 bg-gradient-to-br from-blue-400/10 to-cyan-400/10 rounded-full blur-3xl hidden sm:block" />
          <div className="max-w-4xl mx-auto space-y-8 sm:space-y-12 relative">
            <div className="space-y-4 sm:space-y-6">
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Наша миссия</h2>
              <p className="text-lg text-gray-600">
                Мы помогаем студентам делать правильный выбор и готовить сильные заявки в зарубежные университеты. Наш опыт в IELTS и SAT подготовке дает нам глубокое понимание требований и специфики поступления.
              </p>
              <p className="text-lg text-gray-600">
                Через одноразовые консультации мы делимся накопленными знаниями и помогаем студентам составить четкий план действий для успешного поступления.
              </p>
            </div>

            <div className="space-y-4 sm:space-y-6">
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Наш опыт</h2>
              <div className="space-y-6 sm:space-y-8">
                {experienceTimeline.map((item, index) => (
                  <div key={index} className="flex gap-6">
                    <div className="flex-shrink-0">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                        <CheckCircle2 className="h-5 w-5 text-primary" />
                      </div>
                    </div>
                    <div className="flex-1 space-y-2">
                      <div className="text-sm font-semibold text-primary uppercase tracking-wide">{item.period}</div>
                      <h3 className="text-xl font-semibold text-gray-900">{item.title}</h3>
                      <p className="text-gray-600">{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="bg-gray-50 py-12 sm:py-16 lg:py-20 relative overflow-hidden px-4 sm:px-6">
          <div className="absolute top-10 left-10 w-72 h-72 bg-gradient-to-br from-indigo-400/10 to-purple-400/10 rounded-full blur-3xl hidden sm:block" />
          <div className="absolute bottom-10 right-10 w-64 h-64 bg-gradient-to-br from-blue-400/10 to-cyan-400/10 rounded-full blur-3xl hidden sm:block" />
          <div className="container-wide relative">
            <div className="max-w-4xl mx-auto space-y-8 sm:space-y-12">
              <div className="text-center space-y-3 sm:space-y-4">
                <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Наши ценности</h2>
                <p className="text-base sm:text-lg text-gray-600">
                  Мы строим доверие через профессионализм, прозрачность и реальный опыт
                </p>
              </div>
              <div className="grid gap-6 sm:gap-8 md:grid-cols-2">
                {values.map((value) => {
                  const Icon = value.icon
                  return (
                    <div key={value.title} className="space-y-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                          <Icon className="h-6 w-6 text-primary" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900">{value.title}</h3>
                      </div>
                      <p className="text-gray-600">{value.description}</p>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </section>

        <section className="container-wide py-12 sm:py-16 lg:py-20 relative px-4 sm:px-6">
          <div className="absolute top-20 right-20 w-56 h-56 bg-gradient-to-br from-violet-400/10 to-fuchsia-400/10 rounded-full blur-3xl hidden sm:block" />
          <div className="absolute bottom-20 left-20 w-48 h-48 bg-gradient-to-br from-purple-400/10 to-pink-400/10 rounded-full blur-3xl hidden sm:block" />
          <div className="max-w-4xl mx-auto space-y-6 sm:space-y-8 relative">
            <div className="space-y-4 sm:space-y-6">
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Как мы работаем</h2>
              <p className="text-base sm:text-lg text-gray-600">
                Мы тщательно проверяем каждого консультанта: проверяем образование, достижения и опыт. Только проверенные эксперты с реальным опытом поступления попадают в нашу команду.
              </p>
              <div className="space-y-4 pt-4">
                {[
                  'Проверка образования и достижений консультанта',
                  'Оценка опыта в поступлении и работе с документами',
                  'Проверка способности давать качественные консультации',
                  'Регулярный контроль качества работы'
                ].map((step, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="bg-gray-50 py-12 sm:py-16 lg:py-20 px-4 sm:px-6">
          <div className="container-wide">
            <div className="max-w-3xl mx-auto text-center space-y-6 sm:space-y-8">
              <div className="space-y-3 sm:space-y-4">
                <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900">Готовы начать?</h2>
                <p className="text-base sm:text-lg text-gray-600">
                  Выберите консультанта и получите персональную консультацию по поступлению
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
