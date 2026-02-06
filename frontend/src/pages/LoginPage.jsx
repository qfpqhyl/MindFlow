import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Card,
  FormControlLabel,
  Checkbox,
  Link,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setError('');
    setFormData({ username: '', email: '', password: '', confirmPassword: '' });
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.username, formData.password);

    if (result.success) {
      navigate('/conversations');
    } else {
      setError(result.error);
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('密码不匹配');
      setLoading(false);
      return;
    }

    const result = await register(formData.username, formData.email, formData.password);

    if (result.success) {
      navigate('/conversations');
    } else {
      setError(result.error);
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#FAFAFA',
      }}
    >
      <Container maxWidth="sm">
        <Box sx={{ mb: 8, textAlign: 'center' }}>
          <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
            MindFlow
          </Typography>
          <Typography variant="body1" color="text.secondary">
            智能工作流应用
          </Typography>
        </Box>

        <Card sx={{ p: 4, border: '1px solid #E0E0E0' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            sx={{ borderBottom: '1px solid #E0E0E0', mb: 3 }}
          >
            <Tab label="登录" />
            <Tab label="注册" />
          </Tabs>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          {/* Login Form */}
          {tabValue === 0 && (
            <Box component="form" onSubmit={handleLogin}>
              <TextField
                fullWidth
                label="用户名"
                name="username"
                value={formData.username}
                onChange={handleChange}
                margin="normal"
                required
                autoFocus
              />
              <TextField
                fullWidth
                label="密码"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                margin="normal"
                required
              />
              <FormControlLabel
                control={<Checkbox color="primary" />}
                label="记住我"
                sx={{ mt: 2, mb: 3 }}
              />
              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                sx={{ mb: 2 }}
              >
                {loading ? '登录中...' : '登录'}
              </Button>
            </Box>
          )}

          {/* Register Form */}
          {tabValue === 1 && (
            <Box component="form" onSubmit={handleRegister}>
              <TextField
                fullWidth
                label="用户名"
                name="username"
                value={formData.username}
                onChange={handleChange}
                margin="normal"
                required
                autoFocus
              />
              <TextField
                fullWidth
                label="邮箱"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                margin="normal"
                required
              />
              <TextField
                fullWidth
                label="密码"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                margin="normal"
                required
                helperText="至少 6 个字符"
              />
              <TextField
                fullWidth
                label="确认密码"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                margin="normal"
                required
              />
              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                sx={{ mt: 3, mb: 2 }}
              >
                {loading ? '注册中...' : '注册'}
              </Button>
            </Box>
          )}

          <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid #E0E0E0', textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              {tabValue === 0 ? "还没有账号？ " : "已有账号？ "}
              <Link
                component="button"
                variant="caption"
                onClick={() => setTabValue(tabValue === 0 ? 1 : 0)}
                sx={{ fontWeight: 600 }}
              >
                {tabValue === 0 ? '立即注册' : '立即登录'}
              </Link>
            </Typography>
          </Box>
        </Card>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="caption" color="text.disabled">
            © 2025 MindFlow. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default LoginPage;
