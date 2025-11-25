import { Helmet } from 'react-helmet-async'
import { Link } from 'react-router-dom'
import {
  Users,
  Target,
  Zap,
  Shield,
  Globe,
  Star,
  ChevronRight,
  BookOpen,
  TrendingUp,
  Heart,
  Award,
  Clock,
} from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { Card, CardContent } from '@/shared/ui/card'

export const AboutPage = () => {
  return (
    <>
      <Helmet>
        <title>О нас - MasterConnect</title>
        <meta 
          name="description" 
          content="MasterConnect - платформа для получения консультаций от успешных выпускников топовых университетов. Поступление в MIT, Harvard, Stanford и другие."
        />
      </Helmet>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Герой секция */}
        <div className="text-center mb-20 animate-fade-in-up">
          <h1 className="text-5xl md:text-7xl font-bold mb-8 leading-tight">
            Воплотим твои
            <span className="text-gradient block mt-2">образовательные мечты</span>
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-4xl mx-auto leading-relaxed">
            MasterConnect соединяет амбициозных студентов с успешными выпускниками 
            топовых университетов мира для персональных консультаций
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="text-lg px-8 py-6">
              <Link to="/mentors">
                Найти ментора
                <ChevronRight className="h-5 w-5 ml-2" />
              </Link>
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8 py-6" asChild>
              <Link to="/register">
                Начать обучение
              </Link>
            </Button>
          </div>
        </div>

        {/* Наша миссия */}
        <div className="mb-24">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Наша миссия</h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Мы создаем мосты между поколениями, помогая студентам достичь своих 
              образовательных целей через опыт тех, кто уже прошел этот путь
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="border-2 hover:border-primary/50 transition-all duration-300 hover:shadow-xl">
              <CardContent className="p-10 text-center">
                <Target className="h-16 w-16 text-blue-600 mx-auto mb-6" />
                <h3 className="text-2xl font-semibold mb-4">Цель</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Демократизировать доступ к качественному образовательному 
                  наставничеству для студентов из всех регионов
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-all duration-300 hover:shadow-xl">
              <CardContent className="p-10 text-center">
                <Heart className="h-16 w-16 text-red-500 mx-auto mb-6" />
                <h3 className="text-2xl font-semibold mb-4">Ценности</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Качество, доступность, персональный подход и взаимная 
                  поддержка в образовательном сообществе
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 hover:border-primary/50 transition-all duration-300 hover:shadow-xl">
              <CardContent className="p-10 text-center">
                <TrendingUp className="h-16 w-16 text-green-600 mx-auto mb-6" />
                <h3 className="text-2xl font-semibold mb-4">Результат</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Успешные поступления студентов в топовые университеты 
                  и построение успешной карьеры
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Как это работает - Timeline */}
        <div className="mb-24 bg-gradient-to-br from-blue-50/50 via-white to-indigo-50/30 rounded-3xl p-12">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Как это работает</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Простой процесс получения персональной консультации
            </p>
          </div>

          <div className="max-w-5xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
              {/* Шаг 1 */}
              <div className="flex gap-6">
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg flex-shrink-0">
                    <span className="text-2xl font-bold text-white">1</span>
                  </div>
                  <div className="w-1 flex-1 bg-gradient-to-b from-blue-600 to-indigo-200 mt-4"></div>
                </div>
                <div className="pb-12">
                  <h3 className="text-2xl font-semibold mb-3">Найди ментора</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Выбери ментора из топового университета по своей специальности. 
                    Посмотри отзывы и рейтинги.
                  </p>
                </div>
              </div>

              {/* Шаг 2 */}
              <div className="flex gap-6">
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg flex-shrink-0">
                    <span className="text-2xl font-bold text-white">2</span>
                  </div>
                  <div className="w-1 flex-1 bg-gradient-to-b from-blue-600 to-indigo-200 mt-4"></div>
                </div>
                <div className="pb-12">
                  <h3 className="text-2xl font-semibold mb-3">Забронируй время</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Выбери удобное время в расписании ментора и заполни 
                    анкету с вопросами для эффективной консультации.
                  </p>
                </div>
              </div>

              {/* Шаг 3 */}
              <div className="flex gap-6">
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg flex-shrink-0">
                    <span className="text-2xl font-bold text-white">3</span>
                  </div>
                  <div className="w-1 flex-1 bg-gradient-to-b from-blue-600 to-indigo-200 mt-4"></div>
                </div>
                <div className="pb-12">
                  <h3 className="text-2xl font-semibold mb-3">Получи консультацию</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Проведи 1-на-1 видео-консультацию с ментором через 
                    Google Meet в назначенное время.
                  </p>
                </div>
              </div>

              {/* Шаг 4 */}
              <div className="flex gap-6">
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg flex-shrink-0">
                    <span className="text-2xl font-bold text-white">4</span>
                  </div>
                </div>
                <div className="pb-12">
                  <h3 className="text-2xl font-semibold mb-3">Достигай целей</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Применяй полученные знания и рекомендации для достижения 
                    своих образовательных целей.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Преимущества */}
        <div className="mb-24">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Почему MasterConnect?</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Мы предлагаем больше, чем просто консультации
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            <div className="flex items-start space-x-6 p-6 rounded-2xl hover:bg-blue-50/50 transition-colors">
              <div className="w-14 h-14 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Users className="h-7 w-7 text-blue-600" />
              </div>
              <div>
                <h3 className="text-2xl font-semibold mb-3">Проверенные менторы</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Все наши менторы - выпускники топовых университетов с подтвержденными 
                  достижениями и опытом наставничества
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-6 p-6 rounded-2xl hover:bg-indigo-50/50 transition-colors">
              <div className="w-14 h-14 rounded-xl bg-indigo-100 flex items-center justify-center flex-shrink-0">
                <Shield className="h-7 w-7 text-indigo-600" />
              </div>
              <div>
                <h3 className="text-2xl font-semibold mb-3">Безопасность</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Защищенная платформа для проведения консультаций с гарантией 
                  конфиденциальности и возврата средств
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-6 p-6 rounded-2xl hover:bg-green-50/50 transition-colors">
              <div className="w-14 h-14 rounded-xl bg-green-100 flex items-center justify-center flex-shrink-0">
                <Zap className="h-7 w-7 text-green-600" />
              </div>
              <div>
                <h3 className="text-2xl font-semibold mb-3">Быстрый результат</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Получи конкретные советы и план действий уже после первой 
                  консультации с ментором
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-6 p-6 rounded-2xl hover:bg-purple-50/50 transition-colors">
              <div className="w-14 h-14 rounded-xl bg-purple-100 flex items-center justify-center flex-shrink-0">
                <Globe className="h-7 w-7 text-purple-600" />
              </div>
              <div>
                <h3 className="text-2xl font-semibold mb-3">Глобальность</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Менторы из университетов по всему миру - США, Великобритания, 
                  Канада, Германия и других стран
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-6 p-6 rounded-2xl hover:bg-orange-50/50 transition-colors">
              <div className="w-14 h-14 rounded-xl bg-orange-100 flex items-center justify-center flex-shrink-0">
                <Clock className="h-7 w-7 text-orange-600" />
              </div>
              <div>
                <h3 className="text-2xl font-semibold mb-3">Гибкий график</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Выбирай удобное время для консультаций с учетом разных 
                  часовых поясов
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-6 p-6 rounded-2xl hover:bg-yellow-50/50 transition-colors">
              <div className="w-14 h-14 rounded-xl bg-yellow-100 flex items-center justify-center flex-shrink-0">
                <Award className="h-7 w-7 text-yellow-600" />
              </div>
              <div>
                <h3 className="text-2xl font-semibold mb-3">Гарантия качества</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Система рейтингов и отзывов помогает выбрать лучшего ментора, 
                  а гарантия возврата защищает вас
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Статистика */}
        <div className="mb-24 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 rounded-3xl p-12 text-white">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Результаты говорят сами за себя</h2>
            <p className="text-xl opacity-90">Мы гордимся достижениями наших студентов</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-5xl md:text-6xl font-bold mb-3">500+</div>
              <p className="text-lg opacity-90">Проведенных консультаций</p>
            </div>

            <div>
              <div className="text-5xl md:text-6xl font-bold mb-3">150+</div>
              <p className="text-lg opacity-90">Опытных менторов</p>
            </div>

            <div>
              <div className="text-5xl md:text-6xl font-bold mb-3">4.9</div>
              <p className="text-lg opacity-90">Средний рейтинг</p>
            </div>

            <div>
              <div className="text-5xl md:text-6xl font-bold mb-3">85%</div>
              <p className="text-lg opacity-90">Успешных поступлений</p>
            </div>
          </div>
        </div>

        {/* Призыв к действию */}
        <div className="text-center bg-gradient-to-br from-blue-50 via-white to-indigo-50 rounded-3xl p-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">Начни свой путь к успеху уже сегодня</h2>
          <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-3xl mx-auto leading-relaxed">
            Получи персональную консультацию от выпускника университета мечты 
            и узнай, как достичь своих образовательных целей
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="text-lg px-8 py-6" asChild>
              <Link to="/mentors">
                <BookOpen className="h-5 w-5 mr-2" />
                Найти ментора
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8 py-6" asChild>
              <Link to="/register">
                <Star className="h-5 w-5 mr-2" />
                Зарегистрироваться
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </>
  )
}
