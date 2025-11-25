import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense } from 'react'

import { PublicLayout } from '@/shared/layouts/PublicLayout'
import { PrivateLayout } from '@/shared/layouts/PrivateLayout'
import { AdminLayout } from '@/shared/layouts/AdminLayout'

import { HomePage } from '@/pages/home/HomePage'
import { AboutPage } from '@/pages/about/AboutPage'
import { FAQPage } from '@/pages/public/FAQPage'
import { MentorsPage } from '@/pages/mentors/MentorsPage'
import { MentorDetailPage } from '@/pages/mentors/MentorDetailPage'
import { LoginPage } from '@/pages/auth/LoginPage'
import { RegisterPage } from '@/pages/auth/RegisterPage'
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage'
import { ResetPasswordPage } from '@/pages/auth/ResetPasswordPage'

import { StudentDashboardPage } from '@/pages/student/StudentDashboardPage'
import { StudentBookingsPage } from '@/pages/student/StudentBookingsPage'
import { StudentReviewsPage } from '@/pages/student/StudentReviewsPage'
import { BookConsultationPage } from '@/pages/student/BookConsultationPage'
import { BookingDetailPage } from '@/pages/bookings/BookingDetailPage'
import { StudentProfilePage } from '@/pages/student/StudentProfilePage'
import { ChatPage } from '@/pages/chat/ChatPage'

import { MentorDashboardPage } from '@/pages/mentor/MentorDashboardPage'
import { MentorBookingsPage } from '@/pages/mentor/MentorBookingsPage'
import { MentorProfilePage } from '@/pages/mentor/MentorProfilePage'
import { MentorAvailabilityPage } from '@/pages/mentor/MentorAvailabilityPage'

import { AdminDashboardPage } from '@/pages/admin/AdminDashboardPage'
import { AdminUsersPage } from '@/pages/admin/AdminUsersPage'
import { AdminMentorsPage } from '@/pages/admin/AdminMentorsPage'
import { AdminBookingsPage } from '@/pages/admin/AdminBookingsPage'
import { AdminAnalyticsPage } from '@/pages/admin/AdminAnalyticsPage'

import { SupportPage } from '@/pages/support/SupportPage'

import { PageLoader } from '@/shared/ui/PageLoader'
import { NotFoundPage } from '@/pages/errors/NotFoundPage'

import { ProtectedRoute } from './ProtectedRoute'

export const AppRouter = () => {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Публичные маршруты */}
        <Route path="/" element={<PublicLayout />}>
          <Route index element={<HomePage />} />
          <Route path="about" element={<AboutPage />} />
          <Route path="faq" element={<FAQPage />} />
          <Route path="mentors" element={<MentorsPage />} />
          <Route path="mentors/:id" element={<MentorDetailPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="forgot-password" element={<ForgotPasswordPage />} />
          <Route path="reset-password" element={<ResetPasswordPage />} />
        </Route>
        {/* Приватные маршруты для студентов */}
        <Route
          path="/student/*"
          element={
            <ProtectedRoute roles={['student']}>
              <PrivateLayout />
            </ProtectedRoute>
          }
        >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<StudentDashboardPage />} />
        <Route path="mentors" element={<MentorsPage />} />
        <Route path="mentors/:id" element={<MentorDetailPage />} />
        <Route path="bookings" element={<StudentBookingsPage />} />
        <Route path="bookings/:bookingId" element={<BookingDetailPage />} />
        <Route path="reviews" element={<StudentReviewsPage />} />
        <Route path="book-consultation/:mentorId" element={<BookConsultationPage />} />
        <Route path="profile" element={<StudentProfilePage />} />
        <Route path="support" element={<SupportPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="chat/:dialogId" element={<ChatPage />} />
        </Route>

        {/* Приватные маршруты для менторов */}
        <Route
          path="/mentor/*"
          element={
            <ProtectedRoute roles={['mentor']}>
              <PrivateLayout />
            </ProtectedRoute>
          }
        >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<MentorDashboardPage />} />
        <Route path="bookings" element={<MentorBookingsPage />} />
        <Route path="bookings/:bookingId" element={<BookingDetailPage />} />
        <Route path="profile" element={<MentorProfilePage />} />
          <Route path="availability" element={<MentorAvailabilityPage />} />
        <Route path="support" element={<SupportPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="chat/:dialogId" element={<ChatPage />} />
        </Route>

        {/* Административные маршруты */}
        <Route
          path="/admin/*"
          element={
            <ProtectedRoute roles={['admin']}>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<AdminDashboardPage />} />
          <Route path="users" element={<AdminUsersPage />} />
          <Route path="mentors" element={<AdminMentorsPage />} />
          <Route path="bookings" element={<AdminBookingsPage />} />
          <Route path="bookings/:bookingId" element={<BookingDetailPage />} />
          <Route path="analytics" element={<AdminAnalyticsPage />} />
          <Route path="support" element={<SupportPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="chat/:dialogId" element={<ChatPage />} />
        </Route>

        {/* 404 страница */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  )
}
