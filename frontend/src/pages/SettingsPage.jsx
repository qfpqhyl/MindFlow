import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Divider,
  Avatar,
  IconButton,
} from '@mui/material';
import { Edit as EditIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const SettingsPage = () => {
  const { user, updateUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
  });
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
      });
    }
  }, [user]);

  const handleUpdateProfile = async () => {
    const result = await updateUser(formData);
    if (result.success) {
      setMessage('个人信息已更新');
      setEditing(false);
    } else {
      setMessage(result.error);
    }
    setTimeout(() => setMessage(''), 3000);
  };

  const handleChangePassword = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage('新密码不匹配');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    // TODO: Implement password change API call
    setMessage('密码修改功能待实现');
    setTimeout(() => setMessage(''), 3000);
  };

  if (!user) return null;

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>
        设置
      </Typography>

      {/* Profile Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar
              sx={{ width: 80, height: 80, mr: 3, bgcolor: 'primary.main', fontSize: '2rem' }}
            >
              {user.username?.charAt(0).toUpperCase()}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6">{user.username}</Typography>
              <Typography variant="body2" color="text.secondary">{user.email}</Typography>
            </Box>
            {!editing && (
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={() => setEditing(true)}
              >
                编辑
              </Button>
            )}
          </Box>

          {editing ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                fullWidth
                label="用户名"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              />
              <TextField
                fullWidth
                label="邮箱"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                <Button onClick={() => { setEditing(false); setFormData({ username: user.username, email: user.email }); }}>
                  取消
                </Button>
                <Button variant="contained" onClick={handleUpdateProfile}>
                  保存
                </Button>
              </Box>
            </Box>
          ) : (
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
              <Box>
                <Typography variant="caption" color="text.secondary">用户 ID</Typography>
                <Typography variant="body2">{user.user_id}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">注册时间</Typography>
                <Typography variant="body2">
                  {new Date(user.created_at).toLocaleDateString('zh-CN')}
                </Typography>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Email Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            邮件设置
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2, mb: 2 }}>
            <Box>
              <Typography variant="caption" color="text.secondary">默认邮箱</Typography>
              <Typography variant="body2">
                {user.settings?.default_email || '未设置'}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">邮件提醒</Typography>
              <Typography variant="body2">
                {user.settings?.reminder_enabled ? '已启用' : '已禁用'}
              </Typography>
            </Box>
          </Box>
          <Button variant="outlined" disabled>
            修改邮件设置（待实现）
          </Button>
        </CardContent>
      </Card>

      {/* Change Password */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            修改密码
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 400 }}>
            <TextField
              fullWidth
              label="当前密码"
              type="password"
              value={passwordData.old_password}
              onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })}
            />
            <TextField
              fullWidth
              label="新密码"
              type="password"
              value={passwordData.new_password}
              onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
            />
            <TextField
              fullWidth
              label="确认新密码"
              type="password"
              value={passwordData.confirm_password}
              onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
            />
            <Button
              variant="contained"
              onClick={handleChangePassword}
              sx={{ alignSelf: 'flex-start' }}
            >
              修改密码
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* AI Settings */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            AI 模型设置
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
            <Box>
              <Typography variant="caption" color="text.secondary">默认模型</Typography>
              <Typography variant="body2">
                {user.settings?.default_model_id || 'meta/llama-3.1-405b-instruct'}
              </Typography>
            </Box>
          </Box>
          <Button variant="outlined" sx={{ mt: 2 }} disabled>
            更改模型（待实现）
          </Button>
        </CardContent>
      </Card>

      {/* Message */}
      {message && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color={message.includes('成功') ? 'success.main' : 'error.main'}>
            {message}
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default SettingsPage;
