import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Grid,
  Chip,
  IconButton,
  Skeleton,
} from '@mui/material';
import {
  Add,
  Search,
  Delete,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { conversationsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const ConversationsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const response = await conversationsAPI.getList();
      setConversations(response.data.data.items);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConversation = async () => {
    try {
      // Create conversation with default title "新对话"
      const response = await conversationsAPI.create({});
      const newConversationId = response.data.data.conversation_id;
      // Navigate to the new conversation
      navigate(`/conversations/${newConversationId}`);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleDeleteConversation = async (id, e) => {
    e.stopPropagation();
    if (window.confirm('确定要删除这个对话吗？')) {
      try {
        await conversationsAPI.delete(id);
        fetchConversations();
      } catch (error) {
        console.error('Failed to delete conversation:', error);
      }
    }
  };

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
          对话
        </Typography>
        <Grid container spacing={2}>
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={item}>
              <Skeleton variant="rectangular" height={200} />
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">对话</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreateConversation}
        >
          新建对话
        </Button>
      </Box>

      <TextField
        fullWidth
        placeholder="搜索对话..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        InputProps={{
          startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
        }}
        sx={{ mb: 4 }}
      />

      {filteredConversations.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 12 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchQuery ? '没有找到匹配的对话' : '还没有对话'}
          </Typography>
          <Typography variant="body2" color="text.disabled">
            {searchQuery ? '尝试其他关键词' : '点击"新建对话"开始使用 MindFlow'}
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={2}>
          {filteredConversations.map((conversation) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={conversation.conversation_id}>
              <Card
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                }}
                onClick={() => navigate(`/conversations/${conversation.conversation_id}`)}
              >
                <CardContent sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, pr: 2 }}>
                      {conversation.title}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={(e) => handleDeleteConversation(conversation.conversation_id, e)}
                      sx={{ position: 'absolute', top: 8, right: 8 }}
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </Box>

                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                    <Chip
                      label={`${conversation.message_count} 条消息`}
                      size="small"
                      variant="outlined"
                      sx={{ borderRadius: 0 }}
                    />
                  </Box>

                  <Typography variant="caption" color="text.secondary">
                    {new Date(conversation.updated_at).toLocaleString('zh-CN', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default ConversationsPage;
