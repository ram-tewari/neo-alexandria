// Animation configuration types

export interface AnimationVariant {
  hidden?: any;
  visible?: any;
  rest?: any;
  hover?: any;
  tap?: any;
  focus?: any;
  initial?: any;
  animate?: any;
  exit?: any;
}

export interface StaggerConfig {
  staggerChildren: number;
  delayChildren?: number;
}

export interface TransitionConfig {
  duration: number;
  ease: string | number[];
  delay?: number;
  repeat?: number;
}
