import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
} from '@mui/material';
import GitHubIcon from '@mui/icons-material/GitHub';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { loginWithGithub } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Handle GitHub OAuth callback
  useEffect(() => {
    const token = searchParams.get('token');
    const username = searchParams.get('username');

    if (token && username) {
      // Store token and user info
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify({ user_id: 'me', username }));

      // Navigate to conversations
      navigate('/conversations', { replace: true });
    }
  }, [searchParams, navigate]);

  const handleGithubLogin = () => {
    setLoading(true);
    setError('');

    // Redirect to backend GitHub OAuth endpoint
    const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    window.location.href = `${backendUrl}/auth/github/login`;
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
          <Box
            component="img"
            src="/logo.svg"
            alt="MindFlow Logo"
            sx={{
              height: 60,
              width: 'auto',
              mb: 2,
            }}
          />
          <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
            MindFlow
          </Typography>
          <Typography variant="body1" color="text.secondary">
            思流如潮 - 智能工作流管理
          </Typography>
        </Box>

        <Card sx={{ p: 6, border: '1px solid #E0E0E0', textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
            欢迎使用 MindFlow
          </Typography>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
            使用 GitHub 账号登录，开始您的智能工作流之旅
          </Typography>

          {error && (
            <Box sx={{ mb: 3, p: 2, bgcolor: 'error.light', borderRadius: 1, color: 'error.dark' }}>
              <Typography variant="body2">{error}</Typography>
            </Box>
          )}

          <Button
            fullWidth
            variant="contained"
            size="large"
            startIcon={<GitHubIcon />}
            onClick={handleGithubLogin}
            disabled={loading}
            sx={{
              mb: 2,
              py: 1.5,
              fontSize: '1.1rem',
              backgroundColor: '#24292e',
              '&:hover': {
                backgroundColor: '#24292e',
                opacity: 0.9,
              },
            }}
          >
            {loading ? '登录中...' : '使用 GitHub 登录'}
          </Button>

          <Typography variant="caption" color="text.secondary" sx={{ mt: 3 }}>
            登录即表示您同意我们的服务条款和隐私政策
          </Typography>
        </Card>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            MindFlow 功能亮点
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: 'center', mt: 2 }}>
            <Box sx={{ flex: '1 1 150px', p: 2, bgcolor: 'white', border: '1px solid #E0E0E0' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                💬 AI 对话
              </Typography>
              <Typography variant="caption" color="text.secondary">
                智能助手，随时待命
              </Typography>
            </Box>
            <Box sx={{ flex: '1 1 150px', p: 2, bgcolor: 'white', border: '1px solid #E0E0E0' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                📄 文档管理
              </Typography>
              <Typography variant="caption" color="text.secondary">
                知识沉淀，轻松整理
              </Typography>
            </Box>
            <Box sx={{ flex: '1 1 150px', p: 2, bgcolor: 'white', border: '1px solid #E0E0E0' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                ✅ 任务提醒
              </Typography>
              <Typography variant="caption" color="text.secondary">
                邮件提醒，永不错过
              </Typography>
            </Box>
          </Box>
        </Box>

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
