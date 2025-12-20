# AI Video Generator - Next.js Frontend

Modern, beautiful Next.js frontend for the AI Video Generator platform.

## 🚀 Features

- **Stunning UI**: Modern glassmorphism design with smooth animations
- **Responsive**: Works perfectly on desktop, tablet, and mobile
- **Fast**: Built with Next.js 14 and optimized for performance
- **Type-Safe**: Full TypeScript support
- **API Integration**: Ready to connect to Python backend

## 📦 Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🔧 Configuration

Create a `.env.local` file in the root directory:

```env
PYTHON_BACKEND_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
NEXT_PUBLIC_RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-secret
```

## 📁 Project Structure

```
web/
├── app/
│   ├── api/              # API routes
│   │   ├── auth/         # Authentication endpoints
│   │   └── generate/     # Video generation endpoint
│   ├── dashboard/        # Dashboard page
│   ├── pricing/          # Pricing page
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Landing page
│   └── globals.css       # Global styles
├── public/               # Static assets
└── package.json
```

## 🎨 Pages

- **/** - Landing page with hero, features, and CTA
- **/pricing** - Pricing tiers and FAQ
- **/dashboard** - Video generation interface
- **/videos** - User's video library (to be implemented)

## 🔌 API Routes

### POST /api/generate
Generate a new video

**Request:**
```json
{
  "topic": "Cyberpunk Tokyo at night",
  "style": "cinematic",
  "aspectRatio": "16:9",
  "numScenes": 5
}
```

**Response:**
```json
{
  "success": true,
  "jobId": "abc123",
  "message": "Video generation started"
}
```

### GET /api/generate?jobId=abc123
Check generation status

### POST /api/auth/login
User login

### POST /api/auth/signup
User registration

## 🛠️ Tech Stack

- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **Fonts**: Inter (Google Fonts)

## 🚀 Deployment

### Build for production
```bash
npm run build
npm start
```

### Deploy to Vercel
```bash
vercel deploy
```

## 🔗 Connecting to Python Backend

The Next.js app connects to your Python backend via API routes. Make sure your Python backend is running and accessible at the URL specified in `PYTHON_BACKEND_URL`.

### Python Backend Requirements

Your Python backend should expose these endpoints:

- `POST /api/generate` - Start video generation
- `GET /api/status/:jobId` - Check generation status
- `POST /api/auth/login` - User login
- `POST /api/auth/signup` - User registration

## 📝 TODO

- [ ] Implement authentication flow
- [ ] Add video library page
- [ ] Integrate Razorpay payment
- [ ] Add real-time progress updates (WebSocket)
- [ ] Implement video preview
- [ ] Add download functionality

## 🎯 Next Steps

1. Start your Python backend
2. Update `.env.local` with correct backend URL
3. Run `npm run dev`
4. Visit http://localhost:3000

Enjoy your new beautiful UI! 🎉
