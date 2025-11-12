# MedSynapse Frontend

React-based frontend for the Doctor's Intelligent Assistant.

## Features

- Patient intake form
- Real-time SOAP report generation
- Similar case search
- Database statistics dashboard
- Professional, clean UI

## Tech Stack

- React 18
- Vite (build tool)
- Tailwind CSS (styling)
- React Router (navigation)
- Axios (API client)

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at: http://localhost:3000

### 3. Make sure Backend is Running

The frontend expects the FastAPI backend at `http://localhost:8000`

```bash
# In another terminal
cd backend
uvicorn main:app --reload --port 8000
```

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # API client
│   ├── components/
│   │   ├── ProcessingStatus.jsx
│   │   └── SOAPReportViewer.jsx
│   ├── pages/
│   │   ├── PatientIntake.jsx  # Main intake form
│   │   ├── SearchCases.jsx    # Search functionality
│   │   └── DatabaseStats.jsx  # Statistics dashboard
│   ├── App.jsx                # Main app with routing
│   ├── main.jsx               # Entry point
│   └── index.css              # Tailwind CSS
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## API Integration

The frontend communicates with the FastAPI backend via:

- `POST /intake` - Process patient intake
- `GET /patient/{id}/history` - Get patient history

API client is configured in `src/api/client.js`

## Building for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Environment Variables

Create `.env` file in frontend directory:

```
VITE_API_URL=http://localhost:8000
```

## Notes

- All emojis removed for professional appearance
- Uses Tailwind CSS utility classes
- Responsive design for mobile/tablet/desktop
- Clean, clinical UI suitable for healthcare
