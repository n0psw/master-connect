-- Создание таблицы mentor_settings вручную
CREATE TABLE IF NOT EXISTS mentor_settings (
    mentor_id UUID NOT NULL PRIMARY KEY,
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    buffer_time_minutes INTEGER NOT NULL DEFAULT 15,
    max_bookings_per_day INTEGER NOT NULL DEFAULT 8,
    advance_booking_days INTEGER NOT NULL DEFAULT 30,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mentor_settings_mentor FOREIGN KEY (mentor_id) REFERENCES mentors(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_mentor_settings_mentor_id ON mentor_settings(mentor_id);

