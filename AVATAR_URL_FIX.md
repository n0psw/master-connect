# ✅ Исправление URL аватарок и отображения

**Дата:** 2025-11-24 21:30 UTC  
**Проблема:** Аватарка загружается на сервер, но не отображается (пропадает после сохранения)

---

## Проблема

После нажатия "Сохранить":
1. ✅ Файл загружается на сервер (`/uploads/avatars/xxx.jpg`)
2. ✅ В базе данных сохраняется URL (`/uploads/avatars/xxx.jpg`)
3. ❌ Но аватарка **не отображается** - вместо нее placeholder
4. ❌ Нигде на сайте аватарки не видно

---

## Причины

### 1. Preview очищается раньше, чем обновляются данные
После загрузки `setPreview(null)` вызывался сразу, но `currentAvatarUrl` еще не содержал новый URL из API.

### 2. Неправильный URL изображений
Backend возвращает относительные пути: `/uploads/avatars/xxx.jpg`  
Frontend пытался загрузить: `http://localhost:3000/uploads/avatars/xxx.jpg` ❌  
Но файлы лежат на: `http://localhost:8000/uploads/avatars/xxx.jpg` ✅

### 3. Нет proxy для `/uploads`
Vite dev server не проксировал запросы к `/uploads` на backend.

---

## Решения

### 1. ✅ Добавлен state `uploadedUrl`

**Файл:** `apps/web/src/shared/components/AvatarUpload.tsx`

```typescript
const [uploadedUrl, setUploadedUrl] = useState<string | null>(null)

const uploadMutation = useMutation(
  (file: File) => profilesApi.uploadAvatar(file),
  {
    onSuccess: async (data) => {
      setUploadedUrl(data.avatar_url)  // ✅ Сохраняем URL локально
      toast.success('Аватар успешно загружен!')
      
      await Promise.all([...])  // Инвалидация кэша
      await queryClient.refetchQueries([...])  // Обновление данных
      
      setSelectedFile(null)
      setPreview(null)  // Очищаем preview, но у нас есть uploadedUrl
      
      onSuccess?.()
    }
  }
)

// Порядок важен: preview → uploadedUrl → currentAvatarUrl
const displayAvatar = preview || uploadedUrl || currentAvatarUrl
```

**Что это даёт:**
- После загрузки аватарка сохраняется в `uploadedUrl`
- Даже когда `preview` очищается, отображается `uploadedUrl`
- После обновления кэша подтягивается `currentAvatarUrl` из API

---

### 2. ✅ Добавлена функция `getImageUrl`

**Файл:** `apps/web/src/shared/components/AvatarUpload.tsx`

```typescript
const getImageUrl = (url: string | null) => {
  if (!url) return null
  if (url.startsWith('http')) return url
  if (url.startsWith('/uploads')) {
    return `http://localhost:8000${url}`  // ✅ Добавляем полный URL
  }
  return url
}

<img
  src={getImageUrl(displayAvatar) || ''}
  alt="Аватар"
  className="w-32 h-32 rounded-full object-cover border-2 border-border"
  onError={(e) => {
    console.error('Failed to load avatar:', displayAvatar)
    e.currentTarget.style.display = 'none'
  }}
/>
```

**Что это даёт:**
- Относительные пути (`/uploads/avatars/xxx.jpg`) преобразуются в полные
- Полные URL (`http://...`) остаются без изменений
- Добавлен `onError` для отладки

---

### 3. ✅ Добавлен proxy для `/uploads`

**Файл:** `apps/web/vite.config.ts`

**Было:**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

**Стало:**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
    '/uploads': {  // ✅ Добавлен proxy для статических файлов
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

**Что это даёт:**
- Запросы к `http://localhost:3000/uploads/...` проксируются на `http://localhost:8000/uploads/...`
- Изображения загружаются с правильного сервера

---

### 4. ✅ Обновлен `PrivateHeader`

**Файл:** `apps/web/src/shared/components/headers/PrivateHeader.tsx`

```typescript
const getImageUrl = (url: string | null | undefined) => {
  if (!url) return null
  if (url.startsWith('http')) return url
  if (url.startsWith('/uploads')) {
    return `http://localhost:8000${url}`
  }
  return url
}

