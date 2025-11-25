import { Link } from 'react-router-dom'
import { Mail, Phone, MapPin } from 'lucide-react'

export const PublicFooter = () => {
  return (
    <footer className="border-t bg-background">
      <div className="container-wide py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* О компании */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                <span className="text-sm font-bold">MC</span>
              </div>
              <span className="text-lg font-semibold">MasterConnect</span>
            </div>
            
            <p className="text-sm text-muted-foreground">
              Платформа для онлайн консультаций с опытными менторами по поступлению в университеты.
            </p>
            
            <div className="space-y-2 text-sm text-muted-foreground">
              <div className="flex items-center space-x-2">
                <Mail className="h-4 w-4" />
                <span>support@masterconnect.kz</span>
              </div>
              <div className="flex items-center space-x-2">
                <Phone className="h-4 w-4" />
                <span>+7 (777) 123-45-67</span>
              </div>
              <div className="flex items-center space-x-2">
                <MapPin className="h-4 w-4" />
                <span>Алматы, Казахстан</span>
              </div>
            </div>
          </div>

          {/* Для студентов */}
          <div className="space-y-4">
            <h3 className="font-semibold">Для студентов</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link to="/mentors" className="hover:text-primary transition-colors">
                  Найти ментора
                </Link>
              </li>
              <li>
                <Link to="/how-it-works" className="hover:text-primary transition-colors">
                  Как это работает
                </Link>
              </li>
              <li>
                <Link to="/prices" className="hover:text-primary transition-colors">
                  Цены
                </Link>
              </li>
              <li>
                <Link to="/register" className="hover:text-primary transition-colors">
                  Регистрация
                </Link>
              </li>
            </ul>
          </div>

          {/* Для менторов */}
          <div className="space-y-4">
            <h3 className="font-semibold">Для менторов</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link to="/become-mentor" className="hover:text-primary transition-colors">
                  Стать ментором
                </Link>
              </li>
              <li>
                <Link to="/mentor-guide" className="hover:text-primary transition-colors">
                  Руководство
                </Link>
              </li>
              <li>
                <Link to="/mentor-requirements" className="hover:text-primary transition-colors">
                  Требования
                </Link>
              </li>
              <li>
                <Link to="/mentor-earnings" className="hover:text-primary transition-colors">
                  Заработок
                </Link>
              </li>
            </ul>
          </div>

          {/* Поддержка */}
          <div className="space-y-4">
            <h3 className="font-semibold">Поддержка</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link to="/help" className="hover:text-primary transition-colors">
                  Центр помощи
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-primary transition-colors">
                  Связаться с нами
                </Link>
              </li>
              <li>
                <Link to="/faq" className="hover:text-primary transition-colors">
                  FAQ
                </Link>
              </li>
              <li>
                <Link to="/feedback" className="hover:text-primary transition-colors">
                  Обратная связь
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Нижняя часть */}
        <div className="border-t mt-8 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-muted-foreground">
          <div className="flex items-center space-x-6">
            <p>&copy; 2024 MasterConnect. Все права защищены.</p>
            <Link to="/privacy" className="hover:text-primary transition-colors">
              Конфиденциальность
            </Link>
            <Link to="/terms" className="hover:text-primary transition-colors">
              Условия использования
            </Link>
          </div>
          
          <div className="mt-4 md:mt-0">
            <p>Сделано с ❤️ в Казахстане</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
