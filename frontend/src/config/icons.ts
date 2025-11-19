import {
  LayoutDashboard,
  Library,
  Network,
  Search,
  Heart,
  Clock,
  Bookmark,
  Bell,
  Plus,
  Filter,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Star,
  BookOpen,
  Video,
  FileText,
  GraduationCap,
  User,
  Menu,
  Brain,
  BarChart3,
  Users,
  TrendingUp,
  X,
  Check,
  Archive,
  Edit,
  Share2,
  Grid,
  List,
  Columns,
  LayoutGrid,
  Home,
  Activity,
  Folder,
  Compass,
  StickyNote,
  CheckSquare,
  Highlighter,
  Tag,
  Download,
  Upload,
  FolderHeart,
  BarChart2,
  Lightbulb,
  PieChart,
  Settings,
  Palette,
  HelpCircle,
  MessageSquare,
  Info
} from 'lucide-react';

export const icons = {
  // Navigation - Main
  home: Home,
  dashboard: LayoutDashboard,
  library: Library,
  graph: Network,
  search: Search,
  activity: Activity,
  workspaces: Folder,
  discover: Compass,
  
  // Tools
  notes: StickyNote,
  tasks: CheckSquare,
  highlights: Highlighter,
  tags: Tag,
  import: Download,
  export: Upload,
  
  // Collections
  favorites: Heart,
  recent: Clock,
  clock: Clock,
  readLater: Bookmark,
  playlists: FolderHeart,
  archived: Archive,
  shared: Users,
  
  // Insights
  statistics: BarChart2,
  trends: TrendingUp,
  recommendations: Lightbulb,
  breakdown: PieChart,
  
  // System
  settings: Settings,
  profile: User,
  themes: Palette,
  help: HelpCircle,
  feedback: MessageSquare,
  about: Info,
  
  // Actions
  notification: Bell,
  add: Plus,
  filter: Filter,
  sort: ArrowUpDown,
  prevPage: ChevronLeft,
  nextPage: ChevronRight,
  chevronDown: ChevronDown,
  chevronLeft: ChevronLeft,
  chevronRight: ChevronRight,
  menu: Menu,
  close: X,
  check: Check,
  edit: Edit,
  share: Share2,
  archive: Archive,
  
  // View modes
  grid: Grid,
  list: List,
  columns: Columns,
  masonry: LayoutGrid,
  
  // Content types
  star: Star,
  article: FileText,
  video: Video,
  book: BookOpen,
  paper: GraduationCap,
  
  // Stats
  chart: BarChart3,
  trending: TrendingUp,
  
  // User
  user: User,
  brain: Brain,
} as const;

export type IconName = keyof typeof icons;