{getImageUrl(avatarUrl) ? (
  <img
    src={getImageUrl(avatarUrl)!}
    alt={user?.name || 'Пользователь'}
    className="h-8 w-8 rounded-full object-cover border border-border"
    onError={(e) => {
      console.error('Failed to load avatar in header:', avatarUrl)
      e.currentTarget.style.display = 'none'
    }}
  />
) : (
  <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
    <User className="h-4 w-4 text-primary-foreground" />
  </div>
)}
```

---

## Как это работает

### Загрузка аватарки:

1. Пользователь выбирает файл → `preview` показывает Data URL
2. Нажимает "Сохранить" → файл отправляется на сервер
3. Сервер возвращает: `{ avatar_url: "/uploads/avatars/xxx.jpg" }`
4. `uploadedUrl` сохраняет этот URL локально
5. Кэш инвалидируется и обновляется
6. `preview` очищается, но отображается `uploadedUrl`
7. После обновления данных из API отображается `currentAvatarUrl`

### Отображение:
```typescript
displayAvatar = preview || uploadedUrl || currentAvatarUrl
               ↓        ↓             ↓
            Data URL  Server URL   API URL
```

### URL трансформация:
```
Backend:   /uploads/avatars/xxx.jpg
↓
getImageUrl():
↓
Frontend:  http://localhost:8000/uploads/avatars/xxx.jpg
```

---

## Что нужно сделать

### 1. Перезапустить frontend dev server (ВАЖНО!)
```bash
cd apps/web
npm run dev
```

**⚠️ ВАЖНО:** Vite config изменился, нужен перезапуск!

### 2. Перезапустить backend (если не запущен)
```bash
cd apps/api
python run_server.py
```

### 3. Обновить браузер
- Нажать `Ctrl+Shift+R` (жесткая перезагрузка)

### 4. Проверить:
1. Зайти в **Профиль**
2. Загрузить новую аватарку
3. Убедиться, что она **не пропадает** после сохранения
4. Проверить **хедер вверху** - аватарка должна появиться
5. Открыть консоль браузера (F12) - не должно быть ошибок 404

---

## Отладка

### Если аватарка все еще не загружается:

1. **Открыть консоль браузера (F12)**
   - Проверить Network → ищем запрос к `/uploads/avatars/xxx.jpg`
   - Статус должен быть `200 OK`, не `404 Not Found`

2. **Проверить console.error**
   - Если есть `Failed to load avatar:`, смотрим какой URL
   - Должен быть `http://localhost:8000/uploads/avatars/xxx.jpg`

3. **Проверить файл существует:**
   ```bash
   cd C:\Users\ultua\PycharmProjects\masterconnect
   dir uploads\avatars
   ```

4. **Проверить backend логи:**
   - Должен быть запрос `GET /uploads/avatars/xxx.jpg`
   - Статус `200`

5. **Проверить базу данных:**
   ```bash
   cd C:\Users\ultua\PycharmProjects\masterconnect
   python -c "import sqlite3; conn = sqlite3.connect('test.db'); cursor = conn.cursor(); cursor.execute('SELECT user_id, avatar_url FROM mentors WHERE avatar_url IS NOT NULL'); print(cursor.fetchall())"
   ```

---

## Итоговый чек-лист

✅ Добавлен `uploadedUrl` state в `AvatarUpload`  
✅ Добавлена функция `getImageUrl` для URL трансформации  
✅ Добавлен proxy для `/uploads` в `vite.config.ts`  
✅ Обновлен `PrivateHeader` с `getImageUrl`  
✅ Добавлены `onError` обработчики для отладки  
✅ Обновлен порядок fallback: `preview → uploadedUrl → currentAvatarUrl`

---

## 🎉 Теперь аватарки должны работать полностью!

**После перезапуска frontend dev server и обновления браузера:**
- ✅ Аватарка не пропадает после сохранения
- ✅ Отображается в профиле
- ✅ Отображается в хедере
- ✅ Отображается везде по сайту
- ✅ Правильные URL изображений
- ✅ Proxy работает корректно

**Если проблемы остались - проверьте отладку выше!** 🚀

