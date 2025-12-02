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
      answer: "MasterConnect — это платформа, которая соединяет амбициозных студентов с успешными выпускниками топовых университетов мира. Наши менторы помогают студентам с поступлением, выбором специальности, подготовкой документов и планированием карьеры."
    },
    {
      question: "Кто может стать ментором?",
      answer: "Ментором может стать выпускник или текущий студент топового университета (MIT, Harvard, Stanford, Oxford, Cambridge и др.) с успешным опытом поступления и готовностью помочь другим. Все менторы проходят процесс верификации."
    },
    {
      question: "Как проходят консультации?",
      answer: "Консультации проходят в формате видео-звонков через нашу платформу. Длительность может быть 30, 45 или 60 минут в зависимости от ваших потребностей. Перед консультацией вы заполняете анкету с вопросами, чтобы ментор мог лучше подготовиться."
    },
    {
      question: "Сколько стоят консультации?",
      answer: "Стоимость консультаций устанавливается каждым ментором индивидуально и зависит от его опыта и специализации. В среднем цены варьируются от $30 до $150 за консультацию. Вы видите точную стоимость перед бронированием."
    },
    {
      question: "Как я могу быть уверен в качестве менторов?",
      answer: "Все наши менторы проходят тщательную проверку — мы верифицируем их образование, достижения и опыт. Также у каждого ментора есть рейтинг и отзывы от предыдущих студентов, которые помогут вам сделать выбор."
    },
    {
      question: "Можно ли отменить или перенести консультацию?",
      answer: "Да, вы можете отменить или перенести консультацию не менее чем за 24 часа до назначенного времени. В случае отмены деньги будут возвращены на ваш счет. Менторы также могут инициировать перенос в случае непредвиденных обстоятельств."
    },
    {
      question: "В каких часовых поясах работают менторы?",
      answer: "Наши менторы находятся по всему миру, поэтому вы можете найти подходящее время независимо от вашего местоположения. Каждый ментор указывает свой часовой пояс и доступные часы."
    },
    {
      question: "Какие способы оплаты принимаются?",
      answer: "Мы принимаем основные банковские карты (Visa, MasterCard), PayPal и другие популярные способы оплаты. Оплата производится через защищенную систему, и ваши данные полностью конфиденциальны."
    },
    {
      question: "Что если я не удовлетворен консультацией?",
      answer: "Мы гарантируем качество наших услуг. Если вы не удовлетворены консультацией, свяжитесь с нашей службой поддержки в течение 48 часов, и мы рассмотрим возможность возврата средств или предоставления бесплатной повторной консультации."
    },
    {
      question: "Как стать ментором на платформе?",
      answer: "Для регистрации в качестве ментора зарегистрируйтесь на платформе, выберите роль 'Ментор' и заполните подробную анкету с информацией об образовании, достижениях и опыте. После проверки документов вы сможете начать консультировать студентов."
    },
    {
      question: "Могу ли я получить консультацию на родном языке?",
      answer: "Многие наши менторы владеют несколькими языками, включая русский, английский, казахский и другие. При поиске ментора вы можете фильтровать результаты по языку консультаций."
    },
    {
      question: "Есть ли групповые консультации?",
      answer: "В настоящее время мы фокусируемся на персональных консультациях 1-на-1, которые обеспечивают максимальную эффективность и индивидуальный подход. Групповые сессии планируются в будущих обновлениях платформы."
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
          content="Ответы на часто задаваемые вопросы о платформе MasterConnect. Узнайте как работают консультации с менторами и как стать ментором."
        />
      </Helmet>

      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Заголовок */}
        <div className="text-center mb-12">
          <HelpCircle className="h-16 w-16 text-primary mx-auto mb-6" />
          <h1 className="text-4xl font-bold mb-4">Часто задаваемые вопросы</h1>
          <p className="text-xl text-muted-foreground">
            Найдите ответы на популярные вопросы о работе с платформой
          </p>
        </div>

        {/* Общие вопросы */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            <MessageCircle className="h-6 w-6 mr-2 text-primary" />
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
        <div className="mb-12">
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            <MessageCircle className="h-6 w-6 mr-2 text-blue-500" />
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
        <div className="mb-12">
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            <MessageCircle className="h-6 w-6 mr-2 text-green-500" />
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
    </>
  )
}








