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
  LayoutGrid
} from 'lucide-react';

export const icons = {
  // Navigation
  dashboard: LayoutDashboard,
  library: Library,
  graph: Network,
  search: Search,
  
  // Collections
  favorites: Heart,
  recent: Clock,
  clock: Clock,
  readLater: Bookmark,
  
  // Actions
  notification: Bell,
  add: Plus,
  filter: Filter,
  sort: ArrowUpDown,
  prevPage: ChevronLeft,
  nextPage: ChevronRight,
  chevronDown: ChevronDown,
  menu: Menu,
  close: X,
  check: Check,
  archive: Archive,
  edit: Edit,
  share: Share2,
  
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
  users: Users,
  trending: TrendingUp,
  
  // User
  user: User,
  brain: Brain,
} as const;

export type IconName = keyof typeof icons;
