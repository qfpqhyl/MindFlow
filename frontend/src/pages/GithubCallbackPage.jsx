import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Box, CircularProgress, Typography, Container, Alert } from '@mui/material';
import { usersAPI } from '../services/api';

const GithubCallbackPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleGithubCallback = async () => {
      const token = searchParams.get('token');
      const username = searchParams.get('username');

      if (!token) {
        setError('未获取到授权令牌');
        setTimeout(() => {
          navigate('/login', { replace: true });
        }, 2000);
        return;
      }

      try {
        // Store token
        localStorage.setItem('token', token);

        // Fetch complete user data from API
        const response = await usersAPI.getMe();
        const userData = response.data.data;

        // Store complete user data
        localStorage.setItem('user', JSON.stringify(userData));

        // Navigate to conversations after short delay
        setTimeout(() => {
          navigate('/conversations', { replace: true });
        }, 500);
      } catch (err) {
        console.error('Failed to fetch user data:', err);
        setError('获取用户信息失败，请重试');
        setTimeout(() => {
          navigate('/login', { replace: true });
        }, 2000);
      }
    };

    handleGithubCallback();
  }, [searchParams, navigate]);

  if (error) {
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
        <Container maxWidth="sm" sx={{ textAlign: 'center' }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        </Container>
      </Box>
    );
  }

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
      <Container maxWidth="sm" sx={{ textAlign: 'center' }}>
        <CircularProgress sx={{ mb: 4 }} />
        <Typography variant="h6" gutterBottom>
          正在登录...
        </Typography>
        <Typography variant="body2" color="text.secondary">
          请稍候，我们正在为您设置账户
        </Typography>
      </Container>
    </Box>
  );
};

export default GithubCallbackPage;
