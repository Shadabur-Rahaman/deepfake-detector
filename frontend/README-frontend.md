# iFake - Advanced Deepfake Detection Frontend

A cutting-edge React application built with modern web technologies for detecting deepfakes with industry-leading accuracy.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🛠 Technology Stack

- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS with custom design system
- **Components**: shadcn/ui (customized)
- **Animations**: Framer Motion
- **3D Graphics**: React Three Fiber + Drei
- **State Management**: React Query (TanStack)
- **Theme Management**: Custom theme provider with 4 themes
- **Icons**: Lucide React
- **TypeScript**: Full type safety

## 🎨 Design System

iFake uses a sophisticated design system with multiple themes:

### Themes Available
- **Deep Space** (default): Dark theme with electric blue accents
- **Clean**: Light professional theme
- **Neon**: High-contrast cyberpunk aesthetic  
- **Minimal**: Clean monochrome design

### Color Tokens
All colors are defined as HSL semantic tokens in `src/index.css`:
- Primary: Deep blue (#4f46e5)
- Accent: Electric cyan (#22d3ee)  
- AI Core: Purple (#a855f7)
- AI Neural: Magenta (#ec4899)
- AI Data: Teal (#14b8a6)

### Typography
- **Primary Font**: Inter (clean, modern)
- **Monospace**: JetBrains Mono (code/technical content)

## 🏗 Project Structure

```
src/
├── components/
│   ├── ui/              # shadcn/ui components
│   ├── theme/           # Theme management
│   ├── three/           # 3D components
│   └── *.tsx            # Feature components
├── lib/
│   ├── theme.ts         # Theme utilities
│   └── utils.ts         # General utilities
├── pages/               # Route components
└── hooks/               # Custom React hooks
```

## 🎯 Current Features (Phase 1)

- ✅ Modern responsive design system
- ✅ Multi-theme support (4 themes)
- ✅ 3D neural network hero animation
- ✅ Animated performance metrics
- ✅ "How iFake Thinks" explanation
- ✅ Smooth page transitions
- ✅ Mobile-first responsive design

## 🔧 Development

### Adding New Themes
1. Add theme colors to `src/index.css`
2. Update `src/lib/theme.ts` theme arrays
3. Add icon mapping in `ThemeToggle.tsx`

### Customizing Components
All shadcn components can be customized in `src/components/ui/`. 
Always use design system tokens instead of hardcoded colors.

### Performance
- 3D scene is optimized with performance limits
- Lazy loading for heavy components
- Automatic WebGL fallbacks

## 🌟 Design Choices & Creative Decisions

**Color Palette**: Deep space blues with electric accents convey both trustworthiness (blue) and cutting-edge technology (electric cyan/purple).

**3D Hero**: Neural network particle system reinforces AI technology theme while remaining performant.

**Typography**: Inter provides excellent readability across devices, while JetBrains Mono ensures technical content is clear.

**Animations**: Subtle, purposeful micro-interactions enhance UX without being distracting.

**Layout**: Clean, spacious design builds trust while geometric elements suggest precision.

## 🔮 Next Steps

Continue with Phase 2 to add:
- Additional pages (Features, Try It, Detection, etc.)
- Authentication UI  
- API documentation
- Blog aggregator
- Real-time detection interface

## 📝 Environment Variables

Currently no environment variables required for Phase 1.
Future phases will add:
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_WS_URL` 
- `NEXT_PUBLIC_BLOG_API`

---

Built with ❤️ using modern web technologies for the future of digital trust.