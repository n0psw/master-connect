import { Link } from 'react-router-dom'
import { Instagram } from 'lucide-react'

export const PublicFooter = () => {
  return (
    <footer className="border-t bg-background">
      <div className="container-wide flex flex-col items-center justify-between gap-4 py-6 text-sm text-muted-foreground md:flex-row">
        <div className="flex items-center gap-3">
          <img
            src="/masteredlogo-ico.ico"
            alt="MasterConnect"
            className="h-8 w-8 rounded-full shadow-sm"
          />
          <span className="font-medium">MasterConnect</span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="https://www.instagram.com/master.education/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 hover:text-primary transition-colors"
            aria-label="Instagram"
          >
            <Instagram className="h-5 w-5" />
            <span className="hidden sm:inline">Instagram</span>
          </a>
          <span className="hidden h-1 w-1 rounded-full bg-muted md:inline-block" />
          <span>© {new Date().getFullYear()}</span>
          <span className="hidden h-1 w-1 rounded-full bg-muted md:inline-block" />
          <Link to="/about" className="hover:text-primary transition-colors">
            О платформе
          </Link>
          <Link to="/faq" className="hover:text-primary transition-colors">
            FAQ
          </Link>
        </div>
      </div>
    </footer>
  )
}
