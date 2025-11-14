import { Outlet } from 'react-router-dom';
import { AnimatedOrbs } from '../background/AnimatedOrbs';
import { GridPattern } from '../background/GridPattern';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import './MainLayout.css';

export const MainLayout = () => {
  return (
    <div className="app">
      <AnimatedOrbs />
      <GridPattern />
      <Navbar />
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
