import { useState } from 'react'
import { Helmet } from 'react-helmet-async'
import { Link } from 'react-router-dom'
import { ChevronDown, ChevronRight, HelpCircle, MessageCircle, Mail } from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { Card, CardContent } from '@/shared/ui/card'

interface FAQItemProps {
  question: string
  answer: string
  isOpen: boolean
  onToggle: () => void
}

const FAQItem = ({ question, answer, isOpen, onToggle }: FAQItemProps) => {
  return (
    <Card className="mb-4">
      <CardContent className="p-0">
        <button
          className="w-full p-6 text-left flex items-center justify-between hover:bg-muted/50 transition-colors"
          onClick={onToggle}
        >
          <span className="font-semibold pr-4">{question}</span>
          {isOpen ? (
            <ChevronDown className="h-5 w-5 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-5 w-5 text-muted-foreground" />
          )}
        </button>
        {isOpen && (
          <div className="px-6 pb-6">
            <div className="text-muted-foreground leading-relaxed">
              {answer.split('\n').map((paragraph, index) => (
                <p key={index} className={index > 0 ? 'mt-4' : ''}>
                  {paragraph}
                </p>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export const FAQPage = () => {
  const [openItems, setOpenItems] = useState<Set<number>>(new Set([0]))

  const toggleItem = (index: number) => {
    const newOpenItems = new Set(openItems)
    if (newOpenItems.has(index)) {
      newOpenItems.delete(index)
    } else {
      newOpenItems.add(index)
    }
    setOpenItems(newOpenItems)
  }

  const faqData = [
    {
      question: "Что такое MasterConnect?",
      answer: "MasterConnect — это платформа для одноразовых консультаций по поступлению в зарубежные университеты. Мы давно работаем в сфере IELTS и SAT подготовки в Казахстане, и теперь помогаем студентам с поступлением через консультации от проверенных экспертов."
    },
    {
      question: "Какой у вас опыт в IELTS/SAT подготовке?",
      answer: "Мы работаем в сфере IELTS и SAT подготовки в Казахстане уже много лет. Этот опыт дал нам глубокое понимание требований зарубежных университетов, специфики поступления и того, что нужно для успешной заявки. Теперь мы используем этот опыт для консультаций по поступлению."
    },
    {
      question: "Как проходят консультации по поступлению?",
      answer: "Консультации проходят в формате видео-звонков через нашу платформу. Это одноразовые консультации, где вы получаете конкретные ответы на ваши вопросы и четкий план действий. Длительность может быть 30 или 60 минут в зависимости от ваших потребностей."
    },
    {
      question: "Что входит в одноразовую консультацию?",
      answer: "В консультацию входит разбор вашей ситуации, ответы на вопросы о поступлении, рекомендации по выбору университетов и программ, советы по подготовке документов и эссе, а также составление плана действий. Консультант даст вам конкретные рекомендации, которые вы сможете использовать самостоятельно."
    },
    {
      question: "Почему стоит выбрать вашу платформу?",
      answer: "Мы отличаемся многолетним опытом в образовательной сфере, проверенными консультантами с реальным опытом поступления, прозрачными ценами и честным подходом. Наш опыт в IELTS и SAT подготовке дает нам глубокое понимание процесса поступления и требований университетов."
    },
    {
      question: "Сколько стоят консультации?",
      answer: "Стоимость консультаций устанавливается каждым консультантом индивидуально и зависит от его опыта и специализации. Вы видите точную стоимость перед бронированием. Цены прозрачны и указаны в тенге."
    },
    {
      question: "Как я могу быть уверен в качестве консультантов?",
      answer: "Все наши консультанты проходят тщательную проверку — мы верифицируем их образование, достижения и опыт поступления. Также у каждого консультанта есть рейтинг и отзывы от предыдущих студентов, которые помогут вам сделать выбор."
    },
    {
      question: "Можно ли отменить или перенести консультацию?",
      answer: "Да, вы можете отменить или перенести консультацию не менее чем за 24 часа до назначенного времени. В случае отмены деньги будут возвращены на ваш счет. Консультанты также могут инициировать перенос в случае непредвиденных обстоятельств."
    },
    {
      question: "Какие способы оплаты принимаются?",
      answer: "Мы принимаем основные банковские карты и другие популярные способы оплаты. Оплата производится через защищенную систему, и ваши данные полностью конфиденциальны."
    },
    {
      question: "Что если я не удовлетворен консультацией?",
      answer: "Мы гарантируем качество наших услуг. Если вы не удовлетворены консультацией, свяжитесь с нашей службой поддержки в течение 48 часов, и мы рассмотрим возможность возврата средств или предоставления бесплатной повторной консультации."
    },
    {
      question: "Могу ли я получить консультацию на русском языке?",
      answer: "Да, многие наши консультанты владеют русским, английским, казахским и другими языками. При поиске консультанта вы можете фильтровать результаты по языку консультаций."
    },
    {
      question: "Есть ли групповые консультации?",
      answer: "В настоящее время мы фокусируемся на персональных одноразовых консультациях 1-на-1, которые обеспечивают максимальную эффективность и индивидуальный подход."
    }
  ]

  const studentFAQ = faqData.slice(0, 8)
  const mentorFAQ = faqData.slice(8)
  const generalFAQ = faqData.slice(0, 4)

  return (
    <>
      <Helmet>
        <title>Часто задаваемые вопросы - MasterConnect</title>
        <meta 
          name="description" 
          content="Ответы на часто задаваемые вопросы о консультациях по поступлению. Узнайте о нашем опыте в IELTS/SAT подготовке и как проходят консультации."
        />
      </Helmet>

      <div className="bg-white relative min-h-screen">
        <div className="fixed inset-0 pointer-events-none z-0 hidden sm:block">
          <div className="absolute top-20 left-10 w-96 h-96 bg-gradient-to-br from-violet-400/12 to-fuchsia-400/12 rounded-full blur-3xl" />
          <div className="absolute top-1/3 right-20 w-80 h-80 bg-gradient-to-br from-indigo-400/10 to-purple-400/10 rounded-full blur-3xl" />
          <div className="absolute bottom-20 left-1/4 w-72 h-72 bg-gradient-to-br from-blue-400/10 to-cyan-400/10 rounded-full blur-3xl" />
          <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-gradient-to-br from-pink-400/10 to-rose-400/10 rounded-full blur-2xl" />
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12 relative">
          <div className="text-center mb-8 sm:mb-12 space-y-3 sm:space-y-4">
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">Часто задаваемые вопросы</h1>
            <p className="text-base sm:text-lg text-gray-600 px-2 sm:px-0">
              Ответы на популярные вопросы о консультациях по поступлению
            </p>
          </div>

        <div className="mb-8 sm:mb-12 rounded-2xl border border-gray-200 bg-gray-50 p-4 sm:p-6 md:p-8">
          <h2 className="text-xl sm:text-2xl font-semibold text-gray-900 mb-3 sm:mb-4">О компании</h2>
          <p className="text-gray-600 mb-4">
            Мы давно работаем в сфере IELTS и SAT подготовки в Казахстане. Наш опыт в образовательной сфере и глубокое понимание процесса поступления помогают студентам делать правильный выбор и готовить сильные заявки в зарубежные университеты.
          </p>
          <p className="text-gray-600">
            Теперь мы помогаем студентам с поступлением через одноразовые консультации от проверенных экспертов с реальным опытом поступления.
          </p>
        </div>

        {/* Общие вопросы */}
        <div className="mb-8 sm:mb-12">
          <h2 className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6 flex items-center">
            <MessageCircle className="h-5 w-5 sm:h-6 sm:w-6 mr-2 text-primary" />
            Общие вопросы
          </h2>
          {generalFAQ.map((item, index) => (
            <FAQItem
              key={index}
              question={item.question}
              answer={item.answer}
              isOpen={openItems.has(index)}
              onToggle={() => toggleItem(index)}
            />
          ))}
        </div>

        {/* Вопросы студентов */}
        <div className="mb-8 sm:mb-12">
          <h2 className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6 flex items-center">
            <MessageCircle className="h-5 w-5 sm:h-6 sm:w-6 mr-2 text-blue-500" />
            Для студентов
          </h2>
          {studentFAQ.slice(4).map((item, index) => (
            <FAQItem
              key={index + 4}
              question={item.question}
              answer={item.answer}
              isOpen={openItems.has(index + 4)}
              onToggle={() => toggleItem(index + 4)}
            />
          ))}
        </div>

        {/* Вопросы менторов */}
        <div className="mb-8 sm:mb-12">
          <h2 className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6 flex items-center">
            <MessageCircle className="h-5 w-5 sm:h-6 sm:w-6 mr-2 text-green-500" />
            Для менторов
          </h2>
          {mentorFAQ.map((item, index) => (
            <FAQItem
              key={index + 8}
              question={item.question}
              answer={item.answer}
              isOpen={openItems.has(index + 8)}
              onToggle={() => toggleItem(index + 8)}
            />
          ))}
        </div>

        {/* Не нашли ответ */}
        <Card className="bg-gradient-to-r from-primary/5 to-primary/10">
          <CardContent className="p-8 text-center">
            <Mail className="h-12 w-12 text-primary mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-4">Не нашли ответ на свой вопрос?</h3>
            <p className="text-muted-foreground mb-6">
              Свяжитесь с нашей службой поддержки, и мы поможем вам в течение 24 часов
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild>
                <a href="mailto:support@masterconnect.com">
                  <Mail className="h-4 w-4 mr-2" />
                  Написать в поддержку
                </a>
              </Button>
              <Button variant="outline" asChild>
                <Link to="/mentors">
                  Найти ментора
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Быстрые действия */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardContent className="p-6 text-center">
              <h4 className="font-semibold mb-2">Новый пользователь?</h4>
              <p className="text-sm text-muted-foreground mb-4">
                Зарегистрируйтесь и начните поиск подходящего ментора
              </p>
              <Button asChild size="sm">
                <Link to="/auth/register">Зарегистрироваться</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
        </div>
      </div>
    </>
  )
}







