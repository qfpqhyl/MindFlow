import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChatBubbleOutline,
  Description,
  TaskAlt,
  Settings,
  Logout,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const DRAWER_WIDTH = 280;

const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const menuItems = [
    { text: '对话', icon: <ChatBubbleOutline />, path: '/conversations' },
    { text: '文档', icon: <Description />, path: '/documents' },
    { text: '任务', icon: <TaskAlt />, path: '/tasks' },
    { text: '设置', icon: <Settings />, path: '/settings' },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path) => {
    navigate(path);
    setMobileOpen(false);
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ borderBottom: '1px solid #E0E0E0' }}>
        <Typography variant="h6" component="div" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          MindFlow
        </Typography>
      </Toolbar>

      <List sx={{ flex: 1, py: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              selected={location.pathname === item.path}
              sx={{
                borderRadius: 0,
                mx: 2,
                '&.Mui-selected': {
                  backgroundColor: 'rgba(0,0,0,0.04)',
                  borderLeft: '3px solid #000',
                },
              }}
            >
              <ListItemIcon sx={{ color: 'inherit' }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />
      <List sx={{ py: 2 }}>
        <ListItem disablePadding sx={{ mb: 0.5 }}>
          <ListItemButton
            onClick={logout}
            sx={{ mx: 2 }}
          >
            <ListItemIcon sx={{ color: 'inherit' }}>
              <Logout />
            </ListItemIcon>
            <ListItemText primary="退出登录" />
          </ListItemButton>
        </ListItem>
      </List>

      <Box sx={{ p: 3, borderTop: '1px solid #E0E0E0' }}>
        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
          {user?.username}
        </Typography>
        <Typography variant="caption" color="text.disabled" sx={{ fontSize: '0.7rem' }}>
          {user?.email}
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { sm: `${DRAWER_WIDTH}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            {menuItems.find(item => location.pathname.includes(item.path.replace('/', '')))?.text || 'MindFlow'}
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          height: '100vh',
          overflow: 'auto',
          backgroundColor: '#FAFAFA',
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;
